import io
import json
import random
import struct
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
import PIL.ImageFile as _pil_imagefile
from PIL import Image, ImageDraw, ImageFont
from scipy.fft import fft2, fftshift, dctn

try:
    import rawpy
    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False

try:
    import tifffile
    TIFFFILE_AVAILABLE = True
except ImportError:
    TIFFFILE_AVAILABLE = False

app = FastAPI(title="Binary Image Destroyer")
import os as _os
_templates_dir = _os.environ.get("TEMPLATES_DIR", str(Path(__file__).parent / "templates"))
templates = Jinja2Templates(directory=_templates_dir)

sessions: Dict[str, dict] = {}
MAX_UNDO = 10
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

RAW_EXTS = {"CR2", "CR3", "NEF", "ARW", "DNG", "RAF", "ORF", "RW2", "PEF", "RAW"}


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_icc(data: bytes) -> Optional[bytes]:
    """Extract ICC profile bytes from a JPEG (APP2 marker with ICC_PROFILE\x00 prefix)."""
    i = 2  # skip SOI
    icc_chunks: dict = {}
    while i < len(data) - 3:
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        if marker == 0xDA:  # SOS — stop
            break
        seg_len = (data[i + 2] << 8) | data[i + 3]
        seg_end = i + 2 + seg_len
        if marker == 0xE2 and seg_len > 14:
            hdr = data[i + 4: i + 4 + 12]
            if hdr == b"ICC_PROFILE\x00":
                seq  = data[i + 16]      # chunk index (1-based)
                total = data[i + 17]     # total chunks
                chunk_data = data[i + 18: seg_end]
                icc_chunks[seq] = chunk_data
        i = seg_end
    if not icc_chunks:
        return None
    return b"".join(icc_chunks[k] for k in sorted(icc_chunks.keys()))


def _inject_icc(jpeg_data: bytes, icc_bytes: bytes) -> bytes:
    """Inject ICC profile into a JPEG right after the SOI marker."""
    if not icc_bytes:
        return jpeg_data
    # Build APP2 segments (max 65519 bytes of ICC data per segment)
    MAX_CHUNK = 65519
    chunks = [icc_bytes[i:i + MAX_CHUNK] for i in range(0, len(icc_bytes), MAX_CHUNK)]
    app2_blocks = bytearray()
    for idx, chunk in enumerate(chunks):
        seg_body = b"ICC_PROFILE\x00" + bytes([idx + 1, len(chunks)]) + chunk
        seg_len = len(seg_body) + 2
        app2_blocks += b"\xFF\xE2" + bytes([seg_len >> 8, seg_len & 0xFF]) + seg_body
    # Insert after SOI (first 2 bytes)
    return jpeg_data[:2] + bytes(app2_blocks) + jpeg_data[2:]


def img_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def apply_colormap_hot(arr: np.ndarray) -> np.ndarray:
    """Simple hot colormap: black→red→yellow→white"""
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        norm = np.zeros_like(arr, dtype=np.float32)
    else:
        norm = (arr - mn) / (mx - mn)
    r = np.clip(norm * 3, 0, 1)
    g = np.clip(norm * 3 - 1, 0, 1)
    b = np.clip(norm * 3 - 2, 0, 1)
    rgb = (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)
    return rgb


def error_image(msg: str, w: int = 480, h: int = 120) -> bytes:
    img = Image.new("RGB", (w, h), (20, 20, 20))
    draw = ImageDraw.Draw(img)
    words = msg.split()
    lines, line = [], []
    for w_ in words:
        test = " ".join(line + [w_])
        if len(test) > 55 and line:
            lines.append(" ".join(line))
            line = [w_]
        else:
            line.append(w_)
    if line:
        lines.append(" ".join(line))
    y = max(0, h // 2 - len(lines) * 10)
    for ln in lines:
        draw.text((10, y), ln, fill=(220, 80, 80))
        y += 22
    return img_to_png_bytes(img)


# ── format detection ─────────────────────────────────────────────────────────

def detect_format(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.upper().lstrip(".")
    if data[:2] == b"\xff\xd8":
        return "JPEG"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if data[:2] == b"BM":
        return "BMP"
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        if ext in RAW_EXTS:
            return ext
        return "TIFF"
    if ext in RAW_EXTS:
        return ext
    ext_map = {"JPG": "JPEG", "JPEG": "JPEG", "TIF": "TIFF", "TIFF": "TIFF",
               "BMP": "BMP", "PNG": "PNG"}
    return ext_map.get(ext, ext or "UNKNOWN")


def is_raw(fmt: str) -> bool:
    return fmt in RAW_EXTS


# ── structure parsers ─────────────────────────────────────────────────────────

def parse_jpeg(data: bytes) -> dict:
    NAMES = {0xD8: "SOI", 0xD9: "EOI", 0xDA: "SOS",
             0xC0: "SOF0", 0xC1: "SOF1", 0xC2: "SOF2", 0xC4: "DHT",
             0xDB: "DQT", 0xDD: "DRI",
             0xE0: "APP0", 0xE1: "APP1", 0xE2: "APP2", 0xEE: "APP14",
             0xFE: "COM"}
    markers = []
    scan_start = None
    scan_end = len(data) - 2
    pos = 0
    while pos < len(data) - 1:
        if data[pos] != 0xFF:
            pos += 1
            continue
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        if pos >= len(data):
            break
        mt = data[pos]
        pos += 1
        name = NAMES.get(mt, f"0xFF{mt:02X}")
        if mt == 0xD8:
            markers.append({"name": name, "offset": pos - 2, "size": 2})
        elif mt == 0xD9:
            markers.append({"name": name, "offset": pos - 2, "size": 2})
            scan_end = pos - 2
            break
        elif mt == 0xDA:
            if pos + 1 < len(data):
                length = struct.unpack(">H", data[pos:pos + 2])[0]
                markers.append({"name": name, "offset": pos - 2, "size": 2 + length})
                scan_start = pos + length
            break
        elif 0xD0 <= mt <= 0xD7:
            markers.append({"name": f"RST{mt - 0xD0}", "offset": pos - 2, "size": 2})
        else:
            if pos + 1 < len(data):
                length = struct.unpack(">H", data[pos:pos + 2])[0]
                markers.append({"name": name, "offset": pos - 2, "size": 2 + length})
                pos += length
    return {"type": "JPEG", "markers": markers,
            "scan_data_start": scan_start, "scan_data_end": scan_end,
            "total_size": len(data)}


def parse_bmp(data: bytes) -> dict:
    if len(data) < 54:
        return {"type": "BMP", "error": "File too small"}
    file_size = struct.unpack("<I", data[2:6])[0]
    pixel_offset = struct.unpack("<I", data[10:14])[0]
    dib_size = struct.unpack("<I", data[14:18])[0]
    width = struct.unpack("<i", data[18:22])[0]
    height = struct.unpack("<i", data[22:26])[0]
    bit_count = struct.unpack("<H", data[28:30])[0]
    compression = struct.unpack("<I", data[30:34])[0]
    bpp = bit_count // 8
    row_size = ((bit_count * abs(width) + 31) // 32) * 4
    COMP = {0: "BI_RGB", 1: "BI_RLE8", 2: "BI_RLE4", 3: "BI_BITFIELDS"}
    return {"type": "BMP", "file_size": file_size,
            "pixel_offset": pixel_offset, "dib_header_size": dib_size,
            "width": abs(width), "height": abs(height),
            "height_flipped": height < 0,
            "bit_count": bit_count, "bytes_per_pixel": bpp,
            "compression": COMP.get(compression, f"Unknown({compression})"),
            "row_size": row_size,
            "image_data_start": pixel_offset,
            "image_data_size": row_size * abs(height)}


def parse_tiff(data: bytes) -> dict:
    if len(data) < 8:
        return {"type": "TIFF", "error": "Too small"}
    bo = data[:2]
    if bo == b"II":
        e = "<"
    elif bo == b"MM":
        e = ">"
    else:
        return {"type": "TIFF", "error": "Invalid byte order"}
    ifd_off = struct.unpack(f"{e}I", data[4:8])[0]
    tags = []
    strip_offsets = []
    strip_byte_counts = []
    TNAMES = {256: "ImageWidth", 257: "ImageLength", 258: "BitsPerSample",
              259: "Compression", 262: "PhotometricInterp", 273: "StripOffsets",
              278: "RowsPerStrip", 279: "StripByteCounts", 282: "XResolution",
              283: "YResolution", 305: "Software", 322: "TileWidth",
              323: "TileLength", 324: "TileOffsets", 325: "TileByteCounts"}
    TYPE_SZ = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 11: 4, 12: 8}
    pos = ifd_off
    if pos + 2 > len(data):
        return {"type": "TIFF", "error": "IFD out of range"}
    n = struct.unpack(f"{e}H", data[pos:pos + 2])[0]
    pos += 2
    for _ in range(min(n, 100)):
        if pos + 12 > len(data):
            break
        tag = struct.unpack(f"{e}H", data[pos:pos + 2])[0]
        ftype = struct.unpack(f"{e}H", data[pos + 2:pos + 4])[0]
        count = struct.unpack(f"{e}I", data[pos + 4:pos + 8])[0]
        raw_val = data[pos + 8:pos + 12]
        tsz = TYPE_SZ.get(ftype, 4)
        total = tsz * count
        if total <= 4:
            if ftype == 3:
                value = struct.unpack(f"{e}H", raw_val[:2])[0]
            elif ftype == 4:
                value = struct.unpack(f"{e}I", raw_val)[0]
            else:
                value = struct.unpack(f"{e}I", raw_val)[0]
        else:
            off = struct.unpack(f"{e}I", raw_val)[0]
            if ftype == 3 and off + 2 * count <= len(data):
                value = [struct.unpack(f"{e}H", data[off + i * 2:off + i * 2 + 2])[0]
                         for i in range(min(count, 20))]
            elif ftype == 4 and off + 4 * count <= len(data):
                value = [struct.unpack(f"{e}I", data[off + i * 4:off + i * 4 + 4])[0]
                         for i in range(min(count, 20))]
            else:
                value = off
        tags.append({"tag": tag, "name": TNAMES.get(tag, f"Tag{tag}"), "value": value})
        if tag == 273:
            strip_offsets = value if isinstance(value, list) else [value]
        elif tag == 279:
            strip_byte_counts = value if isinstance(value, list) else [value]
        pos += 12
    img_start = min(strip_offsets) if strip_offsets else None
    return {"type": "TIFF", "byte_order": "LE" if e == "<" else "BE",
            "ifd_offset": ifd_off, "tags": tags[:30],
            "strip_offsets": strip_offsets[:5],
            "strip_byte_counts": strip_byte_counts[:5],
            "image_data_start": img_start, "total_size": len(data)}


def parse_png(data: bytes) -> dict:
    pos = 8
    chunks = []
    idat_start = None
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8].decode("ascii", errors="replace")
        chunks.append({"type": ctype, "offset": pos,
                       "data_size": length, "total_size": length + 12})
        if ctype == "IDAT" and idat_start is None:
            idat_start = pos + 8
        pos += length + 12
    return {"type": "PNG", "chunks": chunks,
            "image_data_start": idat_start, "total_size": len(data)}


def analyze_structure(data: bytes, fmt: str, filename: str) -> dict:
    try:
        if fmt == "JPEG":
            return parse_jpeg(data)
        elif fmt == "BMP":
            return parse_bmp(data)
        elif fmt == "TIFF" or is_raw(fmt):
            return parse_tiff(data)
        elif fmt == "PNG":
            return parse_png(data)
        else:
            return {"type": fmt, "total_size": len(data),
                    "image_data_start": min(1024, len(data) // 10)}
    except Exception as e:
        return {"type": fmt, "error": str(e), "total_size": len(data)}


# ── pixel → byte mapping ──────────────────────────────────────────────────────

def pixel_to_byte_range(x1: int, y1: int, x2: int, y2: int,
                        session: dict) -> Tuple[int, int]:
    fmt = session["format"]
    width = max(1, session["width"])
    height = max(1, session["height"])
    st = session["structure"]
    data_len = len(session["current_bytes"])

    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(x1, min(x2, width - 1))
    y2 = max(y1, min(y2, height - 1))

    if fmt == "BMP":
        bmp = st
        po = bmp.get("pixel_offset", 54)
        rs = bmp.get("row_size", width * bmp.get("bytes_per_pixel", 3))
        bpp = bmp.get("bytes_per_pixel", 3)
        h = bmp.get("height", height)
        if not bmp.get("height_flipped", False):
            by1 = h - 1 - y2
            by2 = h - 1 - y1
        else:
            by1, by2 = y1, y2
        start = po + by1 * rs + x1 * bpp
        end = po + by2 * rs + (x2 + 1) * bpp
        return max(po, start), min(data_len, end)

    elif fmt == "JPEG":
        ss = st.get("scan_data_start") or data_len // 4
        se = st.get("scan_data_end") or data_len - 2
        sz = max(1, se - ss)
        y1r = y1 / height
        y2r = (y2 + 1) / height
        start = ss + int(y1r * sz)
        end = ss + int(y2r * sz)
        xc = (x1 + x2) / (2 * width)
        row_sz = sz // height
        xoff = int(xc * row_sz * 0.4)
        start = max(ss, min(se - 1, start + xoff))
        end = max(start + 1, min(se, end + xoff))
        return start, end

    elif fmt in ("TIFF", "PNG") or is_raw(fmt):
        img_start = st.get("image_data_start")
        if img_start is None:
            img_start = data_len // 8
        sz = max(1, data_len - img_start)
        y1r = y1 / height
        y2r = (y2 + 1) / height
        start = img_start + int(y1r * sz)
        end = img_start + int(y2r * sz)
        return max(img_start, start), min(data_len, max(start + 1, end))

    else:
        hdr = min(1024, data_len // 10)
        sz = max(1, data_len - hdr)
        y1r = y1 / height
        y2r = (y2 + 1) / height
        start = hdr + int(y1r * sz)
        end = hdr + int(y2r * sz)
        return start, min(data_len, max(start + 1, end))


# ── destruction methods ───────────────────────────────────────────────────────

def _jpeg_safe_indices(buf: bytearray, start: int, end: int) -> list:
    """Return byte positions within [start, end) that are safe to modify.

    Rules for JPEG scan data:
    • Skip 0xFF bytes — they are either a marker prefix or part of a
      stuffed-byte pair (0xFF 0x00).  Touching them destroys the marker
      structure and causes *complete* Huffman de-sync → gray output.
    • Skip the byte immediately after 0xFF for the same reason.
    Everything else is a Huffman-coded data byte: safe to XOR / replace.
    """
    safe = []
    for i in range(end - start):
        ab = start + i
        b  = buf[ab]
        if b == 0xFF:
            continue
        if ab > 0 and buf[ab - 1] == 0xFF:
            continue
        safe.append(i)
    return safe


def _jpeg_safe_value(v: int) -> int:
    """Clamp a byte value so it never becomes 0xFF (false marker prefix)."""
    return 0xFE if v == 0xFF else v


def _pos_fracs(pos: str):
    """Return (lo_frac, hi_frac) for a tear position name (0.0-1.0 range)."""
    return {
        "q1": (0.00, 0.25), "q2": (0.25, 0.50),
        "q3": (0.50, 0.75), "q4": (0.75, 1.00),
        "top":    (0.00, 0.33), "middle": (0.33, 0.67), "bottom": (0.67, 1.00),
    }.get(pos, (0.00, 1.00))  # default: random = full range


def _pos_idx(pos: str, n: int):
    """Return (idx_lo, idx_hi) for a position name over n items."""
    lo_f, hi_f = _pos_fracs(pos)
    lo = int(lo_f * n)
    hi = max(lo + 1, int(hi_f * n))
    return max(0, lo), min(n, hi)


def apply_destruction(data: bytes, byte_start: int, byte_end: int,
                      method: str, intensity: float, fmt: str,
                      tear_position: str = "random",
                      blockshift_amount: float = 0.15) -> bytes:
    # ── blockshift: pixel-level HORIZONTAL shift of a row band ───────────────
    # Shifts a horizontal band of rows LEFT or RIGHT by blockshift_amount% of
    # image width.  Produces clean rectangular block displacement without
    # stripes (pure pixel operation, bypasses JPEG scan-data constraints).
    if method == "blockshift":
        try:
            import cv2 as _cv2
            # Re-encode without RST markers so Huffman decoding cascades
            # horizontally across MCU rows → vertical stripe glitch artifact.
            _icc_bs = _extract_icc(data)
            arr = _cv2.imdecode(np.frombuffer(data, np.uint8), _cv2.IMREAD_COLOR)
            if arr is None:
                return data
            _ok, _enc = _cv2.imencode(".jpg", arr, [_cv2.IMWRITE_JPEG_QUALITY, 100])
            if not _ok or len(_enc) == 0:
                return data
            no_rst = bytearray(_inject_icc(_enc.tobytes(), _icc_bs) if _icc_bs else _enc.tobytes())

            # Find SOS (0xFF 0xDA) marker to locate scan data start
            scan_data_start = None
            i = 2  # skip SOI
            while i < len(no_rst) - 1:
                if no_rst[i] == 0xFF and no_rst[i + 1] == 0xDA:
                    seg_len = (no_rst[i + 2] << 8) | no_rst[i + 3]
                    scan_data_start = i + 2 + seg_len
                    break
                elif no_rst[i] == 0xFF and no_rst[i + 1] != 0x00:
                    seg_len = (no_rst[i + 2] << 8) | no_rst[i + 3]
                    i += 2 + seg_len
                else:
                    i += 1
            if scan_data_start is None:
                return data

            # Build safe index list for the scan data region
            scan_end = len(no_rst)
            safe = _jpeg_safe_indices(no_rst, scan_data_start, scan_end)
            if not safe:
                return data
            n_safe = len(safe)
            rlen = scan_end - scan_data_start

            # Determine tear position within scan data
            idx_lo, idx_hi = _pos_idx(tear_position, n_safe)
            tear_idx = random.randint(idx_lo, max(idx_lo, idx_hi - 1)) if n_safe > 3 else 0
            tear_rel = safe[tear_idx] if n_safe > 3 else safe[0]

            # Apply byte rotation to produce vertical stripe artifact.
            # Use blockshift_amount directly (not scaled by intensity) so the
            # slider is the sole control — intensity always converges to max
            # for this method (always valid JPEG), making it meaningless here.
            # Factor 0.004 keeps the segment to ~0.4-20% of scan data.
            shift = max(32, int(n_safe * blockshift_amount * 0.001))
            # Cap segment to at most 4% of scan data to keep effect localized
            max_seg = max(128, n_safe // 25)
            seg_end = min(tear_rel + min(shift * 4, max_seg), rlen)
            sub = no_rst[scan_data_start + tear_rel : scan_data_start + seg_end]
            no_rst[scan_data_start + tear_rel : scan_data_start + seg_end] = sub[shift:] + sub[:shift]

            return bytes(no_rst)
        except Exception:
            return data

    if method == "blockshift_orig":
        try:
            import cv2 as _cv2
            _icc_bo = _extract_icc(data)
            arr = _cv2.imdecode(np.frombuffer(data, np.uint8), _cv2.IMREAD_COLOR)
            if arr is not None:
                h_img, w_img = arr.shape[:2]
                band_height = max(1, int(h_img * blockshift_amount))
                lo_row, hi_row = _pos_idx(tear_position, h_img)
                start_row = random.randint(lo_row, max(lo_row, hi_row - band_height - 1))
                start_row = max(0, min(start_row, h_img - band_height - 1))
                seg_end_row = min(start_row + band_height * 2, h_img)
                seg_len = seg_end_row - start_row
                if seg_len >= 2:
                    half = seg_len // 2
                    seg = arr[start_row:seg_end_row].copy()
                    arr[start_row:start_row + (seg_len - half)] = seg[half:]
                    arr[start_row + (seg_len - half):seg_end_row] = seg[:half]
                _ok, _enc = _cv2.imencode(".jpg", arr, [_cv2.IMWRITE_JPEG_QUALITY, 100])
                if _ok and len(_enc) > 0:
                    return _inject_icc(_enc.tobytes(), _icc_bo) if _icc_bo else _enc.tobytes()
        except Exception:
            pass
        return data

    if method == "hshift":
        try:
            import cv2 as _cv2
            _icc_hs = _extract_icc(data)
            arr = _cv2.imdecode(np.frombuffer(data, np.uint8), _cv2.IMREAD_COLOR)
            if arr is not None:
                h_img, w_img = arr.shape[:2]
                band_height = max(1, int(h_img * blockshift_amount * 2))
                lo_row, hi_row = _pos_idx(tear_position, h_img)
                start_row = random.randint(lo_row, max(lo_row, hi_row - band_height - 1))
                start_row = max(0, min(start_row, h_img - band_height - 1))
                end_row = min(start_row + band_height, h_img)
                shift_pixels = max(1, int(w_img * blockshift_amount))
                if random.random() < 0.5:
                    shift_pixels = -shift_pixels
                arr[start_row:end_row] = np.roll(arr[start_row:end_row], shift_pixels, axis=1)
                _ok, _enc = _cv2.imencode(".jpg", arr, [_cv2.IMWRITE_JPEG_QUALITY, 100])
                if _ok and len(_enc) > 0:
                    return _inject_icc(_enc.tobytes(), _icc_hs) if _icc_hs else _enc.tobytes()
        except Exception:
            pass
        return data

    # ── hshift_binary: MCU-block horizontal shift via RST segment reordering ──
    # Re-encodes with RST=1 (one MCU per restart) then shifts RST segments
    # within a band of MCU rows laterally by N MCU columns.
    # For large images: only the target band is RST=1 encoded to limit memory.
    if method == "hshift_binary":
        try:
            import cv2 as _cv2
            _icc_hb = _extract_icc(data)
            arr = _cv2.imdecode(np.frombuffer(data, np.uint8), _cv2.IMREAD_COLOR)
            if arr is None:
                return data
            h_img, w_img = arr.shape[:2]
            mcu_cols = (w_img + 15) // 16
            mcu_rows = (h_img + 15) // 16
            rst_param = getattr(_cv2, "IMWRITE_JPEG_RST_INTERVAL", 4)

            # ── determine band ──────────────────────────────────────────────
            lo_row, hi_row = _pos_idx(tear_position, mcu_rows)
            band_rows = max(1, int(mcu_rows * blockshift_amount * 2))
            start_mcu_row = random.randint(lo_row, max(lo_row, hi_row - band_rows))
            start_mcu_row = max(0, min(start_mcu_row, mcu_rows - band_rows - 1))
            end_mcu_row   = min(start_mcu_row + band_rows, mcu_rows)
            shift_mcus = max(1, int(mcu_cols * blockshift_amount))
            if random.random() < 0.5:
                shift_mcus = -shift_mcus

            # pixel rows for the band (MCU rows → pixel rows, aligned to 16)
            py0 = start_mcu_row * 16
            py1 = min(end_mcu_row * 16, h_img)
            band_arr = arr[py0:py1].copy()

            # ── encode ONLY the band with RST=1 ────────────────────────────
            _ok, _enc = _cv2.imencode(".jpg", band_arr,
                                      [_cv2.IMWRITE_JPEG_QUALITY, 100, rst_param, 1])
            if not _ok or len(_enc) == 0:
                return data
            jpeg = bytearray(_enc.tobytes())

            # find SOS scan-data start
            ss = None
            i = 2
            while i < len(jpeg) - 1:
                if jpeg[i] == 0xFF and jpeg[i+1] == 0xDA:
                    seg_len = (jpeg[i+2] << 8) | jpeg[i+3]
                    ss = i + 2 + seg_len
                    break
                elif jpeg[i] == 0xFF and jpeg[i+1] not in (0x00, 0xFF):
                    seg_len = (jpeg[i+2] << 8) | jpeg[i+3]
                    i += 2 + seg_len
                else:
                    i += 1
            if ss is None:
                return data

            # collect segments
            segments = []
            seg_start = ss
            j = ss
            while j < len(jpeg) - 1:
                if jpeg[j] == 0xFF and (0xD0 <= jpeg[j+1] <= 0xD7 or jpeg[j+1] == 0xD9):
                    segments.append((seg_start, j))
                    if jpeg[j+1] == 0xD9:
                        break
                    seg_start = j + 2
                    j += 2
                else:
                    j += 1
            else:
                if seg_start < len(jpeg):
                    segments.append((seg_start, len(jpeg)))

            band_mcu_rows = (py1 - py0 + 15) // 16
            if len(segments) < mcu_cols:
                return data

            # ── reorder segments (shift columns) ───────────────────────────
            new_scan = bytearray()
            rst_idx  = 0
            for seg_i, (seg_s, seg_e) in enumerate(segments):
                row_i = seg_i // mcu_cols
                col_i = seg_i % mcu_cols
                shifted_col = (col_i - shift_mcus) % mcu_cols
                src_i = row_i * mcu_cols + shifted_col
                if src_i < len(segments):
                    s2, e2 = segments[src_i]
                    new_scan.extend(jpeg[s2:e2])
                else:
                    new_scan.extend(jpeg[seg_s:seg_e])
                if seg_i < len(segments) - 1:
                    new_scan.extend([0xFF, 0xD0 + (rst_idx % 8)])
                    rst_idx += 1

            shifted_band_bytes = bytes(bytearray(jpeg[:ss]) + new_scan + bytearray([0xFF, 0xD9]))

            # ── decode shifted band and splice into full image ─────────────
            import PIL.ImageFile as _pif
            _pif.LOAD_TRUNCATED_IMAGES = True
            shifted_band_img = Image.open(io.BytesIO(shifted_band_bytes)).convert("RGB")
            shifted_band_img.load()
            shifted_arr = np.array(shifted_band_img)
            arr[py0:py0 + shifted_arr.shape[0]] = shifted_arr[:, :w_img]

            # ── final encode at full quality ────────────────────────────────
            _ok2, _enc2 = _cv2.imencode(".jpg", arr,
                                        [_cv2.IMWRITE_JPEG_QUALITY, 100])
            if not _ok2 or len(_enc2) == 0:
                return data
            out = bytes(_enc2)
            return _inject_icc(out, _icc_hb) if _icc_hb else out
        except Exception:
            return data

    buf = bytearray(data)
    sz  = byte_end - byte_start
    if sz <= 0:
        return bytes(buf)

    # ── JPEG: direct scan-data binary manipulation ────────────────────────────
    #
    # Key design rules for Photoshop compatibility:
    #   1. NEVER delete bytes — always replace.  File size must be identical.
    #   2. NEVER write 0xFF into scan data — it creates false JPEG markers.
    #   3. Modify as FEW bytes as possible (n factor kept low) so the Huffman
    #      decoder can still partially succeed in strict mode (Photoshop).
    #   4. "tear" uses concentrated XOR replacement, NOT byte rotation.
    #      Rotation shifts the Huffman bit-phase for ALL subsequent bytes,
    #      which causes Photoshop to show black/white from that point onward.
    #
    # ALL methods:
    #   1. Extract region as a local bytearray (isolated copy).
    #   2. Build safe-index list (positions where buf[i] != 0xFF and
    #      buf[i-1] != 0xFF — avoids clobbering marker bytes).
    #   3. Modify only n bytes (n = n_safe * intensity * 0.08 — 8× gentler).
    #   4. Write the whole region back in one shot.
    #   5. Assert len(result) == len(data) before returning.
    #
    if fmt == "JPEG":
        region = bytearray(buf[byte_start:byte_end])
        rlen   = len(region)

        # Build safe index list relative to region start
        safe = []
        for i in range(rlen):
            if region[i] == 0xFF:
                continue   # skip marker-prefix bytes
            prev = region[i - 1] if i > 0 else (buf[byte_start - 1] if byte_start > 0 else 0x00)
            if prev == 0xFF:
                continue   # skip stuffed-byte / marker-code partners
            safe.append(i)

        if not safe:
            return bytes(buf)

        n_safe = len(safe)
        # Keep modifications gentle for scattered methods (noise/shuffle/etc):
        # 15% factor — at slider=10% → 1.5%; at slider=100% → 15%.
        # "tear" uses its own larger factor below (0.4) so this n is ignored
        # for that method.  Minimum 16 to guarantee at least some change.
        n      = max(16, int(n_safe * intensity * 0.15))

        # Determine tear position index range for methods that use it
        idx_lo, idx_hi = _pos_idx(tear_position, n_safe)
        idx_lo = max(0, idx_lo)
        idx_hi = max(idx_lo + 1, min(idx_hi, n_safe - 1))

        if method == "noise":
            # XOR each sampled safe byte with a random mask, clamping away
            # from 0xFF.  Unlike plain byte-replacement, XOR preserves the
            # "texture" of the Huffman stream → colour shifts + line artifacts.
            masks = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
                     0x03, 0x07, 0x0F, 0x1F, 0x3F, 0xAA, 0x55, 0x66,
                     0x0C, 0x18, 0x30, 0x60, 0xC0, 0x99, 0x77, 0xBB]
            target = random.sample(safe, min(n, n_safe))
            for i in target:
                new_val = region[i] ^ random.choice(masks)
                region[i] = 0xFE if new_val == 0xFF else new_val

        elif method == "tear":
            tear_rel = safe[random.randint(idx_lo, max(idx_lo, idx_hi - 1))]
            shift    = max(4, int(n_safe * intensity * 0.12))
            seg_end  = min(tear_rel + shift * 4, rlen)
            sub      = region[tear_rel:seg_end]
            region[tear_rel:seg_end] = sub[shift:] + sub[:shift]

        elif method == "black":
            # Sort a sampled subset of safe bytes ascending.
            # Low-value Huffman data → sparse / low-energy → dark artifact bands.
            # intensity controls what fraction of safe bytes are touched.
            target = sorted(random.sample(safe, min(n, n_safe)))
            vals   = sorted(region[i] for i in target)
            for k, i in enumerate(target):
                region[i] = vals[k]

        elif method == "white":
            # Sort a sampled subset of safe bytes descending.
            # High-value Huffman data → dense / high-energy → bright artifact bands.
            target = sorted(random.sample(safe, min(n, n_safe)))
            vals   = sorted((region[i] for i in target), reverse=True)
            for k, i in enumerate(target):
                region[i] = vals[k]

        elif method == "invert":
            # Reverse the ORDER of a sampled subset of safe bytes.
            # Mirror sequence → colour-inversion-like banding, no new 0xFF bytes.
            target = sorted(random.sample(safe, min(n, n_safe)))
            vals   = [region[i] for i in target]
            vals.reverse()
            for k, i in enumerate(target):
                region[i] = vals[k]

        elif method == "shuffle":
            # Fully random permutation of a sampled subset of safe bytes.
            target = random.sample(safe, min(n, n_safe))
            vals   = [region[i] for i in target]
            random.shuffle(vals)
            for i, v in zip(target, vals):
                region[i] = v   # values came from the region → already safe

        elif method == "pattern":
            # Tile the first pat_len safe bytes as a repeating pattern across
            # a sampled subset of positions → periodic Huffman phase → stripes.
            pat_len = max(4, n_safe // 16)
            pat     = [region[safe[i]] for i in range(pat_len)]
            target  = random.sample(safe, min(n, n_safe))
            for k, i in enumerate(target):
                region[i] = pat[k % pat_len]  # values from region → safe

        elif method in ("frequency", "dct"):
            # Flip the MSB (sign bit) of safe bytes at a regular stride.
            # Inverting the sign of a Huffman data byte changes the sign of
            # the DCT coefficient it encodes → block-level colour inversion.
            # Clamp results away from 0xFF.
            stride = max(1, rlen // max(1, n))
            for i in safe:
                if i % stride == 0:
                    new_val = region[i] ^ 0x80
                    region[i] = 0xFE if new_val == 0xFF else new_val

        elif method == "zero":
            # Fill sampled safe positions with 0x00.
            # 0x00 is a valid scan-data byte (it never creates a false marker).
            target = random.sample(safe, min(n, n_safe))
            for i in target:
                region[i] = 0x00

        elif method == "ff":
            # Fill sampled safe positions with 0xFE (safe proxy for 0xFF).
            target = random.sample(safe, min(n, n_safe))
            for i in target:
                region[i] = 0xFE

        elif method == "adjacent":
            # Swap consecutive pairs of safe bytes.
            n_pairs = max(1, int(n_safe / 2 * intensity))
            for k in range(0, min(n_pairs * 2, n_safe - 1), 2):
                i, j = safe[k], safe[k + 1]
                region[i], region[j] = region[j], region[i]

        elif method == "repeat":
            # Replace each sampled safe byte with the byte immediately before it.
            target = random.sample(safe, min(n, n_safe))
            for i in target:
                prev = region[i - 1] if i > 0 else region[i]
                region[i] = 0xFE if prev == 0xFF else prev

        buf[byte_start:byte_end] = region
        result = bytes(buf)
        # ── size guarantee ────────────────────────────────────────────────────
        if len(result) != len(data):
            raise ValueError(f"JPEG: file size changed {len(data)} → {len(result)}")
        return result

    # ── Non-JPEG: direct byte operations ─────────────────────────────────────
    # n is defined here (JPEG path returned early above).
    n = max(16, int(sz * intensity * 0.08))

    if method == "noise":
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] = random.randint(0, 255)

    elif method == "tear":
        # Small-segment rotation — position determined by tear_position.
        lo_f, hi_f = _pos_fracs(tear_position)
        off   = random.randint(int(sz * lo_f), max(int(sz * lo_f), int(sz * hi_f) - 1))
        shift = max(4, int(sz * intensity * 0.12))
        seg_e = min(off + shift * 4, sz)
        sub   = bytearray(buf[byte_start + off : byte_start + seg_e])
        buf[byte_start + off : byte_start + seg_e] = sub[shift:] + sub[:shift]

    elif method == "black":
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] = 0x00

    elif method == "white":
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] = 0xFF

    elif method == "invert":
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] ^= 0xFF

    elif method == "shuffle":
        region = bytearray(buf[byte_start:byte_end])
        idxs = random.sample(range(sz), min(n, sz))
        vals = [region[i] for i in idxs]
        random.shuffle(vals)
        for i, v in zip(idxs, vals):
            region[i] = v
        buf[byte_start:byte_end] = region

    elif method == "pattern":
        pat_sz = max(4, sz // 16)
        pattern = bytes(buf[byte_start:byte_start + pat_sz])
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] = pattern[i % pat_sz]

    elif method in ("frequency", "dct"):
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] ^= 0x55

    elif method == "zero":
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] = 0x00

    elif method == "ff":
        idxs = random.sample(range(sz), min(n, sz))
        for i in idxs:
            buf[byte_start + i] = 0xFF

    elif method == "adjacent":
        region = bytearray(buf[byte_start:byte_end])
        target_count = max(1, min(n // 2, (sz - 1) // 2))
        starts = random.sample(range(0, sz - 1), min(target_count, sz - 1))
        for i in starts:
            region[i], region[i + 1] = region[i + 1], region[i]
        buf[byte_start:byte_end] = region

    elif method == "repeat":
        for i in sorted(random.sample(range(1, sz), min(n, sz - 1))):
            buf[byte_start + i] = buf[byte_start + i - 1]

    result = bytes(buf)
    # ── size guarantee ────────────────────────────────────────────────────────
    if len(result) != len(data):
        raise ValueError(f"Non-JPEG: file size changed {len(data)} → {len(result)}")
    return result


def make_preview(data: bytes, fmt: str, max_dim: int = 800) -> Tuple[bytes, str]:
    """Returns (content_bytes, mime_type).

    For JPEG: PIL tolerant decode → PNG, like Adobe Bridge.
    This shows block-level artifacts instead of browser color stripes.
    For other formats: PIL-decoded, resized PNG.
    """
    if fmt == "JPEG":
        # Bridge-like: PIL LOAD_TRUNCATED_IMAGES=True → PNG
        # This shows block-level artifacts instead of browser color stripes
        old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
        try:
            img = Image.open(io.BytesIO(data))
            img.load()
            img = img.convert("RGB")
            if max_dim > 0:
                w, h = img.size
                if max(w, h) > max_dim:
                    scale = max_dim / max(w, h)
                    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            return img_to_png_bytes(img), "image/png"
        except Exception:
            pass  # fallback below
        finally:
            _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag
    # fallback / non-JPEG
    try:
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGB")
        w, h = img.size
        if max_dim > 0 and max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return img_to_png_bytes(img), "image/png"
    except Exception as e:
        return error_image(f"Cannot decode: {e}"), "image/png"


def make_preview_tolerant(data: bytes, max_dim: int = 1200) -> Tuple[bytes, str]:
    """Bridge mode: force-decode using PIL's truncated-image tolerance.

    Equivalent to opening in Adobe Bridge — errors are silently ignored and
    as much of the image as possible is decoded and rendered.
    Uses LOAD_TRUNCATED_IMAGES=True (saved/restored around the call).
    Always returns a PNG so the result can be displayed on a canvas.
    """
    old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
    _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
    try:
        img = Image.open(io.BytesIO(data))
        img.load()          # force full pixel decode with truncation tolerance
        img = img.convert("RGB")
        w, h = img.size
        if max_dim > 0 and max(w, h) > max_dim:
            scale = max_dim / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        return img_to_png_bytes(img), "image/png"
    except Exception as e:
        return error_image(f"Bridge decode error: {e}"), "image/png"
    finally:
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag


# ── decode methods (Step 2) ───────────────────────────────────────────────────

def decode_pillow(data: bytes, max_dim: int = 800) -> Tuple[bytes, str]:
    """Pillow エラートレラント: LOAD_TRUNCATED_IMAGES=True で強制デコード。"""
    old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
    _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        img = img.convert("RGB")
        if max_dim > 0:
            w, h = img.size
            if max(w, h) > max_dim:
                s = max_dim / max(w, h)
                img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
        return img_to_png_bytes(img), "image/png"
    except Exception as e:
        return error_image(f"Pillow decode error: {e}"), "image/png"
    finally:
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag


def decode_opencv(data: bytes, max_dim: int = 800) -> Tuple[bytes, str]:
    """OpenCV 独自復元: cv2.imdecode(IMREAD_ANYCOLOR)。"""
    try:
        import cv2
        arr = np.frombuffer(data, dtype=np.uint8)
        img_arr = cv2.imdecode(arr, cv2.IMREAD_ANYCOLOR)
        if img_arr is None:
            return error_image("OpenCV: デコード失敗（画像が破損しすぎています）"), "image/png"
        if len(img_arr.shape) == 3 and img_arr.shape[2] >= 3:
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img_arr).convert("RGB")
        if max_dim > 0:
            w, h = img.size
            if max(w, h) > max_dim:
                s = max_dim / max(w, h)
                img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
        return img_to_png_bytes(img), "image/png"
    except ImportError:
        return error_image("OpenCV not installed — pip install opencv-python"), "image/png"
    except Exception as e:
        return error_image(f"OpenCV error: {e}"), "image/png"


def decode_libjpeg_fill(data: bytes, max_dim: int = 800) -> Tuple[bytes, str]:
    """libjpeg エラートレラント (Bridge 的): Pillow truncation + MedianFilter。"""
    from PIL import ImageFilter
    old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
    _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        img = img.convert("RGB")
        img = img.filter(ImageFilter.MedianFilter(size=3))
        if max_dim > 0:
            w, h = img.size
            if max(w, h) > max_dim:
                s = max_dim / max(w, h)
                img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
        return img_to_png_bytes(img), "image/png"
    except Exception as e:
        return error_image(f"libjpeg tolerant error: {e}"), "image/png"
    finally:
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag


def decode_strict(data: bytes, max_dim: int = 800) -> Tuple[bytes, str]:
    """厳密モード (Photoshop 的): 通常デコード。失敗時は有効プレフィクスを二分探索。"""
    old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
    _pil_imagefile.LOAD_TRUNCATED_IMAGES = False
    # Try strict decode first
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        img = img.convert("RGB")
        if max_dim > 0:
            w, h = img.size
            if max(w, h) > max_dim:
                s = max_dim / max(w, h)
                img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
        return img_to_png_bytes(img), "image/png"
    except Exception:
        pass
    finally:
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag

    # JPEG only: binary search for longest decodable prefix
    if data[:2] != b"\xff\xd8":
        return error_image("厳密モード: デコード不可（非JPEGファイル）"), "image/png"

    st = parse_jpeg(data)
    scan_start = st.get("scan_data_start") or (len(data) // 4)
    lo, hi = scan_start, len(data) - 2
    best_img: Optional[Image.Image] = None
    for _ in range(8):
        if hi - lo < 32:
            break
        mid = (lo + hi) // 2
        prefix = data[:mid] + b"\xff\xd9"
        try:
            _pil_imagefile.LOAD_TRUNCATED_IMAGES = False
            tmp = Image.open(io.BytesIO(prefix))
            tmp.load()
            best_img = tmp.convert("RGB")
            lo = mid
        except Exception:
            hi = mid
        finally:
            _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag

    if best_img is None:
        return error_image("厳密モード: デコード不可（破損が深刻すぎます）"), "image/png"
    if max_dim > 0:
        w, h = best_img.size
        if max(w, h) > max_dim:
            s = max_dim / max(w, h)
            best_img = best_img.resize((int(w * s), int(h * s)), Image.LANCZOS)
    return img_to_png_bytes(best_img), "image/png"


_DECODE_FNS = {
    "pillow":  decode_pillow,
    "opencv":  decode_opencv,
    "libjpeg": decode_libjpeg_fill,
    "strict":  decode_strict,
}


# ── visualization ─────────────────────────────────────────────────────────────

# libraw/rawpy orientation → PIL Transpose correction
# orient=6: camera was rotated 90° CW → correct by rotating 90° CCW
# orient=5: camera was rotated 90° CCW → correct by rotating 90° CW
# orient=3: 180° → rotate 180°
_RAWPY_ORIENT_MAP = {
    3: Image.Transpose.ROTATE_180,
    5: Image.Transpose.ROTATE_270,   # 90° CW correction
    6: Image.Transpose.ROTATE_90,    # 90° CCW correction
}


def visualize_bayer(data: bytes, fmt: str, filename: str,
                    full_res: bool = False) -> bytes:
    if not is_raw(fmt):
        return error_image(
            f"Not a RAW file (detected: {fmt}). Bayer visualization requires CR2/NEF/ARW/DNG etc.")
    if not RAWPY_AVAILABLE:
        return error_image("rawpy not installed. See README for setup.")
    try:
        import rawpy
        with rawpy.imread(io.BytesIO(data)) as raw:
            bayer = raw.raw_image_visible.astype(np.float32)
            pattern = raw.raw_pattern

            # --- EXIF orientation ---
            orient = 0
            try:
                orient = int(raw.metadata.orientation)
            except Exception:
                pass

            h, w = bayer.shape
            bayer = bayer / max(bayer.max(), 1.0)

            # Downscale for display (skip when downloading at full resolution)
            if not full_res:
                max_dim = 1200
                if max(h, w) > max_dim:
                    step = max(1, int(max(h, w) / max_dim / 2) * 2)  # even step
                    bayer_small = bayer[::step, ::step]
                    bayer_small = bayer_small[:bayer_small.shape[0] // 2 * 2,
                                              :bayer_small.shape[1] // 2 * 2]
                else:
                    bayer_small = bayer
            else:
                bayer_small = bayer

            sh, sw = bayer_small.shape
            result = np.zeros((sh, sw, 3), dtype=np.float32)

            for row in range(2):
                for col in range(2):
                    ch = int(pattern[row, col])
                    ci = min(2, ch)  # 0=R, 1=G, 2=B
                    vals = bayer_small[row::2, col::2]
                    out_h = (sh - row + 1) // 2
                    out_w = (sw - col + 1) // 2
                    result[row::2, col::2, ci] = vals[:out_h, :out_w]

            rgb = (np.clip(result, 0, 1) * 255).astype(np.uint8)
            img = Image.fromarray(rgb)

            # Apply orientation correction
            if orient in _RAWPY_ORIENT_MAP:
                img = img.transpose(_RAWPY_ORIENT_MAP[orient])

            # Add pattern label
            draw = ImageDraw.Draw(img)
            pat_str = "Pattern: " + "".join(
                ["RGGB"[int(pattern[r, c])] for r in range(2) for c in range(2)])
            orient_str = f"  orient={orient}" if orient else ""
            label = pat_str + orient_str
            draw.rectangle([0, 0, len(label) * 7 + 8, 20], fill=(0, 0, 0))
            draw.text((4, 3), label, fill=(255, 255, 100))
            return img_to_png_bytes(img)
    except Exception as e:
        return error_image(f"RAW decode error: {e}")


def visualize_dct(data: bytes, fmt: str, mode: str = "ac",
                  full_res: bool = False) -> bytes:
    if fmt != "JPEG":
        return error_image(f"DCT visualization is JPEG-only (detected: {fmt}).")
    try:
        img = Image.open(io.BytesIO(data)).convert("L")
        arr = np.array(img, dtype=np.float32) - 128.0
        h, w = arr.shape
        bh = h // 8
        bw = w // 8
        if bh == 0 or bw == 0:
            return error_image("Image too small for 8×8 DCT blocks.")
        dct_map = np.zeros((bh, bw), dtype=np.float32)
        for i in range(bh):
            for j in range(bw):
                block = arr[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8]
                if block.shape == (8, 8):
                    coeffs = dctn(block, norm="ortho")
                    if mode == "dc":
                        dct_map[i, j] = abs(float(coeffs[0, 0]))
                    else:
                        ac = coeffs.copy()
                        ac[0, 0] = 0
                        dct_map[i, j] = float(np.sum(np.abs(ac)))
        dct_log = np.log1p(dct_map)
        rgb = apply_colormap_hot(dct_log)
        small = Image.fromarray(rgb)
        # Scale each DCT block to 8×8 pixels → approximately original resolution
        large = small.resize((bw * 8, bh * 8), Image.NEAREST)
        if not full_res:
            # Blend with a faint original for spatial reference
            orig_small = img.resize((bw * 8, bh * 8), Image.LANCZOS).convert("RGB")
            result_img = Image.blend(large, orig_small, alpha=0.2)
        else:
            result_img = large
        draw = ImageDraw.Draw(result_img)
        label = f"DCT {'DC' if mode == 'dc' else 'AC'} coefficients  ({bw}×{bh} blocks)"
        draw.rectangle([0, 0, len(label) * 7 + 8, 20], fill=(0, 0, 0))
        draw.text((4, 3), label, fill=(255, 220, 80))
        return img_to_png_bytes(result_img)
    except Exception as e:
        return error_image(f"DCT error: {e}")


def visualize_fft(data: bytes, full_res: bool = False) -> bytes:
    try:
        img = Image.open(io.BytesIO(data)).convert("L")
        w, h = img.size
        MAX = 4096 if full_res else 1024
        if max(w, h) > MAX:
            s = MAX / max(w, h)
            img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
        arr = np.array(img, dtype=np.float32)
        F = fft2(arr)
        Fs = fftshift(F)
        mag = np.log1p(np.abs(Fs))
        rgb = apply_colormap_hot(mag)
        result = Image.fromarray(rgb)
        draw = ImageDraw.Draw(result)
        rw, rh = result.size
        cx, cy = rw // 2, rh // 2
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], outline=(255, 255, 255))
        draw.text((cx + 6, cy - 8), "DC (low freq)", fill=(255, 255, 255))
        draw.text((4, 3),
                  "FFT Power Spectrum (log scale)  center=low, edges=high freq",
                  fill=(255, 220, 80))
        return img_to_png_bytes(result)
    except Exception as e:
        return error_image(f"FFT error: {e}")


# ── routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 100 MB)")
    fmt = detect_format(file.filename or "", raw)
    try:
        pil = Image.open(io.BytesIO(raw))
        width, height = pil.size
    except Exception:
        if is_raw(fmt) and RAWPY_AVAILABLE:
            try:
                import rawpy
                with rawpy.imread(io.BytesIO(raw)) as r:
                    width, height = r.sizes.width, r.sizes.height
            except Exception:
                width, height = 0, 0
        else:
            width, height = 0, 0
    structure = analyze_structure(raw, fmt, file.filename or "")
    # ── JPEG: re-encode with RST restart markers ──────────────────────────
    # RST markers allow decoders (PIL, browsers, Photoshop) to resync at
    # each MCU row boundary.  Corruption between two RST markers only
    # breaks those MCU rows; adjacent rows decode correctly.
    # Result: block-level glitch art instead of full-image stripes.
    _img_width = 0
    if fmt == "JPEG":
        try:
            import cv2 as _cv2
            _icc = _extract_icc(raw)  # preserve ICC profile (e.g. Adobe RGB) before cv2 strips it
            _arr = _cv2.imdecode(np.frombuffer(raw, np.uint8), _cv2.IMREAD_COLOR)
            if _arr is not None:
                _h, _w = _arr.shape[:2]
                _img_width = _w
                # One full MCU row: each MCU is 16px wide, so _w MCUs span the full width
                _rst_interval = max(1, (_w + 15) // 16)
                _rst_param    = getattr(_cv2, "IMWRITE_JPEG_RST_INTERVAL", 4)
                _ok, _enc = _cv2.imencode(
                    ".jpg", _arr,
                    [_cv2.IMWRITE_JPEG_QUALITY, 100, _rst_param, _rst_interval],
                )
                if _ok and len(_enc) > 0:
                    _new = _enc.tobytes()
                    raw = _inject_icc(_new, _icc) if _icc else _new
        except Exception:
            pass  # keep original bytes if re-encoding fails
    fid = str(uuid.uuid4())
    sessions[fid] = {
        "original_bytes": raw,
        "current_bytes": raw,
        "history": [],
        "filename": file.filename or "image",
        "format": fmt,
        "width": width,
        "height": height,
        "structure": structure,
    }
    if fmt == "JPEG" and _img_width > 0:
        sessions[fid]["img_width"] = _img_width
        sessions[fid]["img_height"] = _h
    return {"file_id": fid, "format": fmt, "width": width, "height": height,
            "size": len(raw), "structure": structure}


@app.get("/preview/{file_id}")
async def preview(file_id: str, which: str = "current"):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")
    data = s["original_bytes"] if which == "original" else s["current_bytes"]
    content, mime = make_preview(data, s["format"])
    return Response(content=content, media_type=mime)


@app.get("/diff-overlay/{file_id}")
async def diff_overlay(file_id: str, full: bool = False, fmt: str = "png", font_size: Optional[int] = None, flat_var: Optional[int] = None, custom_text: Optional[str] = None, text_color: Optional[str] = None, line_height: Optional[int] = None, letter_spacing: Optional[int] = None):
    """Return destroyed image with original RGB values (or custom text) overlaid on changed areas.
    full=True → process at full resolution (for download).
    fmt → "png" (default) or "jpg" for JPEG output.
    custom_text → cycle through words of this text instead of RGB values.
    text_color → hex color string like #ff0000 for text fill (default green #00e650).
    line_height → cell height in px (overrides auto calculation).
    letter_spacing → offset added to cell width in px (negative to tighten).
    """
    sess = sessions.get(file_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Not found")

    orig_bytes = sess.get("original_bytes")
    curr_bytes = sess.get("current_bytes")
    if not orig_bytes or not curr_bytes:
        raise HTTPException(status_code=404, detail="No image data")

    try:
        old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
        try:
            orig_img = Image.open(io.BytesIO(orig_bytes)).convert("RGB")
            curr_img = Image.open(io.BytesIO(curr_bytes)).convert("RGB")
        finally:
            _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag

        # Preview: resize to max 800px.  Download (full=True): keep original size.
        if not full:
            MAX = 800
            ow, oh = orig_img.size
            if max(ow, oh) > MAX:
                scale = MAX / max(ow, oh)
                nw, nh = int(ow * scale), int(oh * scale)
                orig_img = orig_img.resize((nw, nh), Image.LANCZOS)
                curr_img = curr_img.resize((nw, nh), Image.LANCZOS)

        orig_arr = np.array(orig_img, dtype=np.int32)
        curr_arr = np.array(curr_img, dtype=np.int32)

        # Per-pixel mean channel difference
        pixel_diff = np.abs(orig_arr - curr_arr).mean(axis=2)  # shape (h, w)

        # Build overlay on top of curr_img
        overlay = curr_img.copy()
        draw = ImageDraw.Draw(overlay)

        h_img, w_img = orig_arr.shape[:2]
        # Scale font and cell size proportionally to image size
        # Reference: shorter side 4000px → font_size=6
        _scale = min(h_img, w_img) / 4000.0
        _auto_font = max(4, int(round(6 * _scale)))
        _fs = font_size if (font_size is not None and font_size >= 1) else _auto_font
        # cell_h: line_height override, or auto (font size + padding)
        cell_h = line_height if (line_height is not None and line_height >= 1) else max(_fs + 3, int(_fs * 1.3))

        # Prepare custom text tokens (if any)
        _tokens: Optional[list] = None
        if custom_text and custom_text.strip():
            # Split into individual characters (skip whitespace).
            # This ensures:
            #   1. Japanese text (no spaces) is tokenized correctly
            #   2. cell_w stays small even at large font sizes (max 1 char per cell)
            #   3. Text flows continuously L→R, top→bottom without restarting per row
            _tokens = [c for c in custom_text if not c.isspace()]
            if not _tokens:
                _tokens = ["?"]
            _max_char = 1  # always 1 char per cell in custom-text mode
        else:
            _max_char = 11  # "RRR,GGG,BBB"

        # Detect if custom text contains CJK/fullwidth characters
        # (CJK unified ideographs U+4E00–U+9FFF, Hiragana/Katakana, etc.)
        def _has_cjk(s: str) -> bool:
            return any('\u3000' <= c <= '\u9fff' or '\uff00' <= c <= '\uffef' for c in s)

        _needs_cjk = bool(_tokens and any(_has_cjk(t) for t in _tokens))
        # CJK chars are roughly square; ASCII chars are ~0.62× the height
        _char_w_ratio = 1.05 if _needs_cjk else 0.62

        # cell_w: sized to fit widest label, with optional letter_spacing offset
        cell_w = max(cell_h, int(_fs * _char_w_ratio * _max_char))
        if letter_spacing is not None and letter_spacing != 0:
            cell_w = max(1, cell_w + letter_spacing)
        font_size = _fs

        font = None
        # Font search order:
        #   1. Japanese/CJK-capable fonts (support hiragana, katakana, kanji)
        #   2. Monospace ASCII fonts as fallback
        _jp_fonts = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/PingFang.ttc",
        ]
        _ascii_fonts = [
            "/System/Library/Fonts/Monaco.ttf",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
        # Always try Japanese fonts first (they also cover ASCII)
        for fpath in _jp_fonts + _ascii_fonts:
            try:
                font = ImageFont.truetype(fpath, font_size)
                break
            except Exception:
                pass
        if font is None:
            font = ImageFont.load_default()

        # Parse text color (hex #rrggbb → RGB tuple); default green
        def _parse_hex(h: str) -> Tuple[int, int, int]:
            h = h.strip().lstrip("#")
            if len(h) == 3:
                h = h[0]*2 + h[1]*2 + h[2]*2
            r_ = int(h[0:2], 16); g_ = int(h[2:4], 16); b_ = int(h[4:6], 16)
            return (r_, g_, b_)
        try:
            _text_rgb: Tuple[int, int, int] = _parse_hex(text_color) if text_color else (0, 230, 80)
        except Exception:
            _text_rgb = (0, 230, 80)
        # Shadow: dark if text is bright, white if text is dark
        _lum = 0.299 * _text_rgb[0] + 0.587 * _text_rgb[1] + 0.114 * _text_rgb[2]
        _shadow_rgb: Tuple[int, int, int] = (0, 0, 0) if _lum > 100 else (200, 200, 200)

        # Threshold: a pixel is "changed" if mean channel diff > 25
        CHANGE_THRESH = 25
        # A cell is "corrupted" if ≥50% of its pixels changed significantly
        FRAC_THRESH = 0.50
        # Flat/uniform threshold: if current cell variance < this, it has no texture
        # → truly destroyed/gone (not shifted real content which would have texture)
        FLAT_VAR_THRESH = flat_var if (flat_var is not None and flat_var >= 0) else 150

        _token_counter = 0
        for cy in range(0, h_img, cell_h):
            for cx in range(0, w_img, cell_w):
                cell_pd = pixel_diff[cy:cy+cell_h, cx:cx+cell_w]
                changed_frac = float((cell_pd > CHANGE_THRESH).mean())
                if changed_frac < FRAC_THRESH:
                    continue  # not enough pixels changed — skip
                # Current cell must be flat/uniform (truly destroyed, not shifted content)
                cell_curr = curr_arr[cy:cy+cell_h, cx:cx+cell_w]
                if float(cell_curr.var()) > FLAT_VAR_THRESH:
                    continue  # has texture → probably shifted real content → skip
                # Skip truly pitch-black areas (unreadable text)
                if float(cell_curr.mean()) < 12:
                    continue

                if _tokens:
                    # Custom text mode: cycle through words
                    label = _tokens[_token_counter % len(_tokens)]
                    _token_counter += 1
                else:
                    # Default: draw original RGB values
                    sy = min(cy + cell_h // 2, h_img - 1)
                    sx = min(cx + cell_w // 2, w_img - 1)
                    r = int(orig_arr[sy, sx, 0])
                    g = int(orig_arr[sy, sx, 1])
                    b = int(orig_arr[sy, sx, 2])
                    label = f"{r},{g},{b}"

                # Shadow for readability (no background rectangle)
                draw.text((cx + 1, cy + 1), label, fill=_shadow_rgb, font=font)
                draw.text((cx, cy),         label, fill=_text_rgb,   font=font)

        headers = {}
        use_jpg = fmt.lower() in ("jpg", "jpeg")
        if use_jpg:
            buf_out = io.BytesIO()
            overlay.convert("RGB").save(buf_out, format="JPEG", quality=100)
            content = buf_out.getvalue()
            media_type = "image/jpeg"
            fname = "diff_overlay.jpg"
        else:
            content = img_to_png_bytes(overlay)
            media_type = "image/png"
            fname = "diff_overlay.png"
        if full:
            headers["Content-Disposition"] = f'attachment; filename="{fname}"'
        return Response(content=content, media_type=media_type, headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visualize/bayer/{file_id}")
async def viz_bayer(file_id: str, download: bool = False):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404)
    png = visualize_bayer(s["current_bytes"], s["format"], s["filename"],
                          full_res=download)
    headers = {}
    if download:
        stem = Path(s["filename"]).stem
        headers["Content-Disposition"] = f'attachment; filename="{stem}_bayer.png"'
    return Response(content=png, media_type="image/png", headers=headers)


@app.get("/visualize/dct/{file_id}")
async def viz_dct(file_id: str, mode: str = "ac", download: bool = False):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404)
    png = visualize_dct(s["current_bytes"], s["format"], mode, full_res=download)
    headers = {}
    if download:
        stem = Path(s["filename"]).stem
        headers["Content-Disposition"] = f'attachment; filename="{stem}_dct_{mode}.png"'
    return Response(content=png, media_type="image/png", headers=headers)


@app.get("/visualize/fft/{file_id}")
async def viz_fft(file_id: str, download: bool = False):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404)
    png = visualize_fft(s["current_bytes"], full_res=download)
    headers = {}
    if download:
        stem = Path(s["filename"]).stem
        headers["Content-Disposition"] = f'attachment; filename="{stem}_fft.png"'
    return Response(content=png, media_type="image/png", headers=headers)


def _apply_vertical_stripe(
    data: bytes,
    method: str,
    intensity: float,
    tear_position: str,
    blockshift_amount: float,
    rst_interval: Optional[int] = None,
) -> Optional[bytes]:
    """Apply binary destruction after rotating 90° CW, then rotate back.

    Horizontal JPEG stripes become vertical stripes in the final image.
    Returns None if decoding fails at any step.
    """
    old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
    _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
    try:
        # Step 1: Decode and rotate 90° CW via cv2 (preserves quality better)
        try:
            import cv2 as _cv2
            _src = _cv2.imdecode(np.frombuffer(data, np.uint8), _cv2.IMREAD_COLOR)
            if _src is None:
                raise ValueError("cv2 decode failed")
            # 90° CW = rotate 270° CCW in cv2 terms
            _rot = _cv2.rotate(_src, _cv2.ROTATE_90_CLOCKWISE)
        except Exception:
            # Fallback to PIL
            try:
                _cv2 = None
                src_img = Image.open(io.BytesIO(data)).convert("RGB")
                src_img.load()
                _rot_pil = src_img.transpose(Image.ROTATE_270)
                _rot = np.array(_rot_pil)[:, :, ::-1]  # RGB→BGR for consistency
            except Exception:
                return None

        # Step 2: Re-encode rotated image as JPEG WITH RST markers
        # ALWAYS calculate RST from rotated image dimensions (1 RST per MCU row).
        # Ignoring the UI slider value here — the slider is tuned for the original
        # orientation, but the rotated JPEG has a different width and needs its own interval.
        rot_h, rot_w = _rot.shape[:2]
        _effective_rst = max(1, (rot_w + 15) // 16)  # 1 RST per row of MCUs
        try:
            _cv2_mod = __import__("cv2")
            _rst_param = getattr(_cv2_mod, "IMWRITE_JPEG_RST_INTERVAL", 4)
            _ok, _enc = _cv2_mod.imencode(
                ".jpg", _rot,
                [_cv2_mod.IMWRITE_JPEG_QUALITY, 92, _rst_param, _effective_rst]
            )
            if not _ok or len(_enc) == 0:
                raise ValueError("cv2 encode failed")
            rotated_bytes = _enc.tobytes()
        except Exception:
            # Last resort: PIL without RST
            _rot_rgb = _rot[:, :, ::-1]  # BGR→RGB
            _pil_rot = Image.fromarray(_rot_rgb.astype(np.uint8))
            _buf = io.BytesIO()
            _pil_rot.save(_buf, format="JPEG", quality=100)
            rotated_bytes = _buf.getvalue()

        # Step 3: Analyze structure of rotated JPEG, then apply destruction
        rot_struct = analyze_structure(rotated_bytes, "JPEG", "rotated.jpg")
        rot_start = rot_struct.get("scan_data_start") or len(rotated_bytes) // 4
        rot_end   = rot_struct.get("scan_data_end")   or len(rotated_bytes) - 2

        destroyed = apply_destruction(
            rotated_bytes, rot_start, rot_end,
            method, intensity, "JPEG",
            tear_position=tear_position,
            blockshift_amount=blockshift_amount,
        )

        # Step 4: Decode destroyed image (truncated OK) and rotate back -90° CW
        try:
            dest_img = Image.open(io.BytesIO(destroyed)).convert("RGB")
            dest_img.load()
        except Exception:
            return None
        final = dest_img.transpose(Image.ROTATE_90)  # 90° CCW = back to original orientation

        # Step 5: Re-encode as JPEG
        out_buf = io.BytesIO()
        final.save(out_buf, format="JPEG", quality=100)
        return out_buf.getvalue()

    finally:
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag


def _rebase_jpeg_rst(current_bytes: bytes, rst_interval: int) -> bytes:
    """Re-encode JPEG with a new RST interval.  Decodes current (possibly
    corrupted) bytes via OpenCV error-concealment, then re-encodes cleanly
    with the requested MCU restart interval.  Returns original bytes on failure."""
    try:
        import cv2 as _cv2
        _arr = _cv2.imdecode(np.frombuffer(current_bytes, np.uint8), _cv2.IMREAD_COLOR)
        if _arr is None:
            return current_bytes
        _rst_param = getattr(_cv2, "IMWRITE_JPEG_RST_INTERVAL", 4)
        _ok, _enc = _cv2.imencode(
            ".jpg", _arr,
            [_cv2.IMWRITE_JPEG_QUALITY, 95, _rst_param, rst_interval],
        )
        if _ok and len(_enc) > 0:
            return _enc.tobytes()
    except Exception:
        pass
    return current_bytes


@app.post("/destroy/{file_id}")
async def destroy(file_id: str,
                  x1: int = Form(...), y1: int = Form(...),
                  x2: int = Form(...), y2: int = Form(...),
                  method: str = Form("noise"),
                  intensity: float = Form(0.3),
                  rst_interval: int = Form(8)):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")
    intensity = max(0.01, min(1.0, intensity))
    rst_interval = max(1, min(256, rst_interval))

    # ── JPEG: re-encode with new RST interval when block size changed ─────────
    if s["format"] == "JPEG" and rst_interval != s.get("rst_interval", 8):
        rebased = _rebase_jpeg_rst(s["current_bytes"], rst_interval)
        if rebased != s["current_bytes"]:
            s["current_bytes"] = rebased
            s["structure"] = analyze_structure(rebased, "JPEG", s.get("filename", ""))
        s["rst_interval"] = rst_interval

    byte_start, byte_end = pixel_to_byte_range(x1, y1, x2, y2, s)
    original_size = len(s["current_bytes"])
    try:
        new_data = apply_destruction(s["current_bytes"], byte_start, byte_end,
                                      method, intensity, s["format"])
    except ValueError as e:
        raise HTTPException(500, f"Destruction error: {e}")

    # ── file-size guarantee: reject if size changed ───────────────────────────
    if len(new_data) != original_size:
        raise HTTPException(500,
            f"File size changed after destruction: {original_size} → {len(new_data)}")

    s["history"].append(s["current_bytes"])
    if len(s["history"]) > MAX_UNDO:
        s["history"].pop(0)
    s["current_bytes"] = new_data
    corrupted = False
    try:
        img_check = Image.open(io.BytesIO(new_data))
        img_check.load()
    except Exception:
        corrupted = True
    preview_bytes, preview_mime = make_preview(new_data, s["format"])
    import base64
    preview_b64 = base64.b64encode(preview_bytes).decode()
    return {"ok": True, "corrupted": corrupted,
            "size_preserved": True,
            "original_size": original_size,
            "byte_start": byte_start, "byte_end": byte_end,
            "undo_depth": len(s["history"]),
            "preview_b64": preview_b64,
            "preview_mime": preview_mime}


@app.post("/undo/{file_id}")
async def undo(file_id: str):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404)
    if not s["history"]:
        return {"ok": False, "msg": "Nothing to undo"}
    s["current_bytes"] = s["history"].pop()
    import base64
    preview_bytes, preview_mime = make_preview(s["current_bytes"], s["format"])
    return {"ok": True, "undo_depth": len(s["history"]),
            "preview_b64": base64.b64encode(preview_bytes).decode(),
            "preview_mime": preview_mime}


@app.get("/download/{file_id}")
async def download(file_id: str):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404)
    filename = s["filename"]
    stem = Path(filename).stem
    suffix = Path(filename).suffix or ".bin"
    return Response(
        content=s["current_bytes"],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{stem}_destroyed{suffix}"'}
    )


@app.get("/preview-tolerant/{file_id}")
async def preview_tolerant(file_id: str):
    """Bridge mode: force-decode with LOAD_TRUNCATED_IMAGES=True → PNG."""
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")
    content, mime = make_preview_tolerant(s["current_bytes"])
    return Response(content=content, media_type=mime)


@app.get("/download-tolerant/{file_id}")
async def download_tolerant(file_id: str):
    """Bridge mode: full-resolution tolerant decode → downloadable PNG."""
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")
    content, _ = make_preview_tolerant(s["current_bytes"], max_dim=0)  # 0 = no resize
    stem = Path(s["filename"]).stem
    return Response(
        content=content,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{stem}_destroyed_bridge.png"'}
    )


@app.get("/decode/{method}/{file_id}")
async def decode_preview_ep(method: str, file_id: str):
    """Step 2 preview: decode with one of the 4 methods (800 px PNG)."""
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")
    fn = _DECODE_FNS.get(method)
    if not fn:
        raise HTTPException(400, f"Unknown decode method: {method}")
    content, mime = fn(s["current_bytes"], 800)
    return Response(content=content, media_type=mime)


@app.get("/save/{file_id}")
async def save_decoded(file_id: str, method: str = "pillow", fmt: str = "jpeg"):
    """Step 3 save: full-resolution decode → download in chosen format."""
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")
    fn = _DECODE_FNS.get(method, decode_pillow)
    png_bytes, _ = fn(s["current_bytes"], 0)   # max_dim=0 → full resolution
    try:
        img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(500, f"Save decode error: {e}")
    stem = Path(s["filename"]).stem
    buf = io.BytesIO()
    fmt = (fmt or "jpeg").lower()
    if fmt == "jpeg":
        img.save(buf, format="JPEG", quality=100)
        mime = "image/jpeg"
        dl_name = f"{stem}_destroyed.jpg"
    elif fmt == "tiff":
        img.save(buf, format="TIFF")
        mime = "image/tiff"
        dl_name = f"{stem}_destroyed.tiff"
    else:
        img.save(buf, format="PNG")
        mime = "image/png"
        dl_name = f"{stem}_destroyed.png"
    return Response(
        content=buf.getvalue(),
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{dl_name}"'},
    )


@app.get("/structure/{file_id}")
async def structure(file_id: str):
    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404)
    return s["structure"]


@app.get("/info/{file_id}")
async def get_info(file_id: str):
    sess = sessions.get(file_id)
    if not sess:
        raise HTTPException(404)
    w = sess.get("img_width", 0)
    h = sess.get("img_height", 0)
    mcu_row = max(1, (w + 15) // 16) if w > 0 else 50
    shorter = min(w, h) if w > 0 and h > 0 else 0
    default_font = max(4, int(round(6 * shorter / 4000))) if shorter > 0 else 6
    return JSONResponse({"img_width": w, "img_height": h, "default_rst_interval": mcu_row, "default_font_size": default_font})


def is_valid_image(data: bytes) -> bool:
    """Return True if PIL can still decode the image."""
    old_flag = _pil_imagefile.LOAD_TRUNCATED_IMAGES
    _pil_imagefile.LOAD_TRUNCATED_IMAGES = True
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        return True
    except Exception:
        return False
    finally:
        _pil_imagefile.LOAD_TRUNCATED_IMAGES = old_flag


@app.post("/auto-destroy/{file_id}")
async def auto_destroy(
    file_id: str,
    iterations: int = Form(10),
    max_intensity: float = Form(0.3),
    methods: str = Form("noise,tear,invert,shuffle,pattern,frequency"),
    rst_interval: Optional[int] = Form(None),
    tear_position: str = Form("random"),
    blockshift_amount: float = Form(0.15),
    vertical_stripe: bool = Form(False),
):
    """Randomly destroy the image N times, keeping only valid results.

    Per iteration:
    1. Pick a random region (5–70 % of image dimensions).
    2. Pick a random method.
    3. Binary-search for highest intensity that still produces a decodable file.
    4. Accept if any valid intensity found; skip otherwise.
    """
    import base64

    s = sessions.get(file_id)
    if not s:
        raise HTTPException(404, "Session not found")

    iterations = max(1, min(50, iterations))
    max_intensity = max(0.01, min(1.0, max_intensity))
    if rst_interval is not None:
        rst_interval = max(1, min(500, rst_interval))
    method_list = [m.strip() for m in methods.split(",") if m.strip()]
    if not method_list:
        method_list = ["noise", "invert", "shuffle"]

    w = max(1, s["width"])
    h = max(1, s["height"])
    fmt = s["format"]

    # ── JPEG: re-encode with new RST interval if provided ────────────────────
    if rst_interval is not None and fmt == "JPEG" and rst_interval != s.get("rst_interval"):
        rebased = _rebase_jpeg_rst(s["current_bytes"], rst_interval)
        if rebased != s["current_bytes"]:
            s["current_bytes"] = rebased
            s["structure"] = analyze_structure(rebased, "JPEG", s.get("filename", ""))
        s["rst_interval"] = rst_interval

    # One undo checkpoint for the whole batch
    s["history"].append(s["current_bytes"])
    if len(s["history"]) > MAX_UNDO:
        s["history"].pop(0)

    accepted = 0
    skipped = 0
    log: List[dict] = []
    working_data = s["current_bytes"]

    # Pre-compute full-image byte range once (auto-destroy always targets the
    # entire file so corruption is distributed evenly top-to-bottom).
    if fmt == "JPEG":
        _ss = s["structure"].get("scan_data_start") or len(working_data) // 4
        _se = s["structure"].get("scan_data_end") or len(working_data) - 2
        _full_start, _full_end = _ss, _se
    else:
        _full_start, _full_end = pixel_to_byte_range(0, 0, w - 1, h - 1, s)

    for _ in range(iterations):
        method = random.choice(method_list)
        if method == "frequency" and fmt != "JPEG":
            others = [m for m in method_list if m != "frequency"]
            method = random.choice(others or ["noise"])

        byte_start, byte_end = _full_start, _full_end
        x1, y1, x2, y2 = 0, 0, w - 1, h - 1

        # Re-encode with requested RST interval before each pass
        # (blockshift skips this — it decodes to pixels internally)
        current = working_data
        if rst_interval is not None and fmt == "JPEG" and method not in ("blockshift", "blockshift_orig", "hshift"):
            try:
                import cv2 as _cv2
                _arr = _cv2.imdecode(np.frombuffer(current, np.uint8), _cv2.IMREAD_COLOR)
                if _arr is not None:
                    _rst_param = getattr(_cv2, "IMWRITE_JPEG_RST_INTERVAL", 4)
                    _ok, _enc = _cv2.imencode(".jpg", _arr, [_cv2.IMWRITE_JPEG_QUALITY, 95, _rst_param, rst_interval])
                    if _ok and len(_enc) > 0:
                        current = _enc.tobytes()
            except Exception:
                pass

        lo, hi = 0.01, max_intensity
        best_data: Optional[bytes] = None
        best_intensity = 0.0

        for _ in range(5):  # 5 bisection steps
            mid = (lo + hi) / 2
            if vertical_stripe and fmt == "JPEG":
                # Rotate 90° → destroy → rotate back: horizontal bands → vertical stripes
                candidate = _apply_vertical_stripe(
                    current, method, mid,
                    tear_position=tear_position,
                    blockshift_amount=blockshift_amount,
                    rst_interval=rst_interval,
                )
                # vertical stripe re-encodes, so always "valid" if returned
                if candidate is not None:
                    best_data = candidate
                    best_intensity = mid
                    lo = mid
                else:
                    hi = mid
            else:
                candidate = apply_destruction(current, byte_start, byte_end,
                                              method, mid, fmt,
                                              tear_position=tear_position,
                                              blockshift_amount=blockshift_amount)
                if is_valid_image(candidate):
                    best_data = candidate
                    best_intensity = mid
                    lo = mid
                else:
                    hi = mid

        if best_data is not None:
            working_data = best_data
            accepted += 1
            log.append({"method": method, "intensity": round(best_intensity, 3),
                        "region": [x1, y1, x2, y2], "ok": True})
        else:
            skipped += 1
            log.append({"method": method, "region": [x1, y1, x2, y2], "ok": False})

    s["current_bytes"] = working_data
    preview_bytes, preview_mime = make_preview(working_data, fmt)
    preview_b64 = base64.b64encode(preview_bytes).decode()

    return {
        "ok": True,
        "accepted": accepted,
        "skipped": skipped,
        "undo_depth": len(s["history"]),
        "preview_b64": preview_b64,
        "preview_mime": preview_mime,
        "log": log,
    }

# Binary Image Destroyer

画像のバイナリ構造を可視化し、データを直接操作して破壊するツール。

## セットアップ

### 1. 仮想環境を作成（推奨）

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

### 2. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

### rawpy / LibRaw のインストールについて

`rawpy` は内部で **LibRaw** ライブラリを使用します。
多くの環境では `pip install rawpy` だけで動作しますが、失敗する場合は以下を試してください。

**macOS (Homebrew)**

```bash
brew install libraw
pip install rawpy
```

**Ubuntu / Debian**

```bash
sudo apt-get install libraw-dev
pip install rawpy
```

**Windows**
通常は pip のバイナリホイールが自動インストールされます。問題が起きた場合は [rawpy Releases](https://github.com/letmaik/rawpy/releases) から .whl を手動ダウンロードしてください。

rawpy のインストールが難しい場合でも、RAW ファイル以外の機能（JPEG/TIFF/BMP/PNG）はすべて利用できます。

---

## 起動

```bash
uvicorn app:app --reload
```

ブラウザで http://localhost:8000 を開いてください。

---

## 対応フォーマット

| フォーマット | 構造ビューア | バイナリ破壊 | バイト位置の精度 |
|---|---|---|---|
| JPEG | DCT / FFT | ✅ | スキャンデータ比例マッピング |
| TIFF (非圧縮) | FFT | ✅ | ストリップオフセットから計算 |
| BMP | FFT | ✅ | ピクセル完全マッピング |
| PNG | FFT | ✅ | IDATチャンク比例マッピング |
| CR2 / NEF / ARW / DNG | Bayer / FFT | ✅ | TIFF構造からマッピング |
| その他Pillow対応形式 | FFT | ✅ | 比例マッピング |

---

## 機能概要

### タブ 1：構造ビューア
- **FFT スペクトル** — 全フォーマット対応。低周波成分（中心）と高周波成分（周辺）を可視化
- **DCT 係数マップ** — JPEG 専用。AC/DC 成分を切り替えて各 8×8 ブロックの係数強度をヒートマップ表示
- **ベイヤー配列** — RAW ファイル専用。R/G/B チャンネルを色分けしてオーバーレイ表示

### タブ 2：バイナリ破壊
- ドラッグで破壊領域を選択し、8 種類の破壊方式を適用
- 強度スライダーで影響するバイト量を調整
- アンドゥ最大 10 回
- 元のフォーマットのままダウンロード

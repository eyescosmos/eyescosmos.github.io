#!/usr/bin/env python3
"""
check_texten_completeness.py

photographer-essay-overrides.js の全エントリについて、
textJa にある主要セクション（経歴・表現解説・批評と受容）が
textEn にも対応する英語セクションとして存在するかを確認する。

使い方:
    python3 scripts/check_texten_completeness.py
"""
import re, sys

OVERRIDES_PATH = "data/photographer-essay-overrides.js"

# textJa の主要見出し（部分一致で検索）→ textEn で期待されるキーワード
JA_SECTIONS = {
    "経歴":       ["Biography", "Career", "Background", "Formation"],
    "表現解説":   ["Expression", "Method", "Style", "Approach", "Analysis"],
    "批評と受容": ["Critical", "Criticism", "Reception", "Legacy", "Evaluation"],
}

def extract_backtick_value(text: str, key: str) -> str:
    """key: `...` の値を取り出す（複数行・エスケープバッククォート対応）"""
    pattern = rf"{re.escape(key)}:\s*`"
    m = re.search(pattern, text)
    if not m:
        return ""
    start = m.end()
    # エスケープされた \` は閉じ括弧とみなさず、素の ` で終端する
    pos = start
    result = []
    while pos < len(text):
        if text[pos] == '\\' and pos + 1 < len(text) and text[pos + 1] == '`':
            result.append('`')
            pos += 2
        elif text[pos] == '`':
            break
        else:
            result.append(text[pos])
            pos += 1
    return "".join(result)

def extract_entries(js: str) -> dict[str, dict]:
    """'id': { ... } のブロックを雑に抽出"""
    entries = {}
    for m in re.finditer(r"'([\w\-]+)':\s*\{", js):
        slug = m.group(1)
        start = m.start()
        # 対応する閉じ括弧を探す（簡易）
        depth = 0
        pos = m.start()
        while pos < len(js):
            if js[pos] == '{':
                depth += 1
            elif js[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = js[start:pos + 1]
        entries[slug] = block
    return entries

def check_section(text_en: str, ja_heading: str) -> bool:
    """textEn に対応する英語キーワードが含まれるか"""
    keywords = JA_SECTIONS[ja_heading]
    return any(kw.lower() in text_en.lower() for kw in keywords)

def main():
    with open(OVERRIDES_PATH, encoding="utf-8") as f:
        js = f.read()

    entries = extract_entries(js)
    issues = []

    for slug, block in entries.items():
        text_ja = extract_backtick_value(block, "textJa")
        text_en = extract_backtick_value(block, "textEn")

        if not text_ja:
            continue  # textJa 自体がないエントリはスキップ

        if not text_en:
            issues.append((slug, "textEn が存在しない"))
            continue

        # textJa に含まれる主要セクションを確認
        for ja_heading, _ in JA_SECTIONS.items():
            if ja_heading not in text_ja:
                continue  # このセクション自体 textJa にない
            if not check_section(text_en, ja_heading):
                issues.append((slug, f"textJa に「{ja_heading}」があるが textEn に対応セクションなし"))

        # 極端な文字数差（textEn が textJa の 30% 未満）を警告
        ratio = len(text_en) / max(len(text_ja), 1)
        if ratio < 0.3:
            issues.append((slug, f"textEn が textJa の {ratio:.0%} しかない（短すぎる可能性）"))

    if not issues:
        print("OK: textEn の過不足なし")
        sys.exit(0)
    else:
        print(f"WARN: {len(issues)} 件の問題が見つかりました\n")
        for slug, msg in issues:
            print(f"  [{slug}] {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()

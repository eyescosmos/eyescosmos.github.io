#!/usr/bin/env bash
# git フック（pre-push の preflight）を有効化するワンショット設定。
#
# core.hooksPath はマシンごとのローカル設定でリポジトリに同梱されないため、
# 新規 clone・別マシン（Codex 等）では一度これを実行するまで pre-push が効かない。
# 実行後は git push のたびに自動で preflight.py が走り、FAIL なら push がブロックされる。
#
#   bash scripts/setup_hooks.sh
#
# これは git 側の仕組みなので、エージェントが CLAUDE.md を読むかどうかに依存しない。
set -euo pipefail

REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

echo "== git フック有効化 =="

# 1) core.hooksPath を .githooks に設定
git config core.hooksPath .githooks
echo "→ git config core.hooksPath を設定しました"

# 2) 現在の設定状況を表示
echo
echo "-- 現在の設定 --"
echo "core.hooksPath = $(git config --get core.hooksPath || echo '(未設定)')"

# 3) pre-push の存在・実行権・preflight 呼び出しを確認
HOOK=".githooks/pre-push"
if [ ! -f "$HOOK" ]; then
  echo "✗ $HOOK が見つかりません" >&2
  exit 1
fi
if [ ! -x "$HOOK" ]; then
  chmod +x "$HOOK"
  echo "→ $HOOK に実行権を付与しました"
fi
echo "$HOOK 実行権: $([ -x "$HOOK" ] && echo OK || echo NG)"

if grep -q "preflight.py" "$HOOK"; then
  echo "$HOOK は preflight.py を呼びます: OK"
else
  echo "✗ $HOOK が preflight.py を呼んでいません（フック内容を確認してください）" >&2
  exit 1
fi

echo
echo "✓ 完了。これ以降 git push のたびに preflight が自動実行されます。"
echo "  （緊急回避が必要なときのみ: git push --no-verify）"

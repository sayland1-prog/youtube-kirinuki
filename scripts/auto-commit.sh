#!/bin/bash
# コードが変更されたら自動で git commit & push する
# 使い方: bash scripts/auto-commit.sh

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BRANCH="main"

echo "👀 ファイル監視を開始: $REPO_DIR"
echo "   変更を検知したら自動で commit & push します (Ctrl+C で停止)"

# 最後のコミットから変更があれば即時コミット
_commit_and_push() {
  cd "$REPO_DIR" || return
  if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    git commit -m "auto: $TIMESTAMP" \
      --author="Claude Sonnet 4.6 <noreply@anthropic.com>" 2>/dev/null || return
    git push origin "$BRANCH" 2>&1 | grep -v "^$" || true
    echo "✅ [$TIMESTAMP] コミット & プッシュ完了"
  fi
}

# 起動時に未コミットの変更があればすぐ処理
_commit_and_push

# ファイル変更を監視してコミット（3秒のデバウンス）
fswatch -r \
  --exclude ".git" \
  --exclude "node_modules" \
  --exclude ".next" \
  --exclude "__pycache__" \
  --exclude "output" \
  --exclude "*.pyc" \
  --latency 3 \
  "$REPO_DIR" | while read -r _path; do
  _commit_and_push
done

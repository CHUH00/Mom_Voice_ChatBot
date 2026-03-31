#!/bin/bash
# 변경 사항 주기적 자동 푸시 스크립트

echo "Starting auto-push daemon..."
while true; do
    if [[ $(git status --porcelain) ]]; then
        git add .
        git commit -m "Auto-commit: $(date)"
        git push origin main
        echo "Changes pushed to GitHub at $(date)"
    fi
    sleep 60
done

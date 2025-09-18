#!/bin/bash

# GitHub推送脚本 - 使用Personal Access Token
# 请将YOUR_TOKEN替换为你的GitHub Personal Access Token

GITHUB_TOKEN="YOUR_TOKEN"
REPO_URL="https://${GITHUB_TOKEN}@github.com/mengguiyouziyi/phishing-url-detector.git"

echo "正在推送代码到GitHub..."
git push -u origin "$REPO_URL" master

if [ $? -eq 0 ]; then
    echo "✅ 代码推送成功！"
else
    echo "❌ 推送失败，请检查网络连接和token权限"
fi
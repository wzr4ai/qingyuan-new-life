#!/bin/bash

# 设置 -e 选项，如果任何命令失败，脚本会立即退出
set -e

# --- 动态计算路径，使脚本在哪里执行都能正常工作 ---
# 获取脚本文件所在的目录
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

echo "脚本目录: $SCRIPT_DIR"
PROJECT_ROOT=$SCRIPT_DIR

echo "项目根目录: $PROJECT_ROOT"

# 定义源文件和目标文件的绝对路径
ENV_FILE="$PROJECT_ROOT/backend/.env"
EXAMPLE_FILE="$PROJECT_ROOT/backend/.env.example"

# 检查 .env 文件是否存在
if [ ! -f "$ENV_FILE" ]; then
    echo "警告: 源文件 '$ENV_FILE' 不存在，无法生成 .env.example。"
    exit 0
fi

# --- 核心处理逻辑 ---
grep -v '^#' "$ENV_FILE" | grep -v '^\s*$' | sed 's/=.*/=/' > "$EXAMPLE_FILE"

echo "'$EXAMPLE_FILE' 已根据 '$ENV_FILE' 更新。"

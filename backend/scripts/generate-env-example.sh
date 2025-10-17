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

# 定义一个排除列表，这些变量的值将保持不变，因为它们不是敏感信息。
# 你可以根据需要向这个列表中添加更多变量。
EXCLUDE_VARS=(
    "ENVIRONMENT"
    "APP_HOST"
    "APP_PORT"
    "MYSQL_HOST"
    "MYSQL_PORT"
    "DB_NAME"
)

# 将 bash 数组转换为 awk 可用的、以空格分隔的字符串
exclude_list_str=$(printf "%s " "${EXCLUDE_VARS[@]}")

# 使用 awk 来处理文件，因为它可以更好地处理多行记录
awk -v exclude_list="$exclude_list_str" '
BEGIN {
    # 将传入的排除列表字符串转换为 awk 关联数组，方便快速查找
    split(exclude_list, temp_arr, " ");
    for (i in temp_arr) {
        exclude[temp_arr[i]] = 1;
    }
    # in_multiline 是一个状态标志，用于跟踪我们是否在一个多行变量的内部
    in_multiline = 0;
    # multiline_quote 用于记录开启多行变量的引号类型 (单引号或双引号)
    multiline_quote = "";
}

# 规则1: 如果我们正在一个需要脱敏的多行变量内部，就忽略当前行
in_multiline == 1 {
    # 检查当前行是否是多行变量的结束行。
    # 我们通过检查行的最后一个字符是否与开始时的引号匹配来判断。
    if (length($0) > 0 && substr($0, length($0)) == multiline_quote) {
        in_multiline = 0; # 退出多行模式
        multiline_quote = "";
    }
    next; # 跳到下一行，不执行任何打印操作
}

# 规则2: 保留所有注释行和空行
/^\s*#/ || /^\s*$/ {
    print;
    next;
}

# 规则3: 处理所有包含 "=" 的变量赋值行
/=/ {
    # 提取变量名 (直到第一个等号的所有内容)
    var_name = $0;
    sub(/=.*/, "", var_name);

    # 提取变量值 (从第一个等号之后的所有内容)
    var_value = $0;
    sub(/[^=]*=/, "", var_value);

    # 检查变量是否在排除列表中
    if (var_name in exclude) {
        print; # 如果在，直接打印原始行
        next;
    }

    # 检查是否是多行变量的开始
    # 条件：值的第一个字符是单引号或双引号，但最后一个字符不是相同的引号
    if ((match(var_value, /^\047/) && !match(var_value, /\047$/)) || (match(var_value, /^"/) && !match(var_value, /"$/))) {
        # 记录开启多行变量的引号类型
        multiline_quote = substr(var_value, 1, 1);
        
        # 生成小写的占位符
        placeholder = tolower(var_name);
        print var_name "=\"" placeholder "\""; # 打印脱敏后的单行版本
        
        in_multiline = 1; # 进入多行模式
        next;
    }

    # 处理普通的单行变量
    placeholder = tolower(var_name);
    # 始终用双引号包裹，以确保格式统一和安全
    print var_name "=\"" placeholder "\"";
    next;
}

# 规则4: 打印任何其他不匹配上述规则的行 (为了程序的健壮性)
{ print; }

' "$ENV_FILE" > "$EXAMPLE_FILE"

echo "'$EXAMPLE_FILE' 已根据 '$ENV_FILE' 成功更新。"
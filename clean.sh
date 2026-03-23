#!/bin/zsh

# 检查是否提供了一个参数
if [ "$#" -ne 1 ]; then
    echo "使用方法: $0 <新文件夹名称>"
    exit 1
fi

# 将第一个参数赋值给变量 DIR_NAME
DIR_NAME="$1"

# 检查同名文件夹是否已经存在
if [ -d "$DIR_NAME" ]; then
    echo "错误: 文件夹 '$DIR_NAME' 已存在。"
    exit 1
fi

# 创建文件夹
echo "正在创建文件夹: $DIR_NAME"
mkdir -p "$DIR_NAME"

# 检查 'pic' 文件夹是否存在，如果存在则移动
if [ -d "pic" ]; then
    echo "正在移动 'pic' 文件夹..."
    mv pic "$DIR_NAME/"
else
    echo "警告: 'pic' 文件夹不存在，跳过移动。"
fi

# 移动所有 .pdf 文件
# 使用 zsh 的 globbing 功能检查文件是否存在
if ls *.pdf &> /dev/null; then
    echo "正在移动所有 .pdf 文件..."
    mv *.pdf "$DIR_NAME/"
else
    echo "信息: 没有找到 .pdf 文件。"
fi


# 移动所有 .tex 文件
if ls *.tex &> /dev/null; then
    echo "正在移动所有 .tex 文件..."
    mv *.tex "$DIR_NAME/"
else
    echo "信息: 没有找到 .tex 文件。"
fi

# 移动所有 .txt 文件
if ls *.txt &> /dev/null; then
    echo "正在移动所有 .txt 文件..."
    mv *.txt "$DIR_NAME/"
else
    echo "信息: 没有找到 .tex 文件。"
fi

echo "操作完成！文件和文件夹已移动到 '$DIR_NAME'。"

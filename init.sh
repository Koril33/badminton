#!/bin/sh

# 设置 pip 使用清华镜像
mkdir -p ~/.pip

cat > ~/.pip/pip.conf <<EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

echo "pip 配置已设置为清华源。"

# 创建虚拟环境
python3 -m venv venv

# 检查虚拟环境是否成功创建
if [ -d "venv" ]; then
    # 激活虚拟环境
    . venv/bin/activate
    echo "虚拟环境已激活。"

    # 安装必要的库
    pip install concurrent-log-handler requests apscheduler
    echo "依赖已安装完毕。"
else
    echo "虚拟环境创建失败。"
    exit 1
fi

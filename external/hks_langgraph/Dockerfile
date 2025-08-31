# 使用官方Python镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目依赖文件
COPY requirements.txt .

# 配置阿里云PyPI镜像源并安装依赖
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制项目所有文件
COPY . .

# 暴露应用端口（根据实际项目修改）
EXPOSE 2024

# 启动命令（根据实际项目入口文件修改）
CMD ["langgraph", "dev", "--host", "0.0.0.0"]
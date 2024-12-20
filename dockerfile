FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录的所有文件复制到容器的 /app 目录
COPY webhook.py .

# 安装 Flask 及其依赖
RUN pip install Flask

# 启动 Flask 应用
CMD ["python", "webhook.py"]

# 基础镜像：轻量的Python 3.10
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码文件
COPY app.py .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

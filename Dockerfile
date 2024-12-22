# 使用官方的 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器的 /app 目录
COPY . /app

# 安装 Flask 和其他依赖项
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 暴露 Flask 默认的端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# 启动 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0"]


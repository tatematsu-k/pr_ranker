# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

COPY main.py ./

# 必要なパッケージをインストール
RUN pip install requests

# デフォルトコマンド
CMD ["python", "main.py"]
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 直接用 Django 开发服务器跑，MVP 阶段够用
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

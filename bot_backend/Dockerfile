FROM python:3.9

WORKDIR /bot_backend

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python3", "bot_main.py"]
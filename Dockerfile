
FROM python:3.12-slim-bookworm


WORKDIR /app


COPY . .

RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple


RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


EXPOSE 8000


CMD ["python", "main.py"]



FROM python:3.12-slim-bookworm


WORKDIR /app


COPY . .


RUN pip install -i  https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt




EXPOSE 8000


CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]


FROM python:3.10.1

COPY requirements.txt .
RUN pip install -r requirements.txt

#CMD exec gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

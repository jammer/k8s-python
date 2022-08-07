FROM python:bullseye
RUN pip install nats-py
RUN pip install httpx
WORKDIR /
COPY broadcast.py ./
CMD ["python3","broadcast.py"]

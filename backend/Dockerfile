FROM python:bullseye
RUN pip install Flask
RUN pip install "psycopg[binary]"
RUN pip install nats-py
WORKDIR /
COPY backend.py ./
ENV FLASK_APP=backend.py
ENV FLASK_ENV=development
CMD ["/usr/local/bin/flask","run","--host=0.0.0.0","--port=3000"]

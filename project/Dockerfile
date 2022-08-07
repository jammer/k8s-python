FROM python:bullseye
RUN pip install Flask
RUN pip install httpx
WORKDIR /
COPY project.py ./
ENV FLASK_APP=project.py
ENV FLASK_ENV=development
CMD ["/usr/local/bin/flask","run","--host=0.0.0.0","--port=3001"]

FROM krayzpipes/pylibraries:latest

COPY ./src /app

ENV PYTHONPATH /app
ENV REDIS_URL red1:6379

EXPOSE 80

CMD ["uvicorn", "testmon:app", "--host", "0.0.0.0", "--port", "80"]

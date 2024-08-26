FROM python:3.10.13-slim-bullseye

WORKDIR /multidb

COPY . /multidb/

RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
ENV ACCESS_TOKEN_LIFETIME 24
ENV REFRESH_TOKEN_LIFETIME 168

ENV LOG_FILE_ROTATION_INTERVAL M

ENV AUTHORIZATION_STATUS INACTIVE

ENV DB_ENGINE postgresql+psycopg2
ENV DB_HOST localhost
ENV DB_PORT 5432


EXPOSE 8089

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8089"]
# FROM python:3.14-alpine / multiplatform
FROM python@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92

WORKDIR /code

RUN apk add --no-cache openssl nodejs npm ca-certificates

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./prisma /code/prisma

RUN prisma generate

COPY ./app /code/app

COPY ./seed /code/seed

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

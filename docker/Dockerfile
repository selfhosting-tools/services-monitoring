FROM python:3.8-alpine

COPY requirements.txt /tmp
RUN \
    apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev && \
    pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt && \
    apk del .build-deps

COPY src /services-monitoring/src
COPY docker/entrypoint.py /services-monitoring

WORKDIR /services-monitoring

ENV PYTHONPATH /services-monitoring

EXPOSE 8000

ENTRYPOINT ["python" ,"-u", "entrypoint.py"]

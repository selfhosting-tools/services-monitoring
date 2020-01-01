FROM python:3.7

COPY . /services-monitoring

WORKDIR /services-monitoring

RUN pip install -r requirements.txt

ENV PYTHONPATH /services-monitoring

ENTRYPOINT ["python" ,"-u", "docker/entrypoint.py"]

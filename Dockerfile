# syntax=docker/dockerfile:1
FROM python:latest
WORKDIR /home/anton/python/RS_lightFM/rest_test
COPY requirement.txt requirement.txt
RUN pip3 install -r requirement.txt
COPY . .
CMD ["python3", "RecommendServer.py"]

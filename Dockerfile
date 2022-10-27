# syntax=docker/dockerfile:1
FROM python:3.8.10
COPY requirement.txt requirement.txt
RUN pip3 install -r requirement.txt
COPY . .
EXPOSE 5000/tcp
CMD ["python3", "RecommendServer.py", "--host 0.0.0.0"]

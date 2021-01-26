FROM python:3.7-alpine
WORKDIR /code
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
FROM python:3.12.3-alpine

WORKDIR /app

RUN pip install --upgrade pip
RUN apk add --no-cache postgresql-dev gcc musl-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "python core.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
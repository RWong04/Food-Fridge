FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN apk update && apk add postgresql-client
COPY . .

CMD ["gunicorn", "Food_Waste_Fridge.wsgi:application", "--bind", "0.0.0.0:8000"]

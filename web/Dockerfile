FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies required for Pillow
RUN apk add --no-cache jpeg-dev zlib-dev libjpeg build-base

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Explicitly install Pillow with all required dependencies
RUN pip install --no-cache-dir Pillow

COPY . .

CMD ["gunicorn", "Food_Waste_Fridge.wsgi:application", "--bind", "0.0.0.0:8000"]

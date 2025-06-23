FROM python:3.11-slim

# System kutubxonalarni o‘rnatish
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libgobject-2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    libpng-dev \
    libssl-dev \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu \
    fonts-freefont-ttf && \
    apt-get clean
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

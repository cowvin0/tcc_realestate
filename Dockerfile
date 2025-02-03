FROM python:3.10-slim

# install deps of OS
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# dir of app
WORKDIR /app

COPY ../requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy source code
COPY . .
# COPY ../.env .

# expose port
EXPOSE 8050

# execute app
CMD ["uvicorn", "app.api:api", "--host", "0.0.0.0", "--port", "8050"]

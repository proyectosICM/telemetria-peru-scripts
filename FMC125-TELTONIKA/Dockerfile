FROM python:3.11-slim

WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir paho-mqtt==2.1.0 websockets==16.0

EXPOSE 9526

CMD ["python", "main.py"]

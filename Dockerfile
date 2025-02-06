FROM python:3.9-slim
  WORKDIR /app
  COPY main.py /app/main.py
  RUN pip install discord.py
  CMD ["python", "main.py"]

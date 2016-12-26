FROM python:3.5.2-onbuild

RUN apt-get update && apt-get install -y pandoc && apt-get clean && rm -rf /var/lib/apt/lists/*
EXPOSE 8080
CMD ["python", "./app.py"]
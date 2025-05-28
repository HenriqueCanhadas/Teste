FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

RUN echo "Verificando arquivos no container:" && \
    ls -R /app/templates
    
WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000

CMD ["/bin/sh", "-c", "exec gunicorn setup.wsgi:application --bind 0.0.0.0:$PORT"]

# Use uma imagem base Python com suporte ao sistema
FROM python:3.11-slim

# Instala ffmpeg e dependências do Python
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Cria diretório de trabalho
WORKDIR /app

# Copia arquivos para o container
COPY . /app

# Instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expõe a porta padrão do Django
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["/bin/sh", "-c", "exec gunicorn setup.wsgi:application --bind 0.0.0.0:$PORT"]


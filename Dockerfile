# Base image
FROM nvcr.io/nvidia/pytorch:22.08-py3

# Configuracao de CUDA
ENV PYTORCH_CUDA_ALLOC_CONF=garbage_collection_threshold:0.8,max_split_size_mb:2048

# Evita perguntas ao instalar pacotes
ENV DEBIAN_FRONTEND=noninteractive

# Instalacao de dependencias
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 sox && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip && \
    pip3 install --ignore-installed --no-cache-dir Flask openai-whisper

# Define workspace
WORKDIR /app

# Copia o arquivo do serviço Flask para o container
COPY app.py /app/app.py

# Define a variável FLASK_APP
ENV FLASK_APP=app.py

# Expõe a porta 5000
EXPOSE 5000

# Comando para rodar o serviço Flask
CMD ["flask", "run", "--host=0.0.0.0"]

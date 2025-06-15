FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome para Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo de spaCy en español
RUN python -m spacy download es_core_news_sm

# Copiar código fuente
COPY . .

# Crear directorio para modelos
RUN mkdir -p models

# Exponer puertos
EXPOSE 5005 5055

# Comando por defecto
CMD ["bash", "run.sh"]
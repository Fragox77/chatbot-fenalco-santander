#!/bin/bash

# Script para ejecutar el chatbot de Fenalco Santander

echo "🚀 Iniciando Chatbot Fenalco Santander..."

# Verificar si existe el modelo entrenado
if [ ! -f "models/20240101-120000-friendly-slope.tar.gz" ]; then
    echo "📚 Entrenando modelo de Rasa..."
    rasa train
fi

# Función para verificar si un servicio está corriendo
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Esperando a que $service_name esté disponible en puerto $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port" > /dev/null 2>&1; then
            echo "✅ $service_name está disponible"
            return 0
        fi
        echo "🔄 Intento $attempt/$max_attempts - Esperando $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name no está disponible después de $max_attempts intentos"
    return 1
}

# Función para iniciar servicios en background
start_services() {
    echo "🔧 Iniciando servicios..."
    
    # Iniciar servidor de acciones
    echo "🎯 Iniciando servidor de acciones..."
    rasa run actions --debug &
    ACTIONS_PID=$!
    
    # Esperar a que el servidor de acciones esté listo
    if check_service "Actions Server" 5055; then
        echo "✅ Servidor de acciones iniciado correctamente"
    else
        echo "❌ Error iniciando servidor de acciones"
        exit 1
    fi
    
    # Iniciar servidor principal de Rasa
    echo "🤖 Iniciando servidor principal de Rasa..."
    rasa run --enable-api --cors "*" --debug &
    RASA_PID=$!
    
    # Esperar a que el servidor principal esté listo
    if check_service "Rasa Server" 5005; then
        echo "✅ Servidor principal iniciado correctamente"
    else
        echo "❌ Error iniciando servidor principal"
        kill $ACTIONS_PID 2>/dev/null
        exit 1
    fi
}

# Función para manejar la terminación limpia
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $RASA_PID 2>/dev/null
    kill $ACTIONS_
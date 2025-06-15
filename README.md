# 🤖 Chatbot Fenalco Santander

Chatbot inteligente desarrollado con Rasa Framework para el departamento de capacitación de Fenalco Santander. Proporciona información automatizada sobre programas de capacitación, fechas, horarios y costos.

## 🚀 Características

- ✅ Procesamiento de lenguaje natural en español
- ✅ Consulta de programas de capacitación
- ✅ Información de fechas, horarios y costos
- ✅ Interfaz web responsive
- ✅ Integración con base de datos CSV
- ✅ Containerización con Docker

## 🛠️ Tecnologías Utilizadas

- **Rasa Framework** - Motor de NLP y gestión de diálogos
- **Python** - Lenguaje de programación principal
- **HTML/CSS/JavaScript** - Interfaz web
- **Docker** - Containerización
- **CSV** - Base de datos de programas

## 📋 Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

## 🔧 Instalación

### Opción 1: Instalación Manual

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/chatbot-fenalco-santander.git
   cd chatbot-fenalco-santander
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv chatbot_env
   ```

3. **Activar entorno virtual:**
   ```bash
   # Windows
   chatbot_env\Scripts\activate

   # Linux/Mac
   source chatbot_env/bin/activate
   ```

4. **Instalar dependencias:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Entrenar el modelo:**
   ```bash
   rasa train
   ```

### Opción 2: Con Docker

```bash
git clone https://github.com/tu-usuario/chatbot-fenalco-santander.git
cd chatbot-fenalco-santander
docker-compose up --build
```

## 🚀 Ejecución

### Método Manual (3 terminales)

**Terminal 1 - Servidor Rasa:**
```bash
rasa run --enable-api --cors "*" --port 5005
```

**Terminal 2 - Servidor de Acciones:**
```bash
rasa run actions --port 5055
```

**Terminal 3 - Servidor Web:**
```bash
python -m http.server 3000
```

### Método Docker
```bash
docker-compose up
```

Luego abrir: `http://localhost:3000`

## 💬 Ejemplos de Uso

- "Hola" - Saludo inicial
- "¿Qué programas tienen disponibles?" - Lista de programas
- "Cuéntame sobre el diplomado en alta gerencia" - Información específica
- "¿Cuánto cuesta el bootcamp empresarial?" - Consulta de precios
- "¿Cuáles son los horarios?" - Información de horarios

## 📁 Estructura del Proyecto

```
chatbot-fenalco-santander/
├── data/
│   ├── nlu.yml          # Datos de entrenamiento NLU
│   ├── stories.yml      # Historias de conversación
│   └── rules.yml        # Reglas de diálogo
├── actions/
│   └── actions.py       # Acciones personalizadas
├── web/
│   ├── index.html       # Interfaz web principal
│   ├── style.css        # Estilos CSS
│   └── script.js        # Lógica JavaScript
├── config.yml           # Configuración del pipeline
├── domain.yml           # Definición del dominio
├── requirements.txt     # Dependencias Python
├── Dockerfile          # Configuración Docker
├── docker-compose.yml  # Orquestación de servicios
├── programas.csv       # Base de datos de programas
└── README.md           # Este archivo
```

## 🔧 Configuración

### Personalizar Programas
Edita el archivo `programas.csv` para agregar o modificar programas de capacitación.

### Modificar Respuestas
Las respuestas del bot se configuran en `domain.yml` en la sección `responses`.

### Entrenar con Nuevos Datos
1. Modifica `data/nlu.yml` para agregar nuevos intents
2. Actualiza `data/stories.yml` con nuevos flujos
3. Ejecuta `rasa train` para reentrenar

## 🐛 Resolución de Problemas

### Error de dependencias
```bash
pip install rasa==3.6.0
pip install pandas numpy
```

### Python no reconocido
- Reinstalar Python marcando "Add to PATH"
- Reiniciar terminal

### El modelo no entrena
```bash
rasa train --force
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [tu-usuario](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Fenalco Santander por la oportunidad del proyecto
- Comunidad de Rasa por la documentación y soporte
- Contribuidores del proyecto

## 📞 Contacto

- Email: tu-email@ejemplo.com
- LinkedIn: [tu-perfil](https://linkedin.com/in/tu-perfil)
- GitHub: [@tu-usuario](https://github.com/tu-usuario)

---

⭐ ¡No olvides dar una estrella al proyecto si te fue útil!

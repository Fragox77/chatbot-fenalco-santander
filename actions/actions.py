from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
import requests
import json
from datetime import datetime, timedelta
import pandas as pd

# Base de datos de programas
PROGRAMAS_DB = {
    "diplomados": [
        {
            "nombre": "Diplomado en Gestión Comercial y Ventas",
            "duracion": "120 horas",
            "modalidad": ["Virtual", "Presencial"],
            "precio": 850000,
            "descripcion": "Desarrolla habilidades avanzadas en estrategias comerciales, técnicas de venta y gestión de equipos comerciales.",
            "modulos": ["Fundamentos de ventas", "Negociación efectiva", "Servicio al cliente", "Liderazgo comercial"],
            "disponible": True
        },
        {
            "nombre": "Diplomado en Legislación Comercial",
            "duracion": "100 horas",
            "modalidad": ["Virtual"],
            "precio": 720000,
            "descripcion": "Conoce la normatividad comercial, tributaria y laboral aplicable al sector empresarial.",
            "modulos": ["Derecho comercial", "Legislación tributaria", "Normas laborales", "Contratos comerciales"],
            "disponible": True
        },
        {
            "nombre": "Diplomado en Transformación Digital",
            "duracion": "80 horas",
            "modalidad": ["Virtual"],
            "precio": 950000,
            "descripcion": "Lidera procesos de transformación digital en tu organización.",
            "modulos": ["Marketing digital", "E-commerce", "Analítica de datos", "Automatización"],
            "disponible": True
        },
        {
            "nombre": "Diplomado en Gerencia de Proyectos",
            "duracion": "90 horas",
            "modalidad": ["Presencial", "Virtual"],
            "precio": 890000,
            "descripcion": "Gestiona proyectos exitosos con metodologías reconocidas internacionalmente.",
            "modulos": ["PMI", "Scrum", "Lean", "Gestión de riesgos"],
            "disponible": True
        }
    ],
    "talleres": [
        {
            "nombre": "Taller de Liderazgo Empresarial",
            "duracion": "16 horas",
            "modalidad": ["Presencial"],
            "precio": 320000,
            "descripcion": "Desarrolla competencias de liderazgo para dirigir equipos de alto rendimiento.",
            "disponible": True
        },
        {
            "nombre": "Taller de Comunicación Asertiva",
            "duracion": "12 horas",
            "modalidad": ["Virtual"],
            "precio": 250000,
            "descripcion": "Mejora tus habilidades comunicativas en el entorno empresarial.",
            "disponible": True
        },
        {
            "nombre": "Taller de Inteligencia Emocional",
            "duracion": "20 horas",
            "modalidad": ["Presencial"],
            "precio": 380000,
            "descripcion": "Desarrolla la inteligencia emocional para el éxito profesional.",
            "disponible": True
        }
    ]
}

DESCUENTOS = {
    "fenalco_afiliado": 0.15,  # 15%
    "grupo_3": 0.10  # 10%
}

class ActionBuscarPrograma(Action):
    def name(self) -> Text:
        return "action_buscar_programa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        programa_interes = tracker.get_slot("programa_interes")

        if programa_interes and programa_interes.lower() in PROGRAMAS_DB:
            programas = PROGRAMAS_DB[programa_interes.lower()]
            mensaje = f"📚 **{programa_interes.upper()} DISPONIBLES**\n\n"

            for i, programa in enumerate(programas, 1):
                if programa["disponible"]:
                    mensaje += f"{i}. **{programa['nombre']}**\n"
                    mensaje += f"   • Duración: {programa['duracion']}\n"
                    mensaje += f"   • Modalidad: {', '.join(programa['modalidad'])}\n"
                    mensaje += f"   • Inversión: ${programa['precio']:,}\n"
                    mensaje += f"   • {programa['descripcion']}\n\n"

            mensaje += "¿Te interesa información específica de algún programa?"
            dispatcher.utter_message(text=mensaje)
        else:
            dispatcher.utter_message(text="¿Podrías especificar qué tipo de programa te interesa? Tenemos diplomados, talleres, seminarios, masterclass y bootcamps.")

        return []

class ActionCalcularDescuento(Action):
    def name(self) -> Text:
        return "action_calcular_descuento"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Ejemplo de cálculo de descuento
        precio_base = 850000  # Precio ejemplo

        mensaje = "💰 **DESCUENTOS DISPONIBLES**\n\n"
        mensaje += f"Precio base: ${precio_base:,}\n\n"

        for tipo_descuento, porcentaje in DESCUENTOS.items():
            descuento = precio_base * porcentaje
            precio_final = precio_base - descuento

            if tipo_descuento == "fenalco_afiliado":
                mensaje += f"🏢 **Empresas afiliadas a Fenalco:** {porcentaje*100}%\n"
            else:
                mensaje += f"👥 **Grupos de 3+ personas:** {porcentaje*100}%\n"

            mensaje += f"   Descuento: ${descuento:,}\n"
            mensaje += f"   Precio final: ${precio_final:,}\n\n"

        mensaje += "¿Calificas para algún descuento?"
        dispatcher.utter_message(text=mensaje)

        return []

class ActionVerificarDisponibilidad(Action):
    def name(self) -> Text:
        return "action_verificar_disponibilidad"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Verificar disponibilidad de programas
        programas_disponibles = []

        for categoria, programas in PROGRAMAS_DB.items():
            for programa in programas:
                if programa["disponible"]:
                    programas_disponibles.append({
                        "categoria": categoria,
                        "nombre": programa["nombre"],
                        "modalidad": programa["modalidad"]
                    })

        mensaje = "✅ **PROGRAMAS DISPONIBLES ACTUALMENTE**\n\n"

        categoria_actual = ""
        for programa in programas_disponibles:
            if programa["categoria"] != categoria_actual:
                categoria_actual = programa["categoria"]
                mensaje += f"**{categoria_actual.upper()}:**\n"

            mensaje += f"• {programa['nombre']} ({', '.join(programa['modalidad'])})\n"

        mensaje += "\n¿En cuál te gustaría inscribirte?"
        dispatcher.utter_message(text=mensaje)

        return []

class ActionGenerarCotizacion(Action):
    def name(self) -> Text:
        return "action_generar_cotizacion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Generar cotización personalizada
        fecha_actual = datetime.now().strftime("%d/%m/%Y")

        mensaje = f"📋 **COTIZACIÓN FENALCO SANTANDER**\n"
        mensaje += f"Fecha: {fecha_actual}\n\n"

        mensaje += "**PROGRAMAS SELECCIONADOS:**\n"
        mensaje += "• Diplomado en Gestión Comercial: $850.000\n"
        mensaje += "• Descuento empresas afiliadas (15%): -$127.500\n"
        mensaje += "• **TOTAL: $722.500**\n\n"

        mensaje += "**INCLUYE:**\n"
        mensaje += "✅ Material didáctico\n"
        mensaje += "✅ Certificado oficial\n"
        mensaje += "✅ Acceso plataforma virtual\n"
        mensaje += "✅ Soporte académico\n\n"

        mensaje += "**CONTACTO:**\n"
        mensaje += "📞 (607) 697-5555\n"
        mensaje += "📧 formacion@fenalcosantander.com\n\n"

        mensaje += "¿Te gustaría proceder con la inscripción?"

        dispatcher.utter_message(text=mensaje)

        return []

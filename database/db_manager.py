import pymongo
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@localhost:27017/fenalco_chatbot?authSource=admin')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client.fenalco_chatbot
        self.cursos_collection = self.db.cursos
        self.usuarios_collection = self.db.usuarios
        self.conversaciones_collection = self.db.conversaciones
        
        # Crear índices
        self.create_indexes()
    
    def create_indexes(self):
        """Crear índices para optimizar búsquedas"""
        try:
            # Índices para cursos
            self.cursos_collection.create_index([("title", "text"), ("description", "text"), ("curriculum", "text")])
            self.cursos_collection.create_index("url")
            self.cursos_collection.create_index("modality")
            self.cursos_collection.create_index("price")
            
            # Índices para usuarios
            self.usuarios_collection.create_index("user_id")
            
            # Índices para conversaciones
            self.conversaciones_collection.create_index("user_id")
            self.conversaciones_collection.create_index("timestamp")
            
            logger.info("Índices creados correctamente")
        except Exception as e:
            logger.error(f"Error creando índices: {e}")
    
    def search_courses(self, query: str, filters: Dict = None) -> List[Dict]:
        """Buscar cursos por texto y filtros"""
        try:
            search_query = {}
            
            # Búsqueda por texto
            if query:
                search_query["$text"] = {"$search": query}
            
            # Aplicar filtros
            if filters:
                if filters.get('modality'):
                    search_query["modality"] = {"$regex": filters['modality'], "$options": "i"}
                
                if filters.get('price_range'):
                    # Implementar lógica de rango de precios
                    pass
                
                if filters.get('duration'):
                    search_query["duration"] = {"$regex": filters['duration'], "$options": "i"}
            
            # Ejecutar búsqueda
            cursor = self.cursos_collection.find(search_query)
            
            # Si hay búsqueda por texto, ordenar por relevancia
            if query:
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
            
            results = list(cursor.limit(10))
            
            # Limpiar ObjectId para serialización
            for result in results:
                result['_id'] = str(result['_id'])
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda de cursos: {e}")
            return []
    
    def get_course_by_title(self, title: str) -> Optional[Dict]:
        """Obtener curso por título exacto"""
        try:
            course = self.cursos_collection.find_one({"title": {"$regex": f"^{re.escape(title)}$", "$options": "i"}})
            if course:
                course['_id'] = str(course['_id'])
            return course
        except Exception as e:
            logger.error(f"Error obteniendo curso por título: {e}")
            return None
    
    def get_courses_by_modality(self, modality: str) -> List[Dict]:
        """Obtener cursos por modalidad"""
        try:
            courses = list(self.cursos_collection.find({"modality": {"$regex": modality, "$options": "i"}}).limit(10))
            for course in courses:
                course['_id'] = str(course['_id'])
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo cursos por modalidad: {e}")
            return []
    
    def get_courses_by_category(self, category: str) -> List[Dict]:
        """Obtener cursos por categoría"""
        try:
            search_query = {
                "$or": [
                    {"title": {"$regex": category, "$options": "i"}},
                    {"description": {"$regex": category, "$options": "i"}},
                    {"curriculum": {"$regex": category, "$options": "i"}}
                ]
            }
            courses = list(self.cursos_collection.find(search_query).limit(10))
            for course in courses:
                course['_id'] = str(course['_id'])
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo cursos por categoría: {e}")
            return []
    
    def get_all_courses(self) -> List[Dict]:
        """Obtener todos los cursos"""
        try:
            courses = list(self.cursos_collection.find().limit(50))
            for course in courses:
                course['_id'] = str(course['_id'])
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo todos los cursos: {e}")
            return []
    
    def get_recent_courses(self, days: int = 30) -> List[Dict]:
        """Obtener cursos agregados recientemente"""
        try:
            fecha_limite = datetime.now() - timedelta(days=days)
            courses = list(self.cursos_collection.find(
                {"created_at": {"$gte": fecha_limite}}
            ).sort("created_at", -1).limit(10))
            
            for course in courses:
                course['_id'] = str(course['_id'])
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo cursos recientes: {e}")
            return []
    
    def get_popular_courses(self) -> List[Dict]:
        """Obtener cursos populares (basado en consultas)"""
        try:
            # Por ahora retorna cursos aleatorios, se puede mejorar con analytics
            courses = list(self.cursos_collection.aggregate([
                {"$sample": {"size": 10}}
            ]))
            
            for course in courses:
                course['_id'] = str(course['_id'])
            return courses
        except Exception as e:
            logger.error(f"Error obteniendo cursos populares: {e}")
            return []
    
    def save_user_interaction(self, user_id: str, intent: str, entities: Dict, response: str):
        """Guardar interacción del usuario para analytics"""
        try:
            interaction = {
                "user_id": user_id,
                "intent": intent,
                "entities": entities,
                "response": response,
                "timestamp": datetime.now()
            }
            self.conversaciones_collection.insert_one(interaction)
        except Exception as e:
            logger.error(f"Error guardando interacción: {e}")
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Obtener preferencias del usuario"""
        try:
            user = self.usuarios_collection.find_one({"user_id": user_id})
            return user.get("preferences", {}) if user else {}
        except Exception as e:
            logger.error(f"Error obteniendo preferencias del usuario: {e}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Actualizar preferencias del usuario"""
        try:
            self.usuarios_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "preferences": preferences,
                        "updated_at": datetime.now()
                    },
                    "$setOnInsert": {"created_at": datetime.now()}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error actualizando preferencias del usuario: {e}")
    
    def get_course_stats(self) -> Dict:
        """Obtener estadísticas de los cursos"""
        try:
            stats = {}
            
            # Total de cursos
            stats['total_courses'] = self.cursos_collection.count_documents({})
            
            # Cursos por modalidad
            modalidades = self.cursos_collection.aggregate([
                {"$group": {"_id": "$modality", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ])
            stats['por_modalidad'] = list(modalidades)
            
            # Cursos agregados en los últimos 30 días
            fecha_limite = datetime.now() - timedelta(days=30)
            stats['nuevos_30_dias'] = self.cursos_collection.count_documents(
                {"created_at": {"$gte": fecha_limite}}
            )
            
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def health_check(self) -> bool:
        """Verificar conexión a la base de datos"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return False
    
    def close_connection(self):
        """Cerrar conexión a la base de datos"""
        try:
            self.client.close()
        except Exception as e:
            logger.error(f"Error cerrando conexión: {e}")

# Instancia global del manager
db_manager = DatabaseManager()
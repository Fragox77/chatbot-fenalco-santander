import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import json
import re
from datetime import datetime
import pymongo
import os
from urllib.parse import urljoin, urlparse
import logging
import schedule

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FenalcoScraper:
    def __init__(self):
        self.base_url = "https://www.formacionfenalcosantander.com/"
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@localhost:27017/fenalco_chatbot?authSource=admin')
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client.fenalco_chatbot
        self.collection = self.db.cursos
        
        # Configurar Chrome
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
    def get_driver(self):
        """Inicializar el driver de Chrome"""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Error al inicializar el driver: {e}")
            return None
    
    def scrape_course_list(self):
        """Extraer lista de cursos de la página principal"""
        driver = self.get_driver()
        if not driver:
            return []
        
        courses = []
        try:
            driver.get(self.base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "course-item"))
            )
            
            # Buscar elementos de cursos
            course_elements = driver.find_elements(By.CSS_SELECTOR, ".course-item, .program-card, .training-card")
            
            for element in course_elements:
                try:
                    course_data = self.extract_course_basic_info(element)
                    if course_data:
                        courses.append(course_data)
                except Exception as e:
                    logger.warning(f"Error extrayendo curso: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error en scrape_course_list: {e}")
        finally:
            driver.quit()
            
        return courses
    
    def extract_course_basic_info(self, element):
        """Extraer información básica de un curso"""
        try:
            # Título
            title_element = element.find_element(By.CSS_SELECTOR, "h3, h2, .course-title, .program-title")
            title = title_element.text.strip() if title_element else "Sin título"
            
            # URL
            link_element = element.find_element(By.CSS_SELECTOR, "a")
            url = link_element.get_attribute("href") if link_element else None
            
            # Descripción corta
            desc_element = element.find_elements(By.CSS_SELECTOR, ".course-description, .program-description, p")
            description = desc_element[0].text.strip() if desc_element else ""
            
            # Precio
            price_element = element.find_elements(By.CSS_SELECTOR, ".price, .cost, .precio")
            price = price_element[0].text.strip() if price_element else ""
            
            # Modalidad
            modality_element = element.find_elements(By.CSS_SELECTOR, ".modalidad, .modality, .format")
            modality = modality_element[0].text.strip() if modality_element else ""
            
            return {
                'title': title,
                'url': urljoin(self.base_url, url) if url else None,
                'description': description,
                'price': price,
                'modality': modality,
                'scraped_at': datetime.now()
            }
            
        except Exception as e:
            logger.warning(f"Error extrayendo información básica: {e}")
            return None
    
    def scrape_course_details(self, course_url):
        """Extraer detalles completos de un curso específico"""
        driver = self.get_driver()
        if not driver:
            return {}
        
        details = {}
        try:
            driver.get(course_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Título completo
            title_selectors = ["h1", ".course-title", ".program-title", ".page-title"]
            for selector in title_selectors:
                try:
                    title_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['title'] = title_element.text.strip()
                    break
                except:
                    continue
            
            # Descripción completa
            desc_selectors = [".course-description", ".program-content", ".description", ".content"]
            for selector in desc_selectors:
                try:
                    desc_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if desc_elements:
                        details['description'] = "\n".join([elem.text.strip() for elem in desc_elements])
                        break
                except:
                    continue
            
            # Objetivos
            obj_selectors = [".objectives", ".objetivos", ".goals"]
            for selector in obj_selectors:
                try:
                    obj_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['objectives'] = obj_element.text.strip()
                    break
                except:
                    continue
            
            # Dirigido a
            target_selectors = [".dirigido-a", ".target-audience", ".audience"]
            for selector in target_selectors:
                try:
                    target_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['target_audience'] = target_element.text.strip()
                    break
                except:
                    continue
            
            # Duración
            duration_selectors = [".duration", ".duracion", ".tiempo"]
            for selector in duration_selectors:
                try:
                    duration_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['duration'] = duration_element.text.strip()
                    break
                except:
                    continue
            
            # Precio
            price_selectors = [".price", ".precio", ".cost", ".costo"]
            for selector in price_selectors:
                try:
                    price_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['price'] = price_element.text.strip()
                    break
                except:
                    continue
            
            # Modalidad
            modality_selectors = [".modalidad", ".modality", ".format"]
            for selector in modality_selectors:
                try:
                    modality_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['modality'] = modality_element.text.strip()
                    break
                except:
                    continue
            
            # Fechas
            dates_selectors = [".fechas", ".dates", ".schedule"]
            for selector in dates_selectors:
                try:
                    dates_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['dates'] = dates_element.text.strip()
                    break
                except:
                    continue
            
            # Certificación
            cert_selectors = [".certificacion", ".certification", ".certificate"]
            for selector in cert_selectors:
                try:
                    cert_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['certification'] = cert_element.text.strip()
                    break
                except:
                    continue
            
            # Metodología
            methodology_selectors = [".metodologia", ".methodology", ".approach"]
            for selector in methodology_selectors:
                try:
                    methodology_element = driver.find_element(By.CSS_SELECTOR, selector)
                    details['methodology'] = methodology_element.text.strip()
                    break
                except:
                    continue
            
            # Contenido/Temario
            content_selectors = [".temario", ".curriculum", ".content", ".syllabus"]
            for selector in content_selectors:
                try:
                    content_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if content_elements:
                        details['curriculum'] = "\n".join([elem.text.strip() for elem in content_elements])
                        break
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles del curso {course_url}: {e}")
        finally:
            driver.quit()
        
        return details
    
    def save_to_database(self, course_data):
        """Guardar datos del curso en MongoDB"""
        try:
            # Verificar si el curso ya existe
            existing = self.collection.find_one({"url": course_data.get("url")})
            
            if existing:
                # Actualizar curso existente
                self.collection.update_one(
                    {"url": course_data.get("url")},
                    {"$set": {**course_data, "updated_at": datetime.now()}}
                )
                logger.info(f"Curso actualizado: {course_data.get('title', 'Sin título')}")
            else:
                # Insertar nuevo curso
                course_data["created_at"] = datetime.now()
                course_data["updated_at"] = datetime.now()
                self.collection.insert_one(course_data)
                logger.info(f"Nuevo curso guardado: {course_data.get('title', 'Sin título')}")
                
        except Exception as e:
            logger.error(f"Error guardando en base de datos: {e}")
    
    def full_scrape(self):
        """Ejecutar scraping completo"""
        logger.info("Iniciando scraping completo de Fenalco Santander")
        
        # Obtener lista de cursos
        courses = self.scrape_course_list()
        logger.info(f"Encontrados {len(courses)} cursos")
        
        # Extraer detalles de cada curso
        for i, course in enumerate(courses):
            if course.get('url'):
                logger.info(f"Procesando curso {i+1}/{len(courses)}: {course.get('title')}")
                details = self.scrape_course_details(course['url'])
                
                # Combinar información básica con detalles
                complete_course = {**course, **details}
                
                # Guardar en base de datos
                self.save_to_database(complete_course)
                
                # Pausa entre requests
                time.sleep(2)
        
        logger.info("Scraping completo terminado")
    
    def update_scrape(self):
        """Actualizar información existente"""
        logger.info("Ejecutando actualización de datos")
        self.full_scrape()

def run_scraper():
    """Función para ejecutar el scraper"""
    scraper = FenalcoScraper()
    scraper.full_scrape()

if __name__ == "__main__":
    # Programar ejecuciones
    schedule.every().day.at("02:00").do(run_scraper)  # Ejecutar diariamente a las 2 AM
    schedule.every().monday.at("06:00").do(run_scraper)  # Ejecutar los lunes a las 6 AM
    
    # Ejecutar una vez al inicio
    run_scraper()
    
    # Mantener el script corriendo
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto
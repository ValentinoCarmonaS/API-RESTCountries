#!/usr/bin/env python3
"""
Script de inicialización de la base de datos
Ejecuta la creación de tablas y opcionalmente carga datos iniciales
"""

import logging
from models import create_database, get_session, Country, Language
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Inicializa la base de datos creando las tablas"""
    try:
        logger.info("Iniciando creación de base de datos...")
        create_database()
        return True
    except Exception as e:
        logger.error(f"❌ Error creando base de datos")
        return False

def check_data_exists():
    """Verifica si ya existen datos en la base de datos"""
    try:
        db = get_session()
        count = db.query(Country).count()
        db.close()
        return count > 0
    except Exception as e:
        logger.error(f"Error verificando datos existentes")
        return False

def consume_restcountries_api():
    # Consumir API
    url = "https://restcountries.com/v3.1/all?fields=name,region,population,area,languages,capital,subregion,cca3"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

def parse_country(country_data):
    name = country_data.get("name", {}).get("common", "Unknown")
    region = country_data.get("region", "Unknown")
    population = country_data.get("population", 0)
    area = country_data.get("area")
    alpha3_code = country_data.get("cca3")
    
    capital_list = country_data.get("capital", [])
    capital = capital_list[0] if capital_list else None
    subregion = country_data.get("subregion")
    
    # Crear país
    return Country(
        name=name,
        region=region,
        population=population,
        area=area,
        alpha3_code=alpha3_code,
        capital=capital,
        subregion=subregion
    )

def parse_language(country_data, country: Country, language_cache, db):
    languages_data = country_data.get("languages", {})
    for iso_code, lang_name in languages_data.items():
        if iso_code in language_cache:
            language = language_cache[iso_code]
        else:
            language = db.query(Language).filter(Language.iso639_1 == iso_code).first()
            if not language:
                language = Language(
                    iso639_1=iso_code,
                    name=lang_name,
                    native_name=lang_name
                )
                db.add(language)
            language_cache[iso_code] = language
        
        country.languages.append(language)

def parse_all_data(countries_data, db):
    loaded_countries = 0
    language_cache = {}  # Cache para evitar duplicados

    for country_data in countries_data:
        try:
            country = parse_country(country_data)   
            parse_language(country_data, country, language_cache, db)

            db.add(country)
            loaded_countries += 1

            # Commit cada 50 países para evitar transacciones muy grandes
            if loaded_countries % 50 == 0:
                db.commit()
                logger.info(f"Procesados {loaded_countries} países...")

        except Exception as e:
            logger.warning(f"Error procesando país {country_data.get('name', 'Unknown')}")
            continue

def load_from_restcountries():
    """Carga datos reales desde la API de RESTCountries"""
    try:
        db = get_session()

        countries_data = consume_restcountries_api()        
        parse_all_data(countries_data, db)
        
        # Commit final
        db.commit()      
        db.close()
        
    except requests.RequestException as e:
        logger.error(f"❌ Error conectando con RESTCountries API: {e}")
    except Exception as e:
        logger.error(f"❌ Error cargando datos desde API: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

def main():
    """Función principal de inicialización"""
    logger.info("=== Inicialización de Base de Datos ===")
    
    # 1. Crear estructura de DB
    if not init_database():
        logger.error("❌ Falló la inicialización de la base de datos")
        return False
    
    # 2. Verificar si necesitamos cargar datos
    if check_data_exists():
        logger.info("✅ La base de datos ya contiene datos")
        logger.info("Saliendo sin cargar datos")
    else:
        logger.info("Cargando datos en la base de datos")
        load_from_restcountries()

    

if __name__ == "__main__":
    success = main()
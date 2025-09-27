from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
import logging
import uvicorn
import init_db

from models import Country, get_session, create_database

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Countries API",
    description="API que consume datos de RESTCountries y los persiste localmente",
    version="1.0.0"
)

# Dependency para obtener la sesión de DB
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "Countries API",
        "version": "1.0.0",
        "endpoints": {
            "countries": "/countries?region={region}",
            "countries_stats": "/countries/stats?metric={metric}",
        }
    }

# =============================================================================
#                      Filter countries by region
# =============================================================================

@app.get("/countries")
async def get_countries(
    region: Optional[str] = Query(None, description="Filtrar por región"),
    db: Session = Depends(get_db)
):
    """
    Devuelve países filtrados por región (consulta a DB local).
    Implementa paginación para manejar grandes volúmenes de datos.
    """
    try:
        query = db.query(Country)
        
        # Filtrar por región si se especifica
        if region:
            query = query.filter(Country.region.ilike(f"%{region}%"))
        
        countries = query.all()
                
        if not countries:
            if region:
                raise HTTPException(status_code=404, detail=f"No se encontraron países en la región: {region}")
            else:
                raise HTTPException(status_code=404, detail="No se encontraron países")
        
        return {
            "countries": [country.to_dict() for country in countries],
            "filters": {
                "region": region
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo países")
        raise HTTPException(status_code=500, detail=f"Error interno")

# =============================================================================
#                           Get statistics
# =============================================================================

def get_countries_stats_population(db, region):
    # Estadísticas de población por región
    stats = db.query(
        Country.region,
        func.avg(Country.population).label('avg_population'),
        func.sum(Country.population).label('total_population'),
        func.min(Country.population).label('min_population'),
        func.max(Country.population).label('max_population'),
        func.count(Country.country_id).label('countries_count')
    ).group_by(Country.region)
    
    if region:
        stats = stats.filter(Country.region.ilike(f"%{region}%"))
    
    results = stats.all()
    
    return {
        "metric": "population",
        "region_filter": region,
        "statistics": [
            {
                "region": stat.region,
                "average_population": int(stat.avg_population) if stat.avg_population else 0,
                "total_population": int(stat.total_population) if stat.total_population else 0,
                "min_population": int(stat.min_population) if stat.min_population else 0,
                "max_population": int(stat.max_population) if stat.max_population else 0,
                "countries_count": stat.countries_count
            } for stat in results
        ]
    }

def get_countries_stats_area(db, region):
    # Estadísticas de área por región
    stats = db.query(
        Country.region,
        func.avg(Country.area).label('avg_area'),
        func.sum(Country.area).label('total_area'),
        func.min(Country.area).label('min_area'),
        func.max(Country.area).label('max_area')
    ).filter(Country.area.isnot(None)).group_by(Country.region)
    
    if region:
        stats = stats.filter(Country.region.ilike(f"%{region}%"))
    
    results = stats.all()
    
    return {
        "metric": "area",
        "region_filter": region,
        "statistics": [
            {
                "region": stat.region,
                "average_area": float(stat.avg_area) if stat.avg_area else 0,
                "total_area": float(stat.total_area) if stat.total_area else 0,
                "min_area": float(stat.min_area) if stat.min_area else 0,
                "max_area": float(stat.max_area) if stat.max_area else 0
            } for stat in results
        ]
    }

def get_countries_stats_per_region(db, region):
    # Conteo de países por región
    stats = db.query(
        Country.region,
        func.count(Country.country_id).label('countries_count')
    ).group_by(Country.region).order_by(desc('countries_count'))
    
    if region:
        stats = stats.filter(Country.region.ilike(f"%{region}%"))
    
    results = stats.all()
    
    return {
        "metric": "countries_per_region",
        "region_filter": region,
        "statistics": [
            {
                "region": stat.region,
                "countries_count": stat.countries_count
            } for stat in results
        ]
    }

@app.get("/countries/stats")
async def get_countries_stats(
    metric: str = Query(..., description="Métrica a calcular: population, area, countries_per_region"),
    region: Optional[str] = Query(None, description="Filtrar por región específica"),
    db: Session = Depends(get_db)
):
    """
    Devuelve estadísticas calculadas sobre los países.
    Soporta métricas: population, area, countries_per_region
    """
    try:
        base_query = db.query(Country)
        
        # Filtrar por región si se especifica
        if region:
            base_query = base_query.filter(Country.region.ilike(f"%{region}%"))
        
        if metric == "population":
            get_countries_stats_population(db, region)
            
        elif metric == "area":
            get_countries_stats_area(db, region)
            
        elif metric == "countries_per_region":
            get_countries_stats_per_region(db, region)
        
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Métrica no soportada: {metric}. Use: population, area, countries_per_region"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculando estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno")

if __name__ == "__main__":
    init_db.main()
    uvicorn.run(app, host="localhost", port=8000)
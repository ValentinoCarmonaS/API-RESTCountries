from sqlalchemy import Column, Integer, String, BigInteger, Float, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

# Tabla de relación muchos a muchos entre Country y Language
country_language = Table(
    'country_language',
    Base.metadata,
    Column('country_id', Integer, ForeignKey('countries.country_id'), primary_key=True),
    Column('language_id', Integer, ForeignKey('languages.language_id'), primary_key=True)
)

class Country(Base):
    __tablename__ = 'countries'
    
    country_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    population = Column(BigInteger, nullable=False)
    area = Column(Float)
    alpha3_code = Column(String(3), unique=True)
    capital = Column(String)
    subregion = Column(String)
    
    # Relación muchos a muchos con Language
    languages = relationship("Language", secondary=country_language, back_populates="countries")
    
    def to_dict(self):
        return {
            "country_id": self.country_id,
            "name": self.name,
            "region": self.region,
            "population": self.population,
            "area": self.area,
            "alpha3_code": self.alpha3_code,
            "capital": self.capital,
            "subregion": self.subregion,
            "languages": [lang.to_dict() for lang in self.languages]
        }

class Language(Base):
    __tablename__ = 'languages'
    
    language_id = Column(Integer, primary_key=True, autoincrement=True)
    iso639_1 = Column(String(3), unique=True, nullable=False)
    name = Column(String, nullable=False)
    native_name = Column(String)
    
    # Relación muchos a muchos con Country
    countries = relationship("Country", secondary=country_language, back_populates="languages")
    
    def to_dict(self):
        return {
            "language_id": self.language_id,
            "iso639_1": self.iso639_1,
            "name": self.name,
            "native_name": self.native_name
        }

def create_database():
    engine = create_engine("sqlite:///./countries.db", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session():
    engine = create_database()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
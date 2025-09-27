import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Base, Country, Language

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db_isolated.db" # Use a different file for isolation
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Pytest Fixture for DB ---
@pytest.fixture(scope="function")
def db_session():
    """Fixture to set up and tear down the test database for each test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback() # Rollback any lingering transactions
        db.close()
        Base.metadata.drop_all(bind=engine)


# --- Test Class for Database Models ---

class TestDatabaseModels:

    def test_create_country(self, db_session):
        """Tests the creation of a single Country object."""
        country = Country(
            name="Testland",
            region="Test Region",
            population=1000,
            area=500.0,
            alpha3_code="TST",
            capital="Testville"
        )
        db_session.add(country)
        db_session.commit()

        retrieved_country = db_session.query(Country).filter_by(name="Testland").first()
        assert retrieved_country is not None
        assert retrieved_country.name == "Testland"
        assert retrieved_country.population == 1000
        assert retrieved_country.alpha3_code == "TST"


    def test_create_language(self, db_session):
        """Tests the creation of a single Language object."""
        language = Language(iso639_1="tl", name="Test Language", native_name="Test Lingo")
        db_session.add(language)
        db_session.commit()

        retrieved_language = db_session.query(Language).filter_by(name="Test Language").first()
        assert retrieved_language is not None
        assert retrieved_language.iso639_1 == "tl"

    def test_many_to_many_relationship(self, db_session):
        """Tests the many-to-many relationship between Country and Language."""
        # Create entities
        country1 = Country(name="Country A", region="A", population=1)
        country2 = Country(name="Country B", region="B", population=2)
        lang1 = Language(iso639_1="l1", name="Lang 1")
        lang2 = Language(iso639_1="l2", name="Lang 2")

        # Assign relationships
        country1.languages.append(lang1)
        country1.languages.append(lang2)
        country2.languages.append(lang1)

        db_session.add_all([country1, country2, lang1, lang2])
        db_session.commit()

        # Verify relationships
        retrieved_country1 = db_session.query(Country).filter_by(name="Country A").one()
        retrieved_lang1 = db_session.query(Language).filter_by(name="Lang 1").one()

        assert len(retrieved_country1.languages) == 2
        assert retrieved_lang1 in retrieved_country1.languages

        assert len(retrieved_lang1.countries) == 2
        assert retrieved_country1 in retrieved_lang1.countries
        assert retrieved_country1.languages[0].name == "Lang 1"

    def test_country_name_not_nullable(self, db_session):
        """Tests that the Country name cannot be null."""
        with pytest.raises(IntegrityError):
            country = Country(name=None, region="Test Region", population=100)
            db_session.add(country)
            db_session.commit()

    def test_language_iso_code_unique(self, db_session):
        """Tests that the Language iso639_1 code must be unique."""
        with pytest.raises(IntegrityError):
            lang1 = Language(iso639_1="l1", name="Lang 1")
            lang2 = Language(iso639_1="l1", name="Lang 2")
            db_session.add_all([lang1, lang2])
            db_session.commit()

    def test_to_dict_method(self):
        """Tests the to_dict method of the models."""
        lang = Language(iso639_1="tl", name="Test Language")
        country = Country(name="Testland", region="Test Region", population=1000)
        country.languages.append(lang)

        country_dict = country.to_dict()
        assert country_dict["name"] == "Testland"
        assert "languages" in country_dict
        assert len(country_dict["languages"]) == 1
        assert country_dict["languages"][0]["name"] == "Test Language"

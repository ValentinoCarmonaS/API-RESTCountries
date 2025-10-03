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
        country1 = Country(name="Country A", region="A", population=1, alpha3_code="C1A")
        country2 = Country(name="Country B", region="B", population=2, alpha3_code="C2B")
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

    def test_country_region_not_nullable(self, db_session):
        """Tests that the Country.region cannot be null."""
        with pytest.raises(IntegrityError):
            country = Country(name="NoRegionLand", region=None, population=100)
            db_session.add(country)
            db_session.commit()

    def test_country_population_not_nullable(self, db_session):
        """Tests that the Country.population cannot be null."""
        with pytest.raises(IntegrityError):
            country = Country(name="NoPopLand", region="Test Region", population=None)
            db_session.add(country)
            db_session.commit()

    def test_country_alpha3_code_unique(self, db_session):
        """Tests that the Country.alpha3_code must be unique."""
        with pytest.raises(IntegrityError):
            country1 = Country(name="Country A", region="A", population=1, alpha3_code="AAA")
            country2 = Country(name="Country B", region="B", population=2, alpha3_code="AAA")
            db_session.add_all([country1, country2])
            db_session.commit()

    def test_create_country_with_null_optional_fields(self, db_session):
        """Tests creating a Country with nullable fields set to None."""
        country = Country(
            name="OptionalLand",
            region="Test Region",
            population=500,
            area=None,
            capital=None
        )
        db_session.add(country)
        db_session.commit()

        retrieved = db_session.query(Country).filter_by(name="OptionalLand").one()
        assert retrieved is not None
        assert retrieved.area is None
        assert retrieved.capital is None

    def test_language_name_not_nullable(self, db_session):
        """Tests that the Language.name cannot be null."""
        with pytest.raises(IntegrityError):
            lang = Language(iso639_1="nl", name=None)
            db_session.add(lang)
            db_session.commit()

    def test_country_to_dict_with_no_languages(self, db_session):
        """Tests the to_dict method on a Country with no associated languages."""
        country = Country(name="NoLangLand", region="Test", population=10)
        db_session.add(country)
        db_session.commit()

        country_dict = country.to_dict()
        assert country_dict["name"] == "NoLangLand"
        assert "languages" in country_dict
        assert isinstance(country_dict["languages"], list)
        assert len(country_dict["languages"]) == 0

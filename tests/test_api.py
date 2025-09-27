import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

# --- TestClient Instance ---
client = TestClient(app)


# --- Test Classes ---
class TestRootEndpoint:
    def test_root(self):
        """Tests the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Countries API"
        assert "endpoints" in data

class TestCountriesEndpoint:
    def test_get_all_countries(self):
        """Tests fetching all countries without filters."""
        response = client.get("/countries")
        assert response.status_code == 200
        data = response.json()
        assert "countries" in data
        assert len(data["countries"]) == 250

    def test_filter_by_region_success(self):
        """Tests filtering countries by an existing region."""
        response = client.get("/countries?region=Americas")
        assert response.status_code == 200
        data = response.json()
        assert len(data["countries"]) == 56
        assert data["countries"][0]["region"] == "Americas"
        assert data["countries"][55]["region"] == "Americas"

    def test_filter_by_nonexistent_region(self):
        """Tests filtering by a region that does not exist."""
        response = client.get("/countries?region=Atlantis")
        assert response.status_code == 404
        assert "No se encontraron países en la región: Atlantis" in response.json()["detail"]


class TestStatsEndpoint:
    def test_stats_population(self):
        """Tests population statistics."""
        response = client.get("/countries/stats?metric=population")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "population"
        assert "statistics" in data

    def test_stats_area(self):
        """Tests area statistics."""
        response = client.get("/countries/stats?metric=area")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "area"
        assert "statistics" in data

    def test_stats_countries_per_region(self):
        """Tests countries per region statistics."""
        response = client.get("/countries/stats?metric=countries_per_region")
        assert response.status_code == 200
        data = response.json()
        assert data["metric"] == "countries_per_region"
        assert "statistics" in data

    def test_stats_invalid_metric(self):
        """Tests an invalid metric for statistics."""
        response = client.get("/countries/stats?metric=gdp")
        assert response.status_code == 400
        assert "Métrica no soportada: gdp" in response.json()["detail"]

    def test_stats_with_region_filter(self):
        """Tests statistics filtered by a specific region."""
        response = client.get("/countries/stats?metric=population&region=Europe")
        assert response.status_code == 200
        data = response.json()
        assert data["region_filter"] == "Europe"
        assert len(data["statistics"]) == 1
        assert data["statistics"][0]["region"] == "Europe"

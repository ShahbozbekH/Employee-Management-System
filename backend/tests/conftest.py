import os
import sys
import pymongo
import dotenv
import pathlib

import pytest

@pytest.fixture(autouse=True)
def clear_employees_collection():
    # Load .env to get DB connection
    dotenv.load_dotenv(dotenv.find_dotenv(str(pathlib.Path(__file__).parent.parent / ".env")))
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    db["employees"].delete_many({})
    yield
    db["employees"].delete_many({})
import pytest


def pytest_addoption(parser):
    parser.addoption("--employee_id", action="store", default="E001", help="Employee ID for testing")
    parser.addoption("--name", action="store", default="John Doe", help="Employee name for testing")
    parser.addoption("--email", action="store", default="john.doe@example.com", help="Employee email for testing")
    parser.addoption("--department", action="store", default="Engineering", help="Employee department for testing")
    parser.addoption("--position", action="store", default="Software Engineer", help="Employee position for testing")
    parser.addoption("--status", action="store", default="Active", help="Employee status for testing")


@pytest.fixture
def employee_data(request):
    return {
        "employee_id": request.config.getoption("--employee_id"),
        "name": request.config.getoption("--name"),
        "email": request.config.getoption("--email"),
        "department": request.config.getoption("--department"),
        "position": request.config.getoption("--position"),
        "status": request.config.getoption("--status")
    }


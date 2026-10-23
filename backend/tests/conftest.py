import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.entities import User, UserRole, Property

TEST_DB_FILE = Path(__file__).resolve().parent / "test_staynearby.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_FILE}"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def init_db():
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_FILE.exists():
        try:
            TEST_DB_FILE.unlink()
        except Exception:
            pass

@pytest.fixture(scope="session")
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def sample_users():
    session = TestingSessionLocal()
    renter = User(
        name="Test Renter",
        email="testrenter@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.RENTER.value,
        preferred_budget=500.0,
        preferred_amenities=["wifi", "air_conditioning"],
    )
    host = User(
        name="Test Host",
        email="testhost@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.HOST.value,
    )
    admin = User(
        name="Test Admin",
        email="testadmin@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMIN.value,
    )
    session.add_all([renter, host, admin])
    session.commit()
    session.refresh(renter)
    session.refresh(host)
    session.refresh(admin)
    users = {"renter": renter, "host": host, "admin": admin}
    session.close()
    return users

@pytest.fixture(scope="session")
def renter_token(sample_users):
    return create_access_token(subject=sample_users["renter"].id, role=sample_users["renter"].role)

@pytest.fixture(scope="session")
def host_token(sample_users):
    return create_access_token(subject=sample_users["host"].id, role=sample_users["host"].role)

@pytest.fixture(scope="session")
def admin_token(sample_users):
    return create_access_token(subject=sample_users["admin"].id, role=sample_users["admin"].role)

@pytest.fixture(scope="session")
def sample_property(sample_users):
    session = TestingSessionLocal()
    prop = Property(
        host_id=sample_users["host"].id,
        title="Test Work Studio",
        description="A quiet workspace in Guindy.",
        property_type="workspace_studio",
        neighbourhood="Guindy",
        latitude=13.0067,
        longitude=80.2025,
        public_location_description="Near Guindy Metro",
        exact_address="123 Test St, Guindy, Chennai",
        price_per_hour=300.0,
        price_per_half_day=1200.0,
        price_per_day=2200.0,
        maximum_guests=2,
        amenities=["wifi", "air_conditioning", "work_desk"],
        supported_durations=["hourly", "half_day", "full_day"],
        active=True,
    )
    session.add(prop)
    session.commit()
    session.refresh(prop)
    session.close()
    return prop

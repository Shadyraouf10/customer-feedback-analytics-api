from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_feedback_lifecycle_and_analytics():
    created = client.post(
        "/feedback",
        json={
            "customer_name": "Sara Ahmed",
            "text": "The service was excellent and fast",
            "source": "mobile-app",
        },
    )
    assert created.status_code == 201
    feedback = created.json()
    assert feedback["sentiment"] == "positive"

    listed = client.get("/feedback", params={"sentiment": "positive"})
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch(
        f'/feedback/{feedback["id"]}',
        json={"text": "The service was slow and terrible"},
    )
    assert updated.status_code == 200
    assert updated.json()["sentiment"] == "negative"

    summary = client.get("/analytics/summary")
    assert summary.status_code == 200
    assert summary.json()["total_feedback"] == 1
    assert summary.json()["counts"]["negative"] == 1

    deleted = client.delete(f'/feedback/{feedback["id"]}')
    assert deleted.status_code == 204
    assert client.get(f'/feedback/{feedback["id"]}').status_code == 404


def test_validation_rejects_short_feedback():
    response = client.post(
        "/feedback",
        json={"customer_name": "A", "text": "ok", "source": "x"},
    )
    assert response.status_code == 422


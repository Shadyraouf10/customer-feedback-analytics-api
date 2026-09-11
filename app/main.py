from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Feedback
from .schemas import AnalyticsSummary, FeedbackCreate, FeedbackResponse, FeedbackUpdate
from .sentiment import analyze_sentiment


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Customer Feedback Analytics API",
    version="0.1.0",
    description="Collect, manage, filter, and summarize customer feedback.",
    lifespan=lifespan,
)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {"message": "Customer Feedback Analytics API", "docs": "/docs"}


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Feedback"],
)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)) -> Feedback:
    item = Feedback(
        customer_name=payload.customer_name,
        text=payload.text,
        source=payload.source.lower(),
        sentiment=analyze_sentiment(payload.text),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/feedback", response_model=list[FeedbackResponse], tags=["Feedback"])
def list_feedback(
    sentiment: str | None = Query(default=None, pattern="^(positive|negative|neutral)$"),
    source: str | None = Query(default=None, min_length=2, max_length=50),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Feedback]:
    statement = select(Feedback)
    if sentiment:
        statement = statement.where(Feedback.sentiment == sentiment)
    if source:
        statement = statement.where(Feedback.source == source.lower())
    statement = statement.order_by(Feedback.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


@app.get("/feedback/{feedback_id}", response_model=FeedbackResponse, tags=["Feedback"])
def get_feedback(feedback_id: int, db: Session = Depends(get_db)) -> Feedback:
    item = db.get(Feedback, feedback_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return item


@app.patch("/feedback/{feedback_id}", response_model=FeedbackResponse, tags=["Feedback"])
def update_feedback(
    feedback_id: int,
    payload: FeedbackUpdate,
    db: Session = Depends(get_db),
) -> Feedback:
    item = db.get(Feedback, feedback_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Feedback not found")

    changes = payload.model_dump(exclude_unset=True)
    if "source" in changes:
        changes["source"] = changes["source"].lower()
    if "text" in changes:
        changes["sentiment"] = analyze_sentiment(changes["text"])
    for field, value in changes.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@app.delete(
    "/feedback/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Feedback"],
)
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)) -> Response:
    item = db.get(Feedback, feedback_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/analytics/summary", response_model=AnalyticsSummary, tags=["Analytics"])
def analytics_summary(db: Session = Depends(get_db)) -> AnalyticsSummary:
    rows = db.execute(
        select(Feedback.sentiment, func.count(Feedback.id)).group_by(Feedback.sentiment)
    ).all()
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for sentiment, count in rows:
        counts[sentiment] = count

    total = sum(counts.values())
    percentage = lambda value: round((value / total) * 100, 2) if total else 0.0
    return AnalyticsSummary(
        total_feedback=total,
        counts=counts,
        positive_percentage=percentage(counts["positive"]),
        negative_percentage=percentage(counts["negative"]),
        neutral_percentage=percentage(counts["neutral"]),
    )


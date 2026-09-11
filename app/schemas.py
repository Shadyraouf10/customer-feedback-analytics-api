from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    text: str = Field(min_length=3, max_length=2000)
    source: str = Field(default="web", min_length=2, max_length=50)


class FeedbackUpdate(BaseModel):
    customer_name: str | None = Field(default=None, min_length=2, max_length=100)
    text: str | None = Field(default=None, min_length=3, max_length=2000)
    source: str | None = Field(default=None, min_length=2, max_length=50)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    text: str
    source: str
    sentiment: str
    created_at: datetime


class SentimentCounts(BaseModel):
    positive: int
    negative: int
    neutral: int


class AnalyticsSummary(BaseModel):
    total_feedback: int
    counts: SentimentCounts
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float


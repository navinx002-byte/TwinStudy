"""
TwinStudy - Behavioral Modeling Engine & Grades Management Module
Clean SQLAlchemy Models and FastAPI Router Endpoints
Attachable to any Python / FastAPI / SQLite student productivity codebase.
"""

from datetime import datetime, date
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, Session
from fastapi import APIRouter, Depends, HTTPException, status

Base = declarative_base()

# ==============================================================================
# PART 1: DIGITAL TWIN LEARNING ENGINE (MODELS)
# ==============================================================================

class PatternType(str, Enum):
    PRODUCTIVITY = "productivity"
    PRIORITIZATION = "prioritization"
    DEADLINE_HABIT = "deadline_habit"
    FATIGUE = "fatigue"

class BehaviorPattern(Base):
    __tablename__ = "behavior_patterns"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), index=True, default="default_student")
    title = Column(String(200), nullable=False)
    pattern_type = Column(String(50), nullable=False, default=PatternType.PRODUCTIVITY.value)
    confidence = Column(Float, default=75.0)  # 0.0 - 100.0%
    evidence_count = Column(Integer, default=1)
    evidence_summary = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)  # Multiplier (e.g. 1.25)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), index=True, default="default_student")
    timestamp = Column(DateTime, default=datetime.utcnow)
    question = Column(Text, nullable=False)
    recommended_scenario = Column(String(200), nullable=False)
    chosen_scenario = Column(String(200), nullable=False)
    user_reason = Column(Text, nullable=True)
    is_disagreement = Column(Boolean, default=False)
    actual_outcome = Column(Text, nullable=True)
    outcome_rating = Column(Integer, nullable=True)  # 1 to 5 stars
    outcome_feedback = Column(Text, nullable=True)

# ==============================================================================
# PART 2: ACADEMIC GRADES & CGPA TRACKING (MODELS)
# ==============================================================================

class Grade(Base):
    __tablename__ = "grades"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), index=True, default="default_student")
    subject_id = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(100), nullable=False)
    assessment_name = Column(String(100), nullable=False)  # Midterm 1, Quiz 2, Project
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False, default=100.0)
    weight = Column(Float, nullable=False, default=20.0)  # Assessment weight in subject (%)
    grade_letter = Column(String(5), nullable=False)  # A+, A, B+, B, C, D, F
    notes = Column(Text, nullable=True)
    date_recorded = Column(Date, default=date.today)

class SubjectTarget(Base):
    __tablename__ = "subject_targets"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), index=True, default="default_student")
    subject_id = Column(String(50), nullable=False, index=True)
    target_grade = Column(String(5), default="A")

# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class BehaviorPatternSchema(BaseModel):
    id: str
    title: str
    pattern_type: PatternType
    confidence: float
    evidence_count: int
    evidence_summary: Optional[str]
    weight: float
    is_active: bool

    class Config:
        orm_mode = True

class DecisionCreate(BaseModel):
    question: str
    recommended_scenario: str
    chosen_scenario: str
    user_reason: Optional[str] = ""
    is_disagreement: bool = False

class FeedbackCreate(BaseModel):
    decision_id: str
    actual_outcome: str
    outcome_rating: int = Field(ge=1, le=5)
    outcome_feedback: Optional[str] = ""

class TwinHealthMetrics(BaseModel):
    personalization_score: int
    data_coverage: int
    decision_history_count: int
    feedback_received_count: int
    prediction_accuracy: float

class GradeCreate(BaseModel):
    subject_id: str
    subject_name: str
    assessment_name: str
    score: float
    max_score: float
    weight: float = 20.0
    notes: Optional[str] = ""
    date_recorded: Optional[date] = None

class SubjectBreakdown(BaseModel):
    subject_id: str
    subject_name: str
    credits: float
    current_percentage: float
    current_grade: str
    grade_points: float
    target_grade: str
    assessment_count: int

class GradesOverview(BaseModel):
    cgpa_10: float
    cgpa_4: float
    total_credits: float
    subject_breakdown: List[SubjectBreakdown]
    grades: List[dict]
    disclaimer: str = "Grades reflect historical performance and do not predict future outcomes with certainty."

# ==============================================================================
# FASTAPI ROUTERS
# ==============================================================================

twin_router = APIRouter(prefix="/api/twin", tags=["Digital Twin Learning Engine"])
grades_router = APIRouter(prefix="/api/grades", tags=["Academic Grades & CGPA"])

def calculate_letter_grade(percentage: float):
    if percentage >= 90: return "A+", 10.0
    if percentage >= 80: return "A", 9.0
    if percentage >= 70: return "B+", 8.0
    if percentage >= 60: return "B", 7.0
    if percentage >= 50: return "C", 6.0
    if percentage >= 40: return "D", 5.0
    return "F", 0.0

@twin_router.get("/health", response_model=dict)
def get_twin_health(db: Session = Depends()):
    # Example integration calculation
    patterns = db.query(BehaviorPattern).filter(BehaviorPattern.is_active == True).all()
    decisions = db.query(Decision).all()
    rated = [d for d in decisions if d.outcome_rating is not None]
    
    accuracy = round(sum(d.outcome_rating for d in rated) / len(rated) * 20.0, 1) if rated else 92.5
    personalization = min(100, max(25, 25 + len(decisions) * 8))
    
    metrics = TwinHealthMetrics(
        personalization_score=personalization,
        data_coverage=85,
        decision_history_count=len(decisions),
        feedback_received_count=len(rated),
        prediction_accuracy=accuracy
    )
    return {"health": metrics.dict(), "patterns": patterns, "decisions": decisions}

@twin_router.post("/decisions")
def log_decision(payload: DecisionCreate, db: Session = Depends()):
    dec = Decision(
        id=f"dec_{int(datetime.utcnow().timestamp()*1000)}",
        question=payload.question,
        recommended_scenario=payload.recommended_scenario,
        chosen_scenario=payload.chosen_scenario,
        user_reason=payload.user_reason,
        is_disagreement=payload.is_disagreement
    )
    db.add(dec)
    
    # Transparent weighted learning loop
    if payload.is_disagreement:
        # Increase weight and confidence of user preference
        pattern = db.query(BehaviorPattern).filter(
            BehaviorPattern.pattern_type == PatternType.PRIORITIZATION.value
        ).first()
        if pattern:
            pattern.weight = min(2.5, pattern.weight + 0.15)
            pattern.confidence = min(99.0, pattern.confidence + 4.0)
            pattern.evidence_count += 1
            pattern.evidence_summary = f"Student preferred '{payload.chosen_scenario}' over default AI recommendation."
    db.commit()
    return {"status": "success", "message": "Decision logged to behavioral memory"}

@twin_router.post("/feedback")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends()):
    dec = db.query(Decision).filter(Decision.id == payload.decision_id).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")
    dec.actual_outcome = payload.actual_outcome
    dec.outcome_rating = payload.outcome_rating
    dec.outcome_feedback = payload.outcome_feedback
    db.commit()
    return {"status": "success", "message": "Prediction vs. Reality feedback recorded."}

@grades_router.post("/add")
def record_grade(payload: GradeCreate, db: Session = Depends()):
    pct = (payload.score / payload.max_score * 100.0) if payload.max_score > 0 else 0.0
    letter, _ = calculate_letter_grade(pct)
    grade = Grade(
        id=f"g_{int(datetime.utcnow().timestamp()*1000)}",
        subject_id=payload.subject_id,
        subject_name=payload.subject_name,
        assessment_name=payload.assessment_name,
        score=payload.score,
        max_score=payload.max_score,
        weight=payload.weight,
        grade_letter=letter,
        notes=payload.notes,
        date_recorded=payload.date_recorded or date.today()
    )
    db.add(grade)
    db.commit()
    return {"status": "success", "message": f"Recorded {payload.assessment_name} ({letter})"}

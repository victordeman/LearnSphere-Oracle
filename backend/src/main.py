from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import yaml
import os
import json
import numpy as np
from datetime import timedelta
from typing import Optional, Dict, Any, List

from models import Base, User, Profile
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

from support_systems.match_maker.prompt_generation import PromptGeneration
from support_systems.match_maker.image_pipeline import ImagePipeline
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

app = FastAPI(title="LearnSphere Oracle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
config_path = os.path.join(os.path.dirname(__file__), "../../configs/db_config.yaml")
with open(config_path, "r") as f:
    db_config = yaml.safe_load(f)

DATABASE_URL = os.getenv("DATABASE_URL", db_config["database"].get("url", "postgresql://user:password@db:5432/learnsphere"))

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(AlchemyEncoder, self).default(obj)

engine = create_engine(DATABASE_URL, json_serializer=lambda obj: json.dumps(obj, cls=AlchemyEncoder))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileBase(BaseModel):
    student_id: str
    mbti_type: str
    ils_scores: Dict[str, float]
    sn_integration: str

class ProfileResponse(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class SurveyData(BaseModel):
    extrovert: int
    introvert: int
    sensing: int
    intuitive: int
    thinking: int
    feeling: int
    judging: int
    perceiving: int
    active: int
    reflective: int
    sensing_fslsm: int
    intuitive_fslsm: int
    visual: int
    verbal: int
    sequential: int
    global_ils: int
    text_time: int

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def read_root():
    return {"message": "Welcome to LearnSphere Oracle API"}

@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/profile", response_model=ProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return current_user.profile

# Global qdrant client to avoid locking issues in local mode
_qdrant_client = None

def get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        if qdrant_host == "localhost":
            # For testing in this environment, use a temporary in-memory qdrant
            # or a specific path that we know is initialized.
            # Given the constraints, memory is safest for tests.
            _qdrant_client = QdrantClient(":memory:")
            try:
                _qdrant_client.create_collection(
                    collection_name="profiles",
                    vectors_config={"size": 8, "distance": "Cosine"},
                )
            except Exception:
                pass
        else:
            _qdrant_client = QdrantClient(host=qdrant_host, port=6333)
    return _qdrant_client

@app.post("/survey")
def submit_survey(survey: SurveyData, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), qdrant: QdrantClient = Depends(get_qdrant)):
    pg = PromptGeneration()

    final_survey = [{
        "StudentID": "USER_" + str(current_user.id),
        "Extrovert": survey.extrovert, "Introvert": survey.introvert,
        "Sensing": survey.sensing, "Intuitive": survey.intuitive,
        "Thinking": survey.thinking, "Feeling": survey.feeling,
        "Judging": survey.judging, "Perceiving": survey.perceiving,
        "Active": survey.active, "Reflective": survey.reflective,
        "Sensing_FSLSM": survey.sensing_fslsm, "Intuitive_FSLSM": survey.intuitive_fslsm,
        "Visual": survey.visual, "Verbal": survey.verbal,
        "Sequential": survey.sequential, "Global": survey.global_ils,
        "Text_Time": survey.text_time
    }]

    df, prompts = pg.process_responses(final_survey)
    # Convert numpy types to native python types
    df = df.astype(object)
    row = df.iloc[0].to_dict()
    for k, v in row.items():
        if hasattr(v, "item"):
            row[k] = v.item()
        elif isinstance(v, (np.int64, np.int32)):
            row[k] = int(v)
        elif isinstance(v, (np.float64, np.float32)):
            row[k] = float(v)

    # Save or update profile
    ils_scores = {
        "Active_Reflective": float(row["Active_Reflective"]),
        "Sensing_Intuitive_ILS": float(row["Sensing_Intuitive_ILS"]),
        "Visual_Verbal": float(row["Visual_Verbal"]),
        "Sequential_Global": float(row["Sequential_Global"])
    }
    if current_user.profile:
        db_profile = current_user.profile
        db_profile.student_id = str(row["StudentID"])
        db_profile.mbti_type = str(row["MBTI_Type"])
        db_profile.ils_scores = ils_scores
        db_profile.sn_integration = str(row["SN_Integration"])
    else:
        db_profile = Profile(
            user_id=current_user.id,
            student_id=str(row["StudentID"]),
            mbti_type=str(row["MBTI_Type"]),
            ils_scores=ils_scores,
            sn_integration=str(row["SN_Integration"])
        )
        db.add(db_profile)

    db.commit()
    db.refresh(db_profile)

    # Upsert to vector store
    vector = [
        float(row["Active_Reflective"]),
        float(row["Sensing_Intuitive_ILS"]),
        float(row["Visual_Verbal"]),
        float(row["Sequential_Global"]),
        1.0 if row["MBTI_Type"][0] == "E" else 0.0,
        1.0 if row["MBTI_Type"][1] == "S" else 0.0,
        1.0 if row["MBTI_Type"][2] == "T" else 0.0,
        1.0 if row["MBTI_Type"][3] == "J" else 0.0,
    ]
    qdrant.upsert(
        collection_name="profiles",
        points=[
            PointStruct(
                id=current_user.id,
                vector=vector,
                payload={"student_id": row["StudentID"], "username": current_user.username}
            )
        ]
    )

    return {"message": "Survey processed", "profile": db_profile, "prompt": prompts[0]["Prompt"]}

@app.get("/match")
def get_matches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), qdrant: QdrantClient = Depends(get_qdrant)):
    if not current_user.profile:
        raise HTTPException(status_code=400, detail="Profile not found. Please complete the survey.")

    # Get all profiles for clustering
    all_profiles = db.query(Profile).all()
    if len(all_profiles) < 2:
        return {"message": "Not enough profiles for matching", "similar_partners": [], "complementary_partners": []}

    import pandas as pd
    data = []
    for p in all_profiles:
        d = {
            "StudentID": p.student_id,
            "MBTI_Type": p.mbti_type,
            "Active_Reflective": p.ils_scores["Active_Reflective"],
            "Sensing_Intuitive_ILS": p.ils_scores["Sensing_Intuitive_ILS"],
            "Visual_Verbal": p.ils_scores["Visual_Verbal"],
            "Sequential_Global": p.ils_scores["Sequential_Global"]
        }
        data.append(d)

    df = pd.DataFrame(data)
    ip = ImagePipeline()
    recommendations = ip.cluster_and_recommend(df)

    # Also get matches from vector store for comparison or additional results
    profile_vector = [
        float(current_user.profile.ils_scores["Active_Reflective"]),
        float(current_user.profile.ils_scores["Sensing_Intuitive_ILS"]),
        float(current_user.profile.ils_scores["Visual_Verbal"]),
        float(current_user.profile.ils_scores["Sequential_Global"]),
        1.0 if current_user.profile.mbti_type[0] == "E" else 0.0,
        1.0 if current_user.profile.mbti_type[1] == "S" else 0.0,
        1.0 if current_user.profile.mbti_type[2] == "T" else 0.0,
        1.0 if current_user.profile.mbti_type[3] == "J" else 0.0,
    ]

    vector_matches = qdrant.query_points(
        collection_name="profiles",
        query=profile_vector,
        limit=5
    ).points
    similar_from_vector = [m.payload["student_id"] for m in vector_matches if m.payload["student_id"] != current_user.profile.student_id]

    base_recs = recommendations.get(current_user.profile.student_id, {"similar_partners": [], "complementary_partners": []})
    base_recs["similar_from_vector"] = similar_from_vector

    return base_recs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

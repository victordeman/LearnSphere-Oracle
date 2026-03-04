from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Profile
import yaml
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_db():
    config_path = os.path.join(os.path.dirname(__file__), "../../../configs/db_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    db_url = os.getenv("DATABASE_URL", config["database"].get("url", "postgresql://user:password@db:5432/learnsphere"))
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if test user exists
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(username="testuser", hashed_password=pwd_context.hash("testpassword"))
            db.add(user)
            db.commit()
            db.refresh(user)

            profile = Profile(
                user_id=user.id,
                student_id="TEST_1",
                mbti_type="INFP",
                ils_scores={"Active_Reflective": -5, "Sensing_Intuitive_ILS": -7, "Visual_Verbal": 7, "Sequential_Global": -5},
                sn_integration="mildly N-oriented"
            )
            db.add(profile)
            db.commit()
            print("Database seeded successfully.")
        else:
            print("Database already seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

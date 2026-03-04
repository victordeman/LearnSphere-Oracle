from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    student_id = Column(String, unique=True, index=True)
    mbti_type = Column(String)
    ils_scores = Column(JSON)
    sn_integration = Column(String)
    user = relationship("User", back_populates="profile")

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("profiles.student_id"))
    content = Column(String)

class GeneratedImage(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("profiles.student_id"))
    image_path = Column(String)

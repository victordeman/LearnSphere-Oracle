from sqlalchemy import create_engine
from models import Base
import yaml
import os

def init_db():
    config_path = os.path.join(os.path.dirname(__file__), "../../../configs/db_config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    db_url = os.getenv("DATABASE_URL", config["database"].get("url", "postgresql://user:password@db:5432/learnsphere"))
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()

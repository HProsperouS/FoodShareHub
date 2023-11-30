from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://LIUJIAJUN:ljj20031024xyf@foodsharehubdb.cvnxxsczmlrt.us-east-1.rds.amazonaws.com:5432/FoodShareHubDB"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
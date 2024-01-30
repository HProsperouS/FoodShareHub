from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from aws.services import retrieve_secret
from utils import constants as C

secret_dict = retrieve_secret(C.SECRETS_MANAGER_SECRET_NAME)

DATABASE_URL = f"postgresql://{secret_dict['user']}:{secret_dict['password']}@{secret_dict['host']}:5432/{secret_dict['db']}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
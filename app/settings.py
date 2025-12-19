import os

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    convs_db_uri: str = os.environ.get("CONVS_DB_URI", "")


settings = Settings()

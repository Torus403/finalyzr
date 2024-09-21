from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry

from app.core.config import settings

engine = create_engine(str(settings.DB_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

mapper_registry = registry()
Base = mapper_registry.generate_base()


def setup_database():
    from app.models.users import User

    Base.metadata.create_all(bind=engine)
    mapper_registry.configure()

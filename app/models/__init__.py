from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here for Alembic autogenerate
# from app.models.user import User

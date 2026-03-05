import uuid
from abc import ABC
from typing import Generic, Type, TypeVar

# from loguru import logger
from pydantic import UUID4, BaseModel, Field

# _database = connection.get_database(settings.DATABASE_NAME)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

T = TypeVar("T", bound="PostgreSQLBase")


class PostgreSQLBase(DeclarativeBase, Generic[T]):
    """
        Base PostgreSQL 
    """
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False

        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_postgre(cls: Type[T], data: dict) -> T:
        """
            Receive a dict and return Pydantic Model
        """
        return cls(**dict(data))

    @classmethod
    def from_schema(cls, schema: BaseModel) -> "PostgreSQLBase":
        data = schema.model_dump()
        return cls(**data)

    @classmethod
    async def save(cls, schema: BaseModel, session: AsyncSession) -> "PostgreSQLBase":
        """
        Tạo instance từ Pydantic schema và lưu vào database.
        Dùng cho mọi model kế thừa PostgreSQLBase.
        """
        obj = cls.from_schema(schema)
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj
"""
Base entity (domain) and base PostgreSQL repository (CRUD).

- BaseEntity: Pydantic model với id (UUID), from_postgre (_id → id). Dùng cho domain/API.
- BasePostgresRepository: CRUD trên SQLAlchemy model (create, get_by_id, get_all, update, delete).
"""
from __future__ import annotations

import uuid
from pydantic import BaseModel, Field


# --- Base Entity (domain / API) ---

UUID4 = uuid.UUID 


class BaseEntity(BaseModel):
    """
    Base domain entity với id (UUID).
    Dùng cho validate, serialize, hoặc map từ dict (vd: "_id" → "id").
    """
    id: UUID4 = Field(default_factory=uuid.uuid4)

    model_config = {"frozen": True}

    @classmethod
    def from_postgre(cls: type["BaseEntity"], data: dict) -> BaseEntity:
        """Tạo entity từ dict; đổi key "_id" thành "id" (vd: dữ liệu từ MongoDB/API)."""
        if not data:
            raise ValueError("Data is empty.")
        data = dict(data)
        _id = data.pop("_id", data.get("id"))
        return cls(**{**data, "id": _id})

    def __hash__(self) -> int:
        return hash(self.id)
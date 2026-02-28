"""
Adapter: triển khai CompanyNameRepository bằng PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.CompanyNameRepositoryProtocol.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select

from src.shared.infrastructure.db.models import CompanyName
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)


class CompanyNameRepository(BasePostgresRepository[CompanyName]):
    """Repository cụ thể cho bảng company_name. Dùng trong market_data use cases."""

    model_class = CompanyName

    async def get_by_stock_id(self, stock_id: str) -> CompanyName | None:
        """Lấy một bản ghi theo stock_id."""
        stmt = select(CompanyName).where(CompanyName.stock_id == stock_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

"""
Adapter: triển khai CompanyNameRepository bằng PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.CompanyNameRepositoryProtocol.
"""
from __future__ import annotations

import uuid

from sqlalchemy import select

from src.shared.infrastructure.db.models import FundGav
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)


class FundGavRepository(BasePostgresRepository[FundGav]):
    """Repository cụ thể cho bảng fund_gav. Dùng trong market_data use cases."""

    model_class = FundGav

    async def get_by_fund_id(self, fund_id: str) -> FundGav | None:
        """Lấy một bản ghi theo fund_id."""
        stmt = select(FundGav).where(FundGav.fund_id == fund_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

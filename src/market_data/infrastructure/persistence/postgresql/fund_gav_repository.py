"""
Adapter: triển khai CompanyNameRepository bằng PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.CompanyNameRepositoryProtocol.
"""
from __future__ import annotations
from sqlalchemy import delete, select
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

    async def delete_before_load(self, report_month: int) -> None:
        """Xóa tất cả bản ghi FundGav cua tháng hien tai."""
        stmt = delete(FundGav).where(FundGav.report_month == report_month)
        await self.session.execute(stmt)
        await self.session.commit()

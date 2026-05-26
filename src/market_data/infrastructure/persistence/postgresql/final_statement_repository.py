"""
Adapter: triển khai FinalStatementRepository bằng PostgreSQL (SQLAlchemy).

Implement port market_data.domain.repository.FinalStatementRepositoryProtocol.
"""
from __future__ import annotations
from importlib import import_module
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)
from sqlalchemy import select


def _import_model_class(dotted_path: str) -> type[Any]:
    if ":" in dotted_path:
        module_path, attr_name = dotted_path.split(":", 1)
    else:
        module_path, attr_name = dotted_path.rsplit(".", 1)
    module = import_module(module_path)
    return cast(type[Any], getattr(module, attr_name))


class FinalStatementRepository(BasePostgresRepository[Any]):
    def __init__(self, *, model_path: str, session: AsyncSession | None = None) -> None:
        super().__init__(session=session)
        self._model_path = model_path
        self._model_class: type[Any] | None = None

    @property
    def model_class(self) -> type[Any]:
        if self._model_class is None:
            self._model_class = _import_model_class(self._model_path)
        return self._model_class

    async def upsert_by_year_quarter_stock_id(
        self,
        year: int,
        quarter: str,
        stock_id: str,
        data: dict[str, Any],
    ) -> None:
        """Upert một bản ghi theo year_quarter và stock_id."""
        
        stmt = select(self.model_class).where(
            self.model_class.stock_id == stock_id, 
            self.model_class.year == year,
            self.model_class.quarter == quarter
        )

        result = await self.session.execute(stmt)
        final_statement = result.scalar_one_or_none()
        
        if final_statement is None:
            final_statement = self.model_class(
                # stock_id=stock_id,
                # year=year,
                # quarter=quarter,
                **data,
            )
            self.session.add(final_statement)
        else:
            for key, value in data.items():
                if hasattr(final_statement, key):
                    setattr(final_statement, key, value)
        
        await self.session.commit()

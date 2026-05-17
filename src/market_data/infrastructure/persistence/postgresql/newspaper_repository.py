"""
Implement port market_data.domain.repository.NewspaperUrlRepositoryProtocol.
"""
from __future__ import annotations
from datetime import date 
from sqlalchemy import select
from src.shared.infrastructure.db.models import Newspaper
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)
import uuid


class NewspaperRepository(BasePostgresRepository[Newspaper]):
    """Repository cụ thể cho bảng stock_price. Dùng trong market_data use cases."""

    model_class = Newspaper

    async def upsert_by_newspaper_url(
        self,
        *,
        id: uuid.UUID | None = None,
        newspaper_title: str,
        newspaper_url: str,
        publish_date: str,
        newspaper_content: str,
        newspaper_summary: str,
        is_load_to_qdrant: int,
        created_at: date,
    ) -> object:
        """Upsert (insert or update) Newspaper based on newspaper_url."""
        ...
        stmt = select(Newspaper).where(Newspaper.newspaper_url == newspaper_url)
        result = await self.session.execute(stmt)
        newspaper_record = result.scalar_one_or_none()

        if newspaper_record is None:
            newspaper_record = self.model_class(
                id=id,
                newspaper_title=newspaper_title,
                newspaper_url=newspaper_url,
                publish_date=publish_date,
                newspaper_content=newspaper_content,
                newspaper_summary=newspaper_summary,
                is_load_to_qdrant=is_load_to_qdrant,
                created_at=created_at,
            )
            self.session.add(newspaper_record)
        else:
            newspaper_record.newspaper_title = newspaper_title
            newspaper_record.newspaper_url = newspaper_url
            newspaper_record.publish_date = publish_date
            newspaper_record.newspaper_content = newspaper_content
            newspaper_record.newspaper_summary = newspaper_summary
        await self.session.flush()
        return newspaper_record

        

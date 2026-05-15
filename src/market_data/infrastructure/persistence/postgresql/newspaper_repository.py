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
        title: str,
        url: str,
        publish_date: str,
        content: str,
        summary: str,
        is_embedded: int,
        created_at: date,
    ) -> object:
        """Upsert (insert or update) Newspaper based on newspaper_url."""
        ...
        stmt = select(Newspaper).where(Newspaper.url == url)
        result = await self.session.execute(stmt)
        newspaper_record = result.scalar_one_or_none()

        if newspaper_record is None:
            newspaper_record = self.model_class(
                id=id,
                title=title,
                url=url,
                publish_date=publish_date,
                content=content,
                summary=summary,
                is_embedded=is_embedded,
                created_at=created_at,
            )
            self.session.add(newspaper_record)
        else:
            newspaper_record.title = title
            newspaper_record.url = url
            newspaper_record.publish_date = publish_date
            newspaper_record.content = content
            newspaper_record.summary = summary
        await self.session.flush()
        return newspaper_record

        

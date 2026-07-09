"""
Implement port market_data.domain.repository.NewspaperUrlRepositoryProtocol.
"""
from __future__ import annotations
from datetime import date 
from sqlalchemy import select
from src.shared.infrastructure.db.models import NewspaperUrl
from src.shared.infrastructure.persistence.postgresql.repository import (
    BasePostgresRepository,
)
import uuid


class NewspaperUrlRepository(BasePostgresRepository[NewspaperUrl]):
    """Repository cụ thể cho bảng newspaper_url"""

    model_class = NewspaperUrl

    async def upsert_by_newspaper_url(
        self,
        *,
        id: uuid.UUID | None = None,
        newspaper_title: str | None = None,
        newspaper_url: str,
        source: str | None = None,
        is_crawled: int,
        created_at: date | None = None,
    ) -> object:
        """Upsert (insert or update) NewspaperUrl based on newspaper_url."""
        stmt = select(NewspaperUrl).where(NewspaperUrl.newspaper_url == newspaper_url)
        result = await self.session.execute(stmt)

        records = list(result.scalars().all())
        record = records[0] if records else None

        if len(records) > 1:
            for duplicate in records[1:]: #if record is duplicate. Delete all duplicate records
                await self.session.delete(duplicate)

        if record is None:
            if newspaper_title is None or source is None or created_at is None:
                raise ValueError(
                    "newspaper_title, source, created_at are required when inserting a new NewspaperUrl record"
                )
            record = NewspaperUrl(
                id=id,
                newspaper_title=newspaper_title,
                newspaper_url=newspaper_url,
                source=source,
                is_crawled=is_crawled,
                created_at=created_at,
            )
            self.session.add(record)
        else:
            if is_crawled == 1 and record.is_crawled == 0:
                record.is_crawled = 1

        await self.session.flush()
        return record

    async def query_urls_by_is_crawled(
        self,
    ) -> list[str]:
        """Query NewspaperUrl that not crawled"""
        stmt = select(NewspaperUrl.newspaper_url).where(NewspaperUrl.is_crawled == 0)
        result = await self.session.execute(stmt)
        return result.scalars().all()

from typing import Any, AsyncIterator

from abc import ABC, abstractmethod



class CrawlDataPort(ABC):
    @abstractmethod
    async def crawl(self, link: str, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def crawl_pages(self, link: str, **kwargs: Any) -> AsyncIterator[list[dict[str, Any]]]: ...

    @abstractmethod
    async def extract(self, link: str, **kwargs: Any) -> list[dict[str, Any]]: ...

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright


class BaseCrawler(ABC):
    # model: type[NoSQLBaseDocument]

    @abstractmethod
    async def extract(self, link: str, **kwargs: Any) -> Any: ...


class BasePlaywrightCrawler(BaseCrawler, ABC):
    def __init__(
        self,
        *,
        headless: bool = True,
        scroll_limit: int = 5,
        navigation_timeout_ms: int = 30_000,
    ) -> None:
        self.headless = headless
        self.scroll_limit = scroll_limit
        self.navigation_timeout_ms = navigation_timeout_ms

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Crawler chưa được init. Hãy gọi `await run(...)` trước.")
        return self._page

    async def _init_crawler(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context()
        self._page = await self._context.new_page()
        self._page.set_default_navigation_timeout(self.navigation_timeout_ms)

    async def _close_crawler(self) -> None:
        if self._context is not None:
            await self._context.close()
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    async def handle_popup():
        pass

    async def scroll_page():
        pass

    async def click_to_next_button():
        pass

    async def run(self, link: str, **kwargs: Any) -> Any:
        await self._init_crawler()
        try:
            return await self.extract(link, **kwargs)
        finally:
            await self._close_crawler()

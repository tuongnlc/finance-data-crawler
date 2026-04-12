import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to sys.path if running as script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from orchestration.python_script.crawl_market_data_v1 import run_crawler


async def main():
    parser = argparse.ArgumentParser(description="Crawl stock prices based on config.")
    parser.add_argument("--url", type=str, help="Path to the configuration YAML file", default="configs/crawl_stock_price.yaml")
    args = parser.parse_args()

    load_dotenv()
    await run_crawler(url=args.url)

if __name__ == "__main__":
    asyncio.run(main())

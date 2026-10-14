# cli/sync_share_data.py
"""命令行同步股本变动 / 股东户数。"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import traceback
from datetime import date

from app.services.update_share_data import update_share_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("sync_share_data")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="同步股本变动与股东户数到 SQLite")
    p.add_argument(
        "symbols",
        nargs="+",
        help="6 位股票代码，可一次多个，如 600519 000001",
    )
    p.add_argument(
        "--start",
        default="20200101",
        help="起始日期 YYYYMMDD，默认 20200101",
    )
    p.add_argument(
        "--end",
        default=date.today().strftime("%Y%m%d"),
        help="结束日期 YYYYMMDD，默认今天",
    )
    return p.parse_args(argv)


async def run(symbols: list[str], start_date: str, end_date: str) -> int:
    failed: list[str] = []
    for raw in symbols:
        symbol = raw.strip()[-6:]
        if not symbol:
            continue
        logger.info("正在更新 %s（%s ~ %s）...", symbol, start_date, end_date)
        try:
            await update_share_data(symbol, start_date, end_date)
            logger.info("%s 更新完成", symbol)
        except Exception as e:
            logger.error("%s 更新失败: %s", symbol, e)
            traceback.print_exc()
            failed.append(symbol)
    if failed:
        logger.error("失败: %s", ", ".join(failed))
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return asyncio.run(run(args.symbols, args.start, args.end))


if __name__ == "__main__":
    raise SystemExit(main())

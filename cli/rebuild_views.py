# cli/rebuild_views.py
"""对 settings.DB_PATH 执行 app/queries 下的视图（及建表）SQL。"""

from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("rebuild_views")

# 只跑建视图 / 建表脚本；跳过纯 SELECT 查询文件（get_*）
INCLUDE_PREFIXES = ("view_", "creat_", "profit_")


def list_sql_files(sql_dir: Path) -> list[Path]:
    files = sorted(sql_dir.glob("*.sql"))
    selected: list[Path] = []
    for f in files:
        name = f.name.lower()
        if name.startswith(INCLUDE_PREFIXES):
            selected.append(f)
        else:
            logger.info("跳过查询文件: %s", f.name)
    return selected


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="重建 financial.db 中的视图 / 相关表")
    p.add_argument(
        "--db",
        default=str(settings.DB_PATH),
        help="SQLite 路径，默认 settings.DB_PATH",
    )
    p.add_argument(
        "--sql-dir",
        default=str(settings.SQL_DIR),
        help="SQL 目录，默认 settings.SQL_DIR",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    db_path = Path(args.db)
    sql_dir = Path(args.sql_dir)

    if not db_path.exists():
        logger.error("数据库不存在: %s", db_path)
        return 1
    if not sql_dir.is_dir():
        logger.error("SQL 目录不存在: %s", sql_dir)
        return 1

    files = list_sql_files(sql_dir)
    if not files:
        logger.error("未找到可执行的 SQL 文件（view_/creat_/profit_）")
        return 1

    logger.info("数据库: %s", db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        for f in files:
            sql = f.read_text(encoding="utf-8")
            logger.info("执行: %s", f.name)
            conn.executescript(sql)
        conn.commit()
    except Exception:
        logger.exception("执行失败")
        return 1
    finally:
        conn.close()

    logger.info("完成，共执行 %d 个文件", len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

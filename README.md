# stocks-db-maint

独立维护 SQLite `financial.db` 的后端 CLI：只负责拉取与写入（雪球三表财报、东财业绩快报、分红、股本/股东、视图重建）。**不含**查询 API、登录与前端。

主库约定：本地以 `D:\DB\financial.db` 为准；VPS 等环境用环境变量 `DB_PATH` 指向对应路径。本仓库不存放数据库文件与密钥。

## 目录

```
stocks-db-maint/
├── app/
│   ├── core/config.py      # DB_PATH 等配置
│   ├── crud/               # 写库
│   ├── services/           # 抓取与同步编排
│   ├── queries/            # 视图 / 建表 SQL
│   ├── config/             # financial_fields.json 等
│   └── utils/              # 雪球 cookie、工具函数
└── cli/                    # 命令行入口
```

## 安装

```bash
cd stocks-db-maint
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium # 雪球 cookie 自动刷新需要
cp .env.example .env        # 按需改 DB_PATH
```

## 配置

| 变量 | 说明 |
|------|------|
| `DB_PATH` | SQLite 路径，默认 `./data/financial.db` |
| `STOCK_DICT_A_PATH` | 股票名称字典 `.npy` |
| `OUTPUT_JSON_DIR` | JSON 中间文件目录 |
| `TIMEOUT` / `XUEQIU_REFERER` | 雪球请求超时与 Referer |

雪球 `xq_a_token` 由 Playwright 自动刷新，一般无需手工配置 cookies。

## CLI 示例

在仓库根目录执行：

```bash
# 雪球三表（资产负债表 / 利润表 / 现金流）
python -m cli.sync_financials SH600406
python -m cli.sync_financials SH600406 SZ000027 --concurrency 3
python -m cli.sync_financials --from-db

# 东财业绩快报 → financial_performance
python -m cli.sync_performance 20260630
python -m cli.sync_performance 20241231 20250630 20260630

# 分红 → dividend_events
python -m cli.sync_dividends 000902
python -m cli.sync_dividends 000902 600519 --db D:/DB/financial.db

# 股本变动 / 股东户数
python -m cli.sync_share_data 600519
python -m cli.sync_share_data 600519 000001 --start 20200101

# 重建视图（view_ / creat_ / profit_*.sql）
python -m cli.rebuild_views
python -m cli.rebuild_views --db D:/DB/financial.db
```

## 与 APP_TO_ANALYZE_STOCKS 的关系

本仓库从 [APP_TO_ANALYZE_STOCKS](https://github.com/rocket-shen/APP_TO_ANALYZE_STOCKS) 拆出写库链路（`crud` / `scripts`→`cli` / 相关 `services` / `queries`）。查询站点与 API 仍在原仓库；两边可共用同一 `financial.db`。

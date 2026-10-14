# app/core/config.py — SQLite financial.db 维护专用（无认证 / API）
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 仓库根目录（app/ 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    APP_NAME: str = "stocks-db-maint"
    ENV: str = "dev"

    # 路径：可用环境变量覆盖；未设置时用相对路径
    DB_PATH: Path = BASE_DIR / "data" / "financial.db"
    STOCK_DICT_A_PATH: Path = BASE_DIR / "data" / "stock_dict_a.npy"
    OUTPUT_JSON_DIR: Path = BASE_DIR / "data" / "output"
    DEFAULT_EXPORT_DIR: Path = BASE_DIR / "data" / "exports"

    FINANCIAL_FIELDS_JSON: Path = BASE_DIR / "app" / "config" / "financial_fields.json"
    SQL_DIR: Path = BASE_DIR / "app" / "queries"

    XUEQIU_REFERER: str = "https://xueqiu.com/"
    TIMEOUT: float = 15.0

    @field_validator(
        "DB_PATH",
        "STOCK_DICT_A_PATH",
        "OUTPUT_JSON_DIR",
        "DEFAULT_EXPORT_DIR",
        "FINANCIAL_FIELDS_JSON",
        "SQL_DIR",
        mode="before",
    )
    @classmethod
    def parse_path(cls, v):
        return Path(v) if v else v

    @property
    def is_dev(self) -> bool:
        return self.ENV.strip().lower() == "dev"

    def ensure_dirs(self) -> None:
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
        self.DEFAULT_EXPORT_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()

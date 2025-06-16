BOT_NAME = "sjpl_scraper"

SPIDER_MODULES = ["sjpl_scraper.spiders"]
NEWSPIDER_MODULE = "sjpl_scraper.spiders"

# 注册 Pipeline
ITEM_PIPELINES = {
    'sjpl_scraper.pipelines.SQLitePipeline': 300,
}

# SQLite 存储路径
SQLITE_DB_PATH = "events.db"

# 增量模式开启（可选）
INCREMENTAL_MODE = True

# 输出调试日志
LOG_LEVEL = 'INFO'

# Scrapy settings for sjpl_scraper project

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
LOG_LEVEL = 'DEBUG'

# 请求头设置
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

# 下载延迟
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

# 并发请求数
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# 启用自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = True

# 启用重试
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 302, 303]

# 启用cookies
COOKIES_ENABLED = True
COOKIES_DEBUG = True

# 重定向设置
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 5

# 会话设置
COOKIES_PERSISTENCE = True
COOKIES_PERSISTENCE_DIR = 'cookies'

# 下载中间件设置
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

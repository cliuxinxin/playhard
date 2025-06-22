BOT_NAME = "cupertino_spider"
SPIDER_MODULES = ["cupertino_spider.spiders"]
NEWSPIDER_MODULE = "cupertino_spider.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1

LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    "cupertino_spider.pipelines.SQLitePipeline": 300,
}

BOT_NAME = "sjpl_spider"
SPIDER_MODULES = ["sjpl_spider.spiders"]
NEWSPIDER_MODULE = "sjpl_spider.spiders"

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 4
LOG_LEVEL = 'INFO'

# 如果你后期要将数据写入 sqlite，可以写 pipeline
ITEM_PIPELINES = {
    "sjpl_spider.pipelines.SQLitePipeline": 300,  # 后续可实现
}

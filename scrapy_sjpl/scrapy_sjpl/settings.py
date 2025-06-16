BOT_NAME = 'scrapy_sjpl'

SPIDER_MODULES = ['scrapy_sjpl.spiders']
NEWSPIDER_MODULE = 'scrapy_sjpl.spiders'

ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'scrapy_sjpl.pipelines.EventPipeline': 300,
}

DOWNLOAD_DELAY = 1

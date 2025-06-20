import scrapy

class SjplEventItem(scrapy.Item):
    event_id = scrapy.Field()
    title = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    address = scrapy.Field()  # ✅ 新增字段
    location = scrapy.Field()
    location_details = scrapy.Field()
    audiences = scrapy.Field()
    event_types = scrapy.Field()
    languages = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    image_url = scrapy.Field()
    is_cancelled = scrapy.Field()
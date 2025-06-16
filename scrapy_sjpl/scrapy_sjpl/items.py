import scrapy

class EventItem(scrapy.Item):
    event_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()
    is_cancelled = scrapy.Field()
    is_virtual = scrapy.Field()
    full_location = scrapy.Field()
    address = scrapy.Field()
    address_obj = scrapy.Field()
    audiences = scrapy.Field()
    event_types = scrapy.Field()
    contact = scrapy.Field()
    registration_info = scrapy.Field()
    event_url = scrapy.Field()
    image_url = scrapy.Field()

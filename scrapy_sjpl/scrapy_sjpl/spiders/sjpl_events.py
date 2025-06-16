import scrapy
import json
from scrapy_sjpl.items import EventItem

BASE_API_URL = 'https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search?page={page_num}&limit=20&locale=en-US'

HEADERS = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://sjpl.bibliocommons.com',
    'referer': 'https://sjpl.bibliocommons.com/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}

class SjplEventsSpider(scrapy.Spider):
    name = 'sjpl_events'
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': HEADERS,
    }

    def __init__(self, max_pages=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = 1
        self.max_pages = int(max_pages)  # 支持命令行动态传入分页数
        self.lookups = None

    def start_requests(self):
        url = BASE_API_URL.format(page_num=self.page)
        yield scrapy.Request(url, callback=self.parse)

    def build_lookup_tables(self, entities):
        lookups = {}
        lookups['audiences'] = {v['id']: v['name'] for v in entities.get('eventAudiences', {}).values()}
        lookups['types'] = {v['id']: v['name'] for v in entities.get('eventTypes', {}).values()}
        lookups['programs'] = {v['id']: v['name'] for v in entities.get('eventPrograms', {}).values()}
        lookups['languages'] = {v['id']: v['name'] for v in entities.get('eventLanguages', {}).values()}
        lookups['images'] = {img_id: img_data.get('url') for img_id, img_data in entities.get('images', {}).items()}
        lookups['locations'] = entities.get('locations', {})
        return lookups

    def parse_event(self, event_data, lookups):
        definition = event_data.get('definition', {})
        if not definition:
            return None

        location_id = definition.get('branchLocationId')
        location_data = lookups['locations'].get(location_id) if location_id else None

        location_name = None
        address_obj = None
        formatted_address = None

        if location_data:
            location_name = location_data.get('name')
            address_obj = location_data.get('address')
            if address_obj:
                formatted_address = f"{address_obj.get('number', '')} {address_obj.get('street', '')}, {address_obj.get('city', '')}, {address_obj.get('state', '')} {address_obj.get('zip', '')}".strip()

        location_details = definition.get('locationDetails')

        full_location = location_name if location_name else ""
        if location_details:
            full_location += f" - {location_details}"

        audience_names = [lookups['audiences'].get(aud_id) for aud_id in definition.get('audienceIds', []) if aud_id]
        type_names = [lookups['types'].get(type_id) for type_id in definition.get('typeIds', []) if type_id]

        item = EventItem(
            event_id=event_data.get('id'),
            title=definition.get('title'),
            description=definition.get('description'),
            start_time=definition.get('start'),
            end_time=definition.get('end'),
            is_cancelled=definition.get('isCancelled', False),
            is_virtual=event_data.get('isVirtual', False),
            full_location=full_location.strip(),
            address=formatted_address,
            address_obj=address_obj,
            audiences=audience_names,
            event_types=type_names,
            contact=definition.get('contact'),
            registration_info=definition.get('registrationInfo'),
            event_url=f"https://sjpl.bibliocommons.com/events/{event_data.get('id')}",
            image_url=lookups['images'].get(definition.get('featuredImageId')),
        )
        return item

    def parse(self, response):
        data = json.loads(response.text)

        if self.page == 1:
            entities = data.get('entities', {})
            self.lookups = self.build_lookup_tables(entities)
            # 如果max_pages没有指定，默认用接口返回的总页数限制
            if self.max_pages == 0:
                self.max_pages = data.get('pagination', {}).get('pages', 1)

        event_entities = data.get('entities', {}).get('events', {})
        event_ids = data.get('events', {}).get('results', [])

        for event_id in event_ids:
            event_data = event_entities.get(event_id)
            if event_data:
                item = self.parse_event(event_data, self.lookups)
                if item:
                    yield item

        if self.page < self.max_pages:
            self.page += 1
            next_url = BASE_API_URL.format(page_num=self.page)
            yield scrapy.Request(next_url, callback=self.parse)

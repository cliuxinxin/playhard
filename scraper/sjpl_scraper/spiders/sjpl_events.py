import scrapy
import json
from bs4 import BeautifulSoup
from sjpl_scraper.items import SjplEventItem

class SjplEventsSpider(scrapy.Spider):
    name = "sjpl_events"
    allowed_domains = ["gateway.bibliocommons.com"]
    start_urls = ["https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search?page=1&limit=20&locale=en-US"]

    custom_settings = {
        'FEEDS': {
            'sjpl_events.csv': {
                'format': 'csv',
                'encoding': 'utf-8-sig',
                'overwrite': True
            },
        },
    }

    HEADERS = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://sjpl.bibliocommons.com',
        'referer': 'https://sjpl.bibliocommons.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

    COOKIES = {
        'EVENT': 'app01b',
        'NERF_SRV': 'nerf17',
        'SRV': 'app36',
        '_ga': 'GA1.1.184796718.1749706354',
        'branch': '{"ip":"128.199.11.195","sjpl":null}',
        '_ga_F5QPDQX1BM': 'GS2.1.s1750055591$o6$g1$t1750057934$j46$l0$h0',
        '_ga_G99DMMNG39': 'GS2.1.s1750055591$o5$g1$t1750057934$j46$l0$h0'
    }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.HEADERS, cookies=self.COOKIES, callback=self.parse, meta={'page': 1})

    def parse(self, response):
        data = json.loads(response.text)
        entities = data.get('entities', {})
        audiences = {k: v['name'] for k, v in entities.get('eventAudiences', {}).items()}
        event_types = {k: v['name'] for k, v in entities.get('eventTypes', {}).items()}
        languages = {k: v['name'] for k, v in entities.get('eventLanguages', {}).items()}
        locations_lookup = {}
        for loc_id, loc_data in entities.get('locations', {}).items():
            location_name = loc_data.get('name', f"Unknown ID: {loc_id}")
            address_data = loc_data.get('address', {})
            address_parts = [
                address_data.get('number', ''),
                address_data.get('street', ''),
                address_data.get('city', ''),
                address_data.get('state', ''),
                address_data.get('zip', '')
            ]
            full_address = ', '.join(part for part in address_parts if part)
            locations_lookup[loc_id] = {
                'name': location_name,
                'address': full_address
    }


        for event_id in data.get('events', {}).get('results', []):
            event_data = entities.get('events', {}).get(event_id)
            if not event_data:
                continue
            definition = event_data.get('definition', {})
            description_html = definition.get('description', '')
            soup = BeautifulSoup(description_html, 'html.parser')
            cleaned_description = soup.get_text(separator='\n', strip=True)

            location_id = definition.get('branchLocationId')
            location_details = definition.get('locationDetails', '')
            location_name = "N/A"
            address = ""

            if event_data.get('isVirtual'):
                location_name = "Online / Virtual"
                full_location = location_name
            else:
                location_info = locations_lookup.get(str(location_id))
                if location_info:
                    location_name = location_info['name']
                    address = location_info['address']
                full_location = location_name
                if location_details:
                    full_location = f"{location_name}, {location_details}"


            # location_details 拼接
            location_details = definition.get('locationDetails', '')
            full_location = location_name
            if location_details:
                full_location = f"{location_name}, {location_details}"

            item = SjplEventItem()
            item['event_id'] = event_id
            item['title'] = definition.get('title', 'N/A')
            item['start_time'] = definition.get('start', 'N/A')
            item['end_time'] = definition.get('end', 'N/A')
            item['address'] = address
            item['location'] = full_location
            item['location_details'] = location_details  # 保持冗余字段原样记录
            item['audiences'] = ', '.join([audiences.get(aid, 'N/A') for aid in definition.get('audienceIds', [])])
            item['event_types'] = ', '.join([event_types.get(tid, 'N/A') for tid in definition.get('typeIds', [])])
            item['languages'] = ', '.join([languages.get(lid, 'N/A') for lid in definition.get('languageIds', [])])
            item['description'] = cleaned_description
            item['link'] = f"https://sjpl.bibliocommons.com/events/{event_id}"
            item['is_cancelled'] = definition.get('isCancelled', False)
            item['image_url'] = entities['images'][definition['featuredImageId']]['url']
            yield item

        pagination = data.get('pagination', {})
        current_page = pagination.get('page')
        total_pages = 10
        if current_page and total_pages and current_page < total_pages:
            next_page = current_page + 1
            next_url = f"https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search?page={next_page}&limit=20&locale=en-US"
            yield scrapy.Request(next_url, headers=self.HEADERS, cookies=self.COOKIES, callback=self.parse, meta={'page': next_page})
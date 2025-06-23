# spiders/sunnyvale_spider.py

import scrapy
from ..items import SjplEventItem
import re

class SunnyvaleSpider(scrapy.Spider):
    name = 'sunnyvale_events'
    allowed_domains = ['www.sunnyvale.ca.gov']
    start_urls = ['https://www.sunnyvale.ca.gov/news-center-and-events-calendar/city-calendar']
    
    # 为了防止无限翻页，设置一个最大抓取月数
    # 0 代表当前月, 1 代表下个月, 以此类推
    MAX_MONTH_DEPTH = 2 

    def start_requests(self):
        # 初始请求，附带 meta 信息用于跟踪翻页深度
        yield scrapy.Request(url=self.start_urls[0], meta={'month_depth': 0})

    def parse(self, response):
        """
        解析日历列表页.
        1. 提取当前页面所有事件的详情页链接.
        2. 查找并跟进 "Next Month" 链接进行翻页.
        """
        # 提取当前月份所有事件的链接
        # 链接在 <td class="calendar_day_with_items"> 下的 <a> 标签中
        event_links = response.css('td.calendar_day_with_items a.calendar_eventlink::attr(href)').getall()
        for link in event_links:
            # 使用 urljoin 确保链接是完整的
            detail_url = response.urljoin(link)
            yield scrapy.Request(url=detail_url, callback=self.parse_event)

        # 处理翻页 (Next Month)
        month_depth = response.meta.get('month_depth', 0)
        if month_depth < self.MAX_MONTH_DEPTH:
            next_page_link = response.css('a.next::attr(href)').get()
            if next_page_link:
                next_page_url = response.urljoin(next_page_link)
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    meta={'month_depth': month_depth + 1}
                )

    def parse_event(self, response):
        """
        解析事件详情页，提取所有字段.
        """
        item = SjplEventItem()
        
        # 从URL中提取event_id
        # e.g., /Home/Components/Calendar/Event/8735/19 -> 8735
        event_id_match = re.search(r'/Event/(\d+)/', response.url)
        item['event_id'] = event_id_match.group(1) if event_id_match else None

        # 提取标题
        title_text = response.css('h2.detail-title span[itemprop="summary"]::text').get('').strip()
        item['title'] = title_text
        
        # 判断事件是否被取消
        item['is_cancelled'] = 'cancel' in title_text.lower()
        
        # 提取开始和结束时间 (UTC格式)
        item['start_time'] = response.css('time[itemprop="startDate"]::attr(datetime)').get()
        item['end_time'] = response.css('time[itemprop="endDate"]::attr(datetime)').get()
        
        # 提取地点和地址
        item['location'] = response.css('span[itemprop="location"] span[itemprop="name"]::text').get('').strip()
        address_parts = response.xpath('//span[@itemprop="address"]//text()').getall()
        item['address'] = ' '.join(part.strip() for part in address_parts if part.strip()).replace('\n', ', ')

        # 提取描述
        description_parts = response.css('div.detail-content *::text').getall()
        item['description'] = ' '.join(part.strip() for part in description_parts if part.strip())
        
        # 详情页链接
        item['link'] = response.url

        # --- 以下字段在HTML中未找到明确对应项，暂时留空 ---
        item['location_details'] = None # 描述中可能包含，但没有单独字段
        item['audiences'] = []          # 未找到
        item['event_types'] = []       # 未找到
        item['languages'] = []         # 未找到
        item['image_url'] = None       # 未找到

        yield item
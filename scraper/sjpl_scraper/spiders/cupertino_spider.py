import scrapy
from scrapy.http import FormRequest
from ..items import SjplEventItem
from datetime import datetime
import re
import hashlib

class CupertinoEventsSpider(scrapy.Spider):
    name = 'cupertino_events'
    allowed_domains = ['www.cupertino.gov']
    start_urls = ['https://www.cupertino.gov/Parks-Recreation/Events/Parks-and-Recreation-Event-Calendar']

    def start_requests(self):
        """重写start_requests方法，添加自定义请求头"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                },
                dont_filter=True
            )

    def parse(self, response):
        """
        这个方法处理活动列表页。
        它会为每个活动生成一个详情页的请求，并处理分页。
        """
        self.logger.debug(f"正在解析列表页: {response.url}")
        
        # 1. 提取当前页面所有活动的详情页链接
        event_links = response.css('div.list-item-container article > a::attr(href)').getall()
        self.logger.info(f"找到 {len(event_links)} 个活动链接")
        
        for link in event_links:
            full_url = response.urljoin(link)
            self.logger.debug(f"准备抓取活动详情: {full_url}")
            yield response.follow(
                link,
                callback=self.parse_event_detail,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                }
            )

        # 2. 处理分页
        next_button = response.css('span.button-next input[name="ctl10$ctl00$ctl09"]')
        if next_button and not next_button.css('[disabled="disabled"]'):
            self.logger.info("找到下一页按钮，准备抓取下一页")
            yield FormRequest.from_response(
                response,
                formdata={
                    '__EVENTTARGET': 'ctl10$ctl00$ctl09'
                },
                callback=self.parse,
                dont_filter=True,
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                }
            )
        else:
            self.logger.info("没有找到下一页按钮或已到最后一页")

    def generate_event_id(self, title, start_time, url):
        """生成唯一的event_id"""
        unique_string = f"{title}_{start_time}_{url}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def parse_date_time(self, date_str):
        """解析日期时间字符串"""
        try:
            # 移除多余的空白字符
            date_str = ' '.join(date_str.split())
            
            # 处理多行日期格式
            if '\n' in date_str:
                date_str = date_str.replace('\n', ' ').strip()
            
            # 尝试匹配不同的日期格式
            patterns = [
                # 格式: "Thursday, June 12, 2025 | 06:30 PM - 08:00 PM"
                r'([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s*\|\s*(\d+:\d+\s+[AP]M)\s*-\s*(\d+:\d+\s+[AP]M)',
                # 格式: "Friday, July 04, 2025 | 09:30 PM"
                r'([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s*\|\s*(\d+:\d+\s+[AP]M)',
                # 格式: "Saturday, July 19, 2025 | 06:00 PM - Sunday, July 20, 2025 | 08:30 PM"
                r'([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s*\|\s*(\d+:\d+\s+[AP]M)\s*-\s*([A-Za-z]+,\s+[A-Za-z]+\s+\d+,\s+\d{4})\s*\|\s*(\d+:\d+\s+[AP]M)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    if len(match.groups()) == 3:  # 单日多时段
                        date_part = match.group(1)
                        start_time = match.group(2)
                        end_time = match.group(3)
                        start_datetime = datetime.strptime(f"{date_part} {start_time}", "%A, %B %d, %Y %I:%M %p")
                        end_datetime = datetime.strptime(f"{date_part} {end_time}", "%A, %B %d, %Y %I:%M %p")
                        return start_datetime, end_datetime
                    elif len(match.groups()) == 2:  # 单日单时段
                        date_part = match.group(1)
                        start_time = match.group(2)
                        start_datetime = datetime.strptime(f"{date_part} {start_time}", "%A, %B %d, %Y %I:%M %p")
                        # 假设活动持续2小时
                        end_datetime = start_datetime.replace(hour=start_datetime.hour + 2)
                        return start_datetime, end_datetime
                    elif len(match.groups()) == 4:  # 跨日
                        start_date = match.group(1)
                        start_time = match.group(2)
                        end_date = match.group(3)
                        end_time = match.group(4)
                        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%A, %B %d, %Y %I:%M %p")
                        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%A, %B %d, %Y %I:%M %p")
                        return start_datetime, end_datetime
            
            self.logger.warning(f"无法解析日期格式: {date_str}")
            return None, None
            
        except Exception as e:
            self.logger.error(f"解析日期时出错 {date_str}: {str(e)}")
            return None, None

    def parse_event_detail(self, response):
        """
        这个方法处理活动详情页，提取具体信息。
        """
        self.logger.debug(f"正在解析活动详情页: {response.url}")
        
        # 提取所有的日期和时间
        dates = [date.strip() for date in response.css('ul.multi-date-list li::text').getall()]
        self.logger.debug(f"找到 {len(dates)} 个日期")
        
        # 提取描述
        description_parts = response.xpath(
            '//img[contains(@class, "main-page-image")]/following-sibling::p//text()'
        ).getall()
        description = ' '.join(part.strip() for part in description_parts if part.strip())

        # 提取位置信息
        location = response.xpath('//h2[text()="Location"]/following-sibling::p[1]/text()').get('').strip()
        
        # 提取标题
        title = response.css('h1.oc-page-title::text').get('').strip()
        self.logger.debug(f"活动标题: {title}")

        # 提取主图片URL
        image_relative_url = response.css('img.main-page-image::attr(src)').get()
        # 将相对URL转换为绝对URL，如果找不到图片则返回None
        image_url = response.urljoin(image_relative_url) if image_relative_url else None
        
        # 处理每个日期
        for date_str in dates:
            start_datetime, end_datetime = self.parse_date_time(date_str)
            if start_datetime and end_datetime:
                # 生成event_id
                event_id = self.generate_event_id(title, start_datetime.strftime("%Y-%m-%d %H:%M:%S"), response.url)
                
                item = SjplEventItem()
                item['event_id'] = event_id
                item['title'] = title
                item['description'] = description
                item['start_time'] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
                item['end_time'] = end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                item['location'] = location
                item['address'] = location  # 使用相同的位置信息
                item['location_details'] = ''  # 默认空字符串
                item['event_types'] = ','.join(response.css('ul.categories-list li a::text').getall())
                item['audiences'] = ''  # 默认空字符串
                item['languages'] = ''  # 默认空字符串
                item['link'] = response.url
                item['image_url'] = image_url  # 默认空字符串
                item['is_cancelled'] = False
                
                self.logger.info(f"成功解析活动: {title} ({start_datetime.strftime('%Y-%m-%d %H:%M')})")
                yield item 
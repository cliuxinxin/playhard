import scrapy
import json
import re
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from ..items import SjplEventItem
import logging

class FremontActivitiesSpider(scrapy.Spider):
    name = "fremont_activities"
    allowed_domains = ["anc.apm.activecommunities.com"]
    
    # 修改起始URL
    start_url = "https://anc.apm.activecommunities.com/fremont/activity/search?onlineSiteId=0&activity_select_param=2&viewMode=list"
    
    # 修改API URL
    api_url = "https://anc.apm.activecommunities.com/fremont/rest/activities/list?locale=en-US"

    def start_requests(self):
        """重写start_requests方法，访问主页面获取CSRF令牌"""
        self.logger.info("开始请求主页面: %s", self.start_url)
        yield scrapy.Request(
            url=self.start_url,
            callback=self.get_token_and_start_api_calls,
            dont_filter=True
        )

    def get_token_and_start_api_calls(self, response):
        """解析主页面获取CSRF令牌，然后开始API调用"""
        self.logger.info("成功获取主页面，准备提取CSRF令牌")
        
        # 从script标签中提取令牌
        script_text = response.xpath('//script[contains(text(), "__csrfToken")]/text()').get()
        
        if not script_text:
            self.logger.error("无法找到包含CSRF令牌的script标签")
            return

        # 使用正则表达式提取令牌值
        match = re.search(r'window\.__csrfToken\s*=\s*"(.*?)"', script_text)
        if not match:
            self.logger.error("正则表达式无法从script中提取CSRF令牌")
            return
            
        csrf_token = match.group(1)
        self.logger.info("成功提取CSRF令牌: %s", csrf_token)

        # 搜索过滤条件
        post_body = {
            "activity_search_pattern": {
                "skills": [],
                "time_after_str": "",
                "days_of_week": None,
                "activity_select_param": 2,
                "center_ids": [],
                "time_before_str": "",
                "open_spots": None,
                "activity_id": None,
                "activity_category_ids": [],
                "date_before": "",
                "min_age": None,
                "date_after": "",
                "activity_type_ids": [],
                "site_ids": [],
                "for_map": False,
                "geographic_area_ids": [],
                "season_ids": [],
                "activity_department_ids": [],
                "activity_other_category_ids": [],
                "child_season_ids": [],
                "activity_keyword": "",
                "instructor_ids": [],
                "max_age": None,
                "custom_price_from": "",
                "custom_price_to": ""
            },
            "activity_transfer_pattern": {}
        }
        
        # 从第1页开始
        page_number = 1
        
        # 构造API请求头
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://anc.apm.activecommunities.com',
            'Referer': self.start_url,
            'X-CSRF-Token': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'page_info': json.dumps({
                "order_by": "",
                "page_number": page_number,
                "total_records_per_page": 20
            })
        }

        # 发送第一个API请求
        self.logger.info("准备发送第一个API请求")
        yield scrapy.Request(
            url=self.api_url,
            method='POST',
            headers=headers,
            body=json.dumps(post_body),
            callback=self.parse_api,
            cb_kwargs={
                'headers': headers,
                'post_body': post_body
            },
            dont_filter=True
        )

    def parse_api(self, response, headers, post_body):
        """解析API响应，处理数据并处理分页"""
        try:
            data = json.loads(response.text)
            
            page_info = data.get('headers', {}).get('page_info', {})
            current_page = page_info.get('page_number', 1)
            total_pages = page_info.get('total_page', 1)
            
            self.logger.info("正在解析第 %d 页，共 %d 页", current_page, total_pages)
            
            activity_items = data.get('body', {}).get('activity_items', [])
            
            for item in activity_items:
                try:
                    # 使用BeautifulSoup清理HTML
                    soup = BeautifulSoup(item.get('desc', ''), 'lxml')
                    
                    # 创建事件项
                    event_item = SjplEventItem()
                    
                    # 生成唯一ID
                    event_item['event_id'] = self.generate_event_id(item)
                    
                    # 基本信息
                    event_item['title'] = item.get('name', '')
                    event_item['description'] = soup.get_text(separator=' ', strip=True)
                    event_item['link'] = item.get('detail_url', '')
                    
                    # 解析日期和时间
                    start_time, end_time = self.parse_date_time(item)
                    event_item['start_time'] = start_time
                    event_item['end_time'] = end_time
                    
                    # 地点信息
                    event_item['location'] = item.get('location', {}).get('label', '')
                    event_item['address'] = item.get('location', {}).get('address', '')
                    event_item['location_details'] = item.get('location', {}).get('description', '')
                    
                    # 其他信息
                    event_item['audiences'] = item.get('ages', '')
                    event_item['languages'] = ''  # 默认空字符串
                    event_item['event_types'] = item.get('activity_type', '')
                    event_item['image_url'] = item.get('image_url', '')
                    
                    self.logger.info("成功解析活动: %s", event_item['title'])
                    yield event_item
                    
                except Exception as e:
                    self.logger.error("处理活动时出错: %s", str(e))
                    continue
            
            # 处理分页
            if current_page < total_pages:
                next_page = current_page + 1
                
                # 更新page_info头
                headers['page_info'] = json.dumps({
                    "order_by": "",
                    "page_number": next_page,
                    "total_records_per_page": 20
                })
                
                self.logger.info("准备请求下一页: %d", next_page)
                
                yield scrapy.Request(
                    url=self.api_url,
                    method='POST',
                    headers=headers,
                    body=json.dumps(post_body),
                    callback=self.parse_api,
                    cb_kwargs={
                        'headers': headers,
                        'post_body': post_body
                    },
                    dont_filter=True
                )
                
        except json.JSONDecodeError as e:
            self.logger.error("解析API响应失败: %s", str(e))
            self.logger.debug("响应内容: %s", response.text[:500])

    def generate_event_id(self, item):
        """生成唯一的事件ID"""
        unique_str = f"{item.get('id', '')}_{item.get('name', '')}_{item.get('date_range', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def parse_date_time(self, item):
        """解析日期和时间"""
        try:
            date_range = item.get('date_range', '')
            time_range = item.get('time_range_landing_page', '')
            
            if not date_range:
                return None, None
                
            # 解析日期范围
            date_parts = date_range.split(' - ')
            if len(date_parts) != 2:
                return None, None
                
            start_date = date_parts[0]
            end_date = date_parts[1]
            
            # 解析时间范围
            time_parts = time_range.split(' - ')
            if len(time_parts) != 2:
                return None, None
                
            start_time = time_parts[0]
            end_time = time_parts[1]
            
            # 组合日期和时间
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%m/%d/%Y %I:%M %p")
            end_datetime = datetime.strptime(f"{end_date} {end_time}", "%m/%d/%Y %I:%M %p")
            
            return start_datetime.isoformat(), end_datetime.isoformat()
            
        except Exception as e:
            self.logger.warning("解析日期时间失败: %s", str(e))
            return None, None 
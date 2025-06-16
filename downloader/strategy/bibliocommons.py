from db_handler import save_activities_to_db

class BibliocommonsFetchStrategy:
    # 字段映射关系：ORM字段 -> (原始字段, 清洗函数/默认值)
    FIELD_MAPPING = {
        "title":        ("title", lambda v: v.strip() if v else "无标题"),
        "city":         (None, lambda v, raw=None: "San Jose"),  # 固定值
        "venue":        ("branchLocationId", None),    # 直接映射
        "address":      (None, lambda v, raw=None: None),        # 没有就None
        "start_time":   ("start", None),
        "end_time":     ("end", None),
        "age_range":    (None, lambda v, raw=None: None),
        "tags":         (None, lambda v, raw=None: []),
        "url":          (None, lambda v, raw: f"https://sjpl.bibliocommons.com/events/{raw.get('id')}") ,
        "is_free":      (None, lambda v, raw=None: True),
        "requires_registration": (None, lambda v, raw=None: False),
        "source":       (None, lambda v, raw=None: "sjpl.org"),
        "last_updated": (None, lambda v, raw=None: None),
    }

    def __init__(self):
        self.url = 'https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search'
        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'Origin': 'https://sjpl.bibliocommons.com',
            'Priority': 'u=1, i',
            'Referer': 'https://sjpl.bibliocommons.com/',
            'Sec-Ch-Ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }
        self.cookies = {
            'branch': '%7B%22ip%22%3A%22128.199.14.41%22%2C%22sjpl%22%3Anull%7D',
            'NERF_SRV': 'nerf16',
            'SRV': 'app34',
            'EVENT': 'app04b',
        }

    def build_params(self, page, limit=20):
        return {
            'page': page,
            'limit': limit,
            'locale': 'en-US',
        }

    def parse_page(self, page_data):
        """
        解析单页原始数据，提取事件信息。
        Args:
            page_data (dict): 原始API返回数据。
        Returns:
            list: 解析后的事件列表。
        """
        results = []
        if not page_data or "events" not in page_data:
            return results
        events_info = page_data["events"]
        if (
            "results" in events_info
            and "entities" in page_data
            and "events" in page_data["entities"]
        ):
            for event_id in events_info["results"]:
                event_details = page_data["entities"]["events"].get(event_id)
                if event_details:
                    definition = event_details.get("definition", {})
                    # 组装原始event字典，便于字段映射
                    raw_event = {**definition, **event_details}
                    results.append(raw_event)
        return results

    def map_and_clean_event(self, raw_event):
        mapped = {}
        for orm_field, (raw_field, func) in self.FIELD_MAPPING.items():
            if func:
                try:
                    value = func(raw_event.get(raw_field) if raw_field else None, raw_event)
                except TypeError:
                    value = func(raw_event.get(raw_field) if raw_field else None)
            else:
                value = raw_event.get(raw_field) if raw_field else None
            mapped[orm_field] = value
        return mapped

    def save_to_db(self, events):
        filtered_events = [self.map_and_clean_event(e) for e in events]
        save_activities_to_db(filtered_events)
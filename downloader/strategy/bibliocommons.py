class BibliocommonsFetchStrategy:
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
                    # 只保留ORM需要的字段，并生成url和source
                    extracted_event = {
                        "title": definition.get("title"),
                        "city": None,  # 可根据需要补充
                        "venue": definition.get("branchLocationId"),  # 临时用branchLocationId做venue
                        "address": None,  # 可根据需要补充
                        "start_time": definition.get("start"),
                        "end_time": definition.get("end"),
                        "age_range": None,  # 可根据需要补充
                        "tags": [],  # 可根据需要补充
                        "url": f"https://sjpl.bibliocommons.com/events/{event_details.get('id')}",
                        "is_free": True,  # 默认免费
                        "requires_registration": False,  # 默认不需要注册
                        "source": "sjpl.org",
                        "last_updated": None,  # 可根据需要补充
                    }
                    results.append(extracted_event)
        return results
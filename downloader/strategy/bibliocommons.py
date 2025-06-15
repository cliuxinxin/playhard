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
                    extracted_event = {
                        "id": event_details.get("id"),
                        "key": event_details.get("key"),
                        "seriesId": event_details.get("seriesId"),
                        "title": event_details["definition"].get("title"),
                        "description": event_details["definition"].get("description"),
                        "start_time": event_details["definition"].get("start"),
                        "end_time": event_details["definition"].get("end"),
                        "branchLocationId": event_details["definition"].get("branchLocationId"),
                        "locationDetails": event_details["definition"].get("locationDetails"),
                        "audienceIds": event_details["definition"].get("audienceIds", []),
                        "languageIds": event_details["definition"].get("languageIds", []),
                        "programId": event_details["definition"].get("programId"),
                        "typeIds": event_details["definition"].get("typeIds", []),
                        "isVirtual": event_details["definition"].get("isVirtual", False),
                        "isCancelled": event_details["definition"].get("isCancelled", False),
                        "contact_name": event_details["definition"].get("contact", {}).get("name"),
                        "contact_email": event_details["definition"].get("contact", {}).get("email", {}).get("value"),
                        "contact_phone": event_details["definition"].get("contact", {}).get("phone", {}).get("value"),
                        "isFull": event_details.get("isFull", False),
                        "registrationClosed": event_details.get("registrationClosed", False),
                        "numberRegistered": event_details.get("numberRegistered"),
                        "numberWaitlistRegistered": event_details.get("numberWaitlistRegistered"),
                    }
                    results.append(extracted_event)
        return results
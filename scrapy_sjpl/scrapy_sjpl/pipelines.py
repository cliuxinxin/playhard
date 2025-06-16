import json
from datetime import datetime

class EventPipeline:
    def open_spider(self, spider):
        self.events = []
        self.missing_fields_count = 0
        self.total_events = 0

    def process_item(self, item, spider):
        self.total_events += 1
        # 简单清洗示例：确保title和start_time存在
        if not item.get('title') or not item.get('start_time'):
            self.missing_fields_count += 1

        # 可以在这里做字段格式化，比如时间字符串转datetime等（示例略）
        self.events.append(dict(item))
        return item

    def close_spider(self, spider):
        filename = 'events.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=4)

        print(f"\n[Pipeline] Scraped {self.total_events} events, "
              f"with {self.missing_fields_count} missing title or start_time.")

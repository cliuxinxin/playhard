import sqlite3

class SQLitePipeline:
    def open_spider(self, spider):
        db_path = spider.settings.get('SQLITE_DB_PATH', 'events.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                title TEXT,
                start_time TEXT,
                end_time TEXT,
                location TEXT,
                address TEXT,
                location_details TEXT,
                audiences TEXT,
                event_types TEXT,
                languages TEXT,
                description TEXT,
                link TEXT,
                image_url TEXT,
                is_cancelled INTEGER
            )
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        # 增量抓取：跳过已存在记录
        if spider.settings.getbool('INCREMENTAL_MODE', True):
            self.cursor.execute("SELECT 1 FROM events WHERE event_id=?", (item['event_id'],))
            if self.cursor.fetchone():
                spider.logger.info(f"[SKIP] 已存在: {item['event_id']}")
                return item

        # location 字段为 location + location_details 拼接
        full_location = item['location']
        if item.get('location_details'):
            full_location = f"{full_location}, {item['location_details']}"

        self.cursor.execute('''
            INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item['event_id'], item['title'], item['start_time'], item['end_time'],
            full_location, item['address'], item['location_details'],
            item['audiences'], item['event_types'], item['languages'],
            item['description'], item['link'], item['image_url'], int(item['is_cancelled'])
        ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()

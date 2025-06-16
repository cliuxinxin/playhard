import sqlite3
import smtplib
from email.mime.text import MIMEText

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
                location_details TEXT,
                audiences TEXT,
                event_types TEXT,
                languages TEXT,
                description TEXT,
                link TEXT,
                is_cancelled INTEGER
            )
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            if spider.settings.getbool('INCREMENTAL_MODE', True):
                self.cursor.execute("SELECT 1 FROM events WHERE event_id=?", (item['event_id'],))
                if self.cursor.fetchone():
                    spider.logger.info(f"[SKIP] 已存在: {item['event_id']}")
                    return item

            self.cursor.execute('''
                INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['event_id'], item['title'], item['start_time'], item['end_time'],
                item['location'], item['location_details'], item['audiences'],
                item['event_types'], item['languages'], item['description'],
                item['link'], int(item['is_cancelled'])
            ))
            self.conn.commit()
        except Exception as e:
            spider.logger.error(f"[ERROR] 插入失败: {e}")
            # self.send_email(f"Scrapy 爬虫出错：{e}")
        return item

    def close_spider(self, spider):
        self.conn.close()

    def send_email(self, content):
        sender = 'your@email.com'
        receivers = ['alert@email.com']
        msg = MIMEText(content)
        msg['Subject'] = 'Scrapy 报错通知'
        msg['From'] = sender
        msg['To'] = ', '.join(receivers)

        try:
            with smtplib.SMTP_SSL('smtp.yourprovider.com', 465) as server:
                server.login('your@email.com', 'your_password')
                server.sendmail(sender, receivers, msg.as_string())
        except Exception as e:
            print(f"[EMAIL ERROR] 无法发送错误邮件：{e}")

import logging

logging.basicConfig(level=logging.INFO)

def notify(message):
    # 未来可以扩展为邮件、钉钉、Slack 通知等
    logging.info(f"{message}")
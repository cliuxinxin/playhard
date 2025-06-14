import logging

logging.basicConfig(level=logging.ERROR)

def notify(message):
    # 未来可以扩展为邮件、钉钉、Slack 通知等
    logging.error(f"[报警] {message}")
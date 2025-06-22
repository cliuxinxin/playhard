from apscheduler.schedulers.blocking import BlockingScheduler
from platform.spider_runner import run_spider
from platform.config_loader import load_task_config

def schedule_task(task_file):
    config = load_task_config(task_file)
    scheduler = BlockingScheduler()
    hour, minute = map(int, config["run_time"].split(":"))

    scheduler.add_job(
        lambda: run_spider(config["project"], config["spider"]),
        trigger="cron", hour=hour, minute=minute
    )
    scheduler.start()
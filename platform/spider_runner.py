import subprocess
import os

def run_spider(project_name: str, spider_name: str):
    project_path = os.path.join(os.getcwd(), "spiders", project_name)
    cmd = f"cd {project_path} && scrapy crawl {spider_name}"
    subprocess.run(cmd, shell=True)
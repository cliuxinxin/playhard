import os
import json

def run_sjpl():
    print("模拟抓取 San Jose 图书馆活动数据...")
    raw_data = [
        {
            "title": "Toddler Storytime",
            "date": "June 15, 2025",
            "time": "10:30 AM - 11:00 AM",
            "description": "Free storytime for toddlers aged 1-3. No registration required.",
            "url": "https://events.sjpl.org/event/123456"
        }
    ]
    os.makedirs("../data/raw", exist_ok=True)
    with open("../data/raw/sjpl.json", "w") as f:
        json.dump(raw_data, f, indent=2)

if __name__ == "__main__":
    run_sjpl()
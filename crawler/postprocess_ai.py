def mock_ai_clean(raw_item):
    return {
        "title": raw_item["title"],
        "city": "San Jose",
        "venue": "San Jose Library",
        "address": "Main Branch",
        "start_time": "2025-06-15 10:30",
        "end_time": "2025-06-15 11:00",
        "age_range": "1-3",
        "tags": ["storytime", "free"],
        "url": raw_item["url"],
        "is_free": True,
        "requires_registration": False
    }
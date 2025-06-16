我想做一个系统，这个系统有几个核心功能，下载网页，解析网页，数据规整落库
1. 下载网页
1.1 定期调度下载网页
1.2 不同的网页有不同的下载策略，每个网页的翻页机制不一样
1.3 知道自己应该下载到那里就更新完毕
1.4 下载失败需要重试和报警机制
2. 解析网页
2.1 不同的网页有不同的解析策略
2.2 解析的调度，下载完成以后解析最新的数据
2.3 解析失败需要重试和报警机制
3. 数据落库
3.1 落库的调度，解析完成以后落库
3.2 不同的网页有不同的落库策略
3.3 落库失败需要重试和报警机制
4. 先用这个网页来做一个demo
4.1 并且可以扩展到其他的网页å

现在我已经做了数据的抓取和解析，现在需要落库，这是我的数据库设计

Activity = {
    "title": "Toddler Storytime",
    "city": "Cupertino",
    "venue": "Cupertino Public Library",
    "address": "10800 Torre Ave, Cupertino, CA",
    "start_time": "2025-06-10 10:30",
    "end_time": "2025-06-10 11:00",
    "age_range": "0-3",
    "tags": ["storytime", "free", "indoor"],
    "url": "https://...",
    "is_free": True,
    "requires_registration": False,
    "source": "sjpl.org",
    "last_updated": "2025-06-03"
}

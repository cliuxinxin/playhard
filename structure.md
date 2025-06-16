# 架构

          +-----------------------------+
          |      调度与监控中心         |
          |   - cron/airflow/scrapyd    |
          +-----------------------------+
                      |
         +------------+-------------+
         |                          |
  +------v------+          +--------v-------+
  |  多站点配置  |          |  统一Spider入口 |
  | (spider.yaml)|          | (dispatcher.py) |
  +------+-------+          +--------+--------+
         |                           |
  +------v------+     +-------------v-----------+
  | 各站点策略spider |--> 解析 + Item + 翻页策略 |
  +-------------+     +-------------------------+
                             |
                     +-------v--------+
                     |   ItemPipeline |
                     | - 清洗         |
                     | - 存库         |
                     | - 去重         |
                     +----------------+



# 模块划分

1. spiders/：每个网站一个 spider
命名规范如：sjpl_events.py, city_library.py, bayarea_kids.py

每个 spider 实现自己的：

起始请求

翻页逻辑

数据提取逻辑（XPath / CSS / JSON）

动态渲染机制（Playwright/Splash）

python
复制
编辑
class SJPLEventsSpider(SiteSpider):
    name = 'sjpl_events'
    custom_settings = {'USE_PLAYWRIGHT': False}  # 可选

    def start_requests(self):
        yield scrapy.Request(url=self.site_config['start_url'], callback=self.parse)

    def parse(self, response):
        # 数据提取
        ...
        # 翻页逻辑
        ...
2. site_config/：每个网站配置文件（推荐 YAML）
便于非程序员维护，包含字段映射、翻页规则、起始链接、动态渲染设置等。

yaml
复制
编辑
sjpl_events:
  start_url: https://sjpl.bibliocommons.com/v2/events
  pagination: next_link
  render: false
  fields:
    title: "//h1/text()"
    location: "//div[@class='location']/text()"
    ...
3. middlewares/：下载中间件模块
用于：

Header/UA 随机切换

代理池支持

请求重试（对接第三方 API 限速）

4. pipelines/：清洗 + 存储
每一个 Item 进入 Pipeline：

字段标准化（时间格式统一、空字段过滤、HTML 清洗）

存入数据库（如 SQLite / MySQL / MongoDB）

可加“站点来源标识”，方便归档

可添加去重（基于 URL + 标题）

python
复制
编辑
class NormalizePipeline:
    def process_item(self, item, spider):
        item['start_time'] = parse_time(item['start_time'])
        item['location'] = item['location'].strip()
        return item
5. items.py：统一数据结构
python
复制
编辑
class EventItem(scrapy.Item):
    title = scrapy.Field()
    location = scrapy.Field()
    start_time = scrapy.Field()
    category = scrapy.Field()
    source = scrapy.Field()  # 来源站点标识
6. utils/：工具类模块
时间格式化

清洗 HTML

URL 去重/归一

动态渲染支持（Playwright）

# 日志
每个任务自动输出：爬取数量、失败数量、重试次数、时长

保留日志：方便复现与排查问题

# 数据库
本地调试阶段：sqlite

# 目标
新增站点：只需新增 spider + 配置文件

系统自动调度、自动翻页、自动规整数据并存库

支持失败报警、断点续爬、动态渲染、代理限速

前后端解耦，具备“数据中台”能力


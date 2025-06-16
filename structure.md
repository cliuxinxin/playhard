# 项目架构
playhard/
├── README.md
├── requirements.txt
├── scrapy_projects/
│   ├── sjpl_events/           # SJPL 爬虫项目
│   │   ├── scrapy.cfg
│   │   └── sjpl_events/
│   │       ├── __init__.py
│   │       ├── items.py
│   │       ├── settings.py
│   │       ├── parser/
│   │       │   └── sjpl_parser.py
│   │       └── spiders/
│   │           └── sjpl_spider.py
│   └── other_spider/          # 其他爬虫项目
│       ├── scrapy.cfg
│       └── other_spider/
│           ├── __init__.py
│           ├── items.py
│           ├── settings.py
│           └── spiders/
│               └── other_spider.py
├── data/
│   ├── sjpl/                  # SJPL 数据目录
│   │   └── output.json
│   └── other/                 # 其他爬虫数据目录
│       └── output.json
├── scripts/
│   ├── run_all.py            # 运行所有爬虫的脚本
│   └── stats.py              # 数据统计脚本
└── main.py                   # 启动程序

# 模块说明
🧩 各模块职责详解

1. Scrapy 项目
   - 每个爬虫项目独立配置
   - 可以设置不同的爬取策略和参数
   - 支持自定义中间件和管道

2. 爬虫模块
   - 实现数据抓取逻辑
   - 处理分页和请求
   - 调用解析器处理响应
   - 输出结构化数据

3. 解析模块
   - 实现数据解析逻辑
   - 将原始数据转换为结构化格式
   - 提供数据清理和验证

4. 数据模型
   - 定义数据结构
   - 确保数据一致性
   - 提供数据验证

# 运行方式
🛠 运行步骤

1. 运行单个爬虫
```bash
cd scrapy_projects/sjpl_events
scrapy crawl sjpl -o ../../data/sjpl/output.json
```

2. 运行所有爬虫（使用脚本）
```bash
python scripts/run_all.py
```

3. 查看数据统计
```bash
python scripts/stats.py
```

# 数据统计
📊 统计信息

1. 爬虫运行统计
   - 运行时间
   - 请求数量
   - 成功/失败率
   - 数据量统计

2. 数据质量统计
   - 字段完整性
   - 数据有效性
   - 重复数据检测

# 注意事项
⚠️ 重要提示

1. 确保在正确的目录下运行命令
2. 检查 scrapy.cfg 和 settings.py 配置是否正确
3. 确保所有依赖模块都已正确安装
4. 注意爬虫的请求频率和限制
5. 定期检查数据质量和完整性
6. 监控爬虫运行状态和错误日志

# 爬虫管理
🔧 管理功能

1. 爬虫调度
   - 支持定时运行
   - 支持并发控制
   - 支持失败重试

2. 数据管理
   - 数据备份
   - 历史记录
   - 数据清理

3. 监控告警
   - 运行状态监控
   - 错误告警
   - 数据异常检测
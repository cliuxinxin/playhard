# BabyWeekend Data Pipeline

一个面向美国湾区华人妈妈群体的亲子活动推荐数据采集与处理系统，使用 [Crawl4AI](https://github.com/kevin-zou/Crawl4AI) 抓取数据，并结合 LLM 清洗结构化信息，供 App 使用。

## 🧱 项目结构

```
babyweekend-data-pipeline/
├── config/               # 各城市站点抓取规则（YAML）
├── prompts/              # 多个数据清洗用 prompt
├── crawler/              # 抓取执行、AI 清洗、数据入库逻辑
├── data/                 # 保存原始抓取和清洗后的数据
└── app_api/              # 简易 API，供前端/APP 使用
```

## 🚀 快速启动

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行数据抓取：

```bash
python crawler/run_all.py
```

3. 启动本地 API：

```bash
uvicorn app_api.main:app --reload
```

## 🧠 数据清洗说明

在 `crawler/postprocess_ai.py` 中使用 OpenAI API 调用 prompt 提取结构化字段。

## 📂 示例抓取站点

已包含 San Jose 图书馆官网配置：`config/sjpl.yaml`
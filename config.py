from dataclasses import dataclass
from typing import Optional

@dataclass
class PipelineConfig:
    # 基础配置
    max_pages: int = 2
    strategy_name: Optional[str] = None
    
    # 流程控制
    enable_fetch: bool = True        # 是否启用抓取
    enable_parse: bool = True        # 是否启用解析
    enable_save_raw: bool = True     # 是否保存原始数据
    enable_save_parsed: bool = True  # 是否保存解析后的数据
    enable_db_save: bool = True      # 是否保存到数据库
    enable_logging: bool = True      # 是否启用日志打印
    enable_detail_download: bool = True  # 是否下载详情页
    
    # 输出配置
    raw_dir: str = "downloads/{strategy_name}/raw"
    parsed_dir: str = "downloads/{strategy_name}/parsed"
    detail_dir: str = "downloads/{strategy_name}/detail"  # 详情页存储目录

MAX_CONCURRENCY = 10  # 并发任务数量
RATE_LIMIT_QPS = 100  # 每秒最大请求数
MAX_RETRIES = 3       # 最大重试次数
RETRY_BACKOFF = 1     # 初始退避时间（秒）
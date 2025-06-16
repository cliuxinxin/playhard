import json
from downloader.notifier import notify

def save_json(data, filename, strategy_name=None):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        notify(f"{strategy_name+': ' if strategy_name else ''}已保存为 {filename}")
        return True
    except Exception as e:
        notify(f"{strategy_name+': ' if strategy_name else ''}保存 {filename} 失败: {e}")
        return False
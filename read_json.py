import json
from typing import Any, Dict, List

def analyze_json_structure(data: Any, path: str = "") -> None:
    """分析JSON结构并打印主要信息"""
    if isinstance(data, dict):
        print(f"\n{path} (字典) 包含以下键:")
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"  - {key}: {type(value).__name__}")
                analyze_json_structure(value, f"{path}.{key}")
            else:
                print(f"  - {key}: {type(value).__name__} = {value}")
    elif isinstance(data, list):
        if len(data) > 0:
            print(f"\n{path} (列表) 包含 {len(data)} 个元素")
            print(f"第一个元素的类型: {type(data[0]).__name__}")
            if isinstance(data[0], (dict, list)):
                analyze_json_structure(data[0], f"{path}[0]")
        else:
            print(f"\n{path} (空列表)")

def main():
    try:
        # 读取JSON文件
        with open('sjpl.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print("JSON文件结构分析:")
        print("=" * 50)
        analyze_json_structure(data)
        
    except FileNotFoundError:
        print("错误: 找不到sjpl.json文件")
    except json.JSONDecodeError:
        print("错误: JSON文件格式不正确")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
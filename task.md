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

现在我已经有个爬虫的程序了，帮我基于这个扩展一下，实现上面的目标，第一步就是实现下载部分的功能，其他部先弄好架构就好了，下载的时候需要控制速度，不要超过1000次每秒，并且要支持并发，并且要支持重试和报警机制
import requests
import json
import time

def fetch_bibliocommons_events(page, limit=20):
    """
    从 Bibliocommons Gateway API 获取指定页码的活动数据。

    Args:
        page (int): 要获取的页码。
        limit (int): 每页的活动数量。

    Returns:
        dict: 包含活动数据（如果成功）或错误信息。
    """
    url = 'https://gateway.bibliocommons.com/v2/libraries/sjpl/events/search'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
        'Origin': 'https://sjpl.bibliocommons.com',
        'Priority': 'u=1, i',
        'Referer': 'https://sjpl.bibliocommons.com/',
        'Sec-Ch-Ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }
    cookies = {
        'branch': '%7B%22ip%22%3A%22128.199.14.41%22%2C%22sjpl%22%3Anull%7D',
        'NERF_SRV': 'nerf16',
        'SRV': 'app34',
        'EVENT': 'app04b',
    }
    params = {
        'page': page,
        'limit': limit,
        'locale': 'en-US',
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, params=params)
        response.raise_for_status()  # 如果请求不成功，将引发 HTTPError

        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred on page {page}: {http_err}")
        return {"error": f"HTTP error occurred on page {page}: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred on page {page}: {req_err}")
        return {"error": f"Request error occurred on page {page}: {req_err}"}
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error on page {page}: {json_err}. Response content: {response.text[:200]}...") # 打印部分响应内容以帮助调试
        return {"error": f"JSON decode error on page {page}: {json_err}"}

def scrape_all_bibliocommons_events(initial_limit=20):
    """
    爬取所有 Bibliocommons 活动数据。

    Args:
        initial_limit (int): 首次请求时每页的活动数量。

    Returns:
        list: 包含所有提取到的事件数据的列表。
    """
    all_events_data = []
    current_page = 1
    total_pages = 1 # 初始设置为1，将在第一次请求后更新

    print("Starting to scrape all Bibliocommons events...")

    while current_page <= total_pages:
        print(f"Fetching page {current_page}/{total_pages}...")
        page_data = fetch_bibliocommons_events(current_page, initial_limit)

        if page_data and "events" in page_data:
            events_info = page_data["events"]

            # 更新总页数
            if "pagination" in events_info:
                total_pages = events_info["pagination"]["pages"]

            # 提取事件详情
            if "results" in events_info and "entities" in page_data and "events" in page_data["entities"]:
                for event_id in events_info["results"]:
                    event_details = page_data["entities"]["events"].get(event_id)
                    if event_details:
                        # 提取你感兴趣的所有字段
                        extracted_event = {
                            "id": event_details.get("id"),
                            "key": event_details.get("key"),
                            "seriesId": event_details.get("seriesId"),
                            "title": event_details["definition"].get("title"),
                            "description": event_details["definition"].get("description"),
                            "start_time": event_details["definition"].get("start"),
                            "end_time": event_details["definition"].get("end"),
                            "branchLocationId": event_details["definition"].get("branchLocationId"),
                            "locationDetails": event_details["definition"].get("locationDetails"),
                            "audienceIds": event_details["definition"].get("audienceIds", []),
                            "languageIds": event_details["definition"].get("languageIds", []),
                            "programId": event_details["definition"].get("programId"),
                            "typeIds": event_details["definition"].get("typeIds", []),
                            "isVirtual": event_details["definition"].get("isVirtual", False),
                            "isCancelled": event_details["definition"].get("isCancelled", False),
                            "contact_name": event_details["definition"].get("contact", {}).get("name"),
                            "contact_email": event_details["definition"].get("contact", {}).get("email", {}).get("value"),
                            "contact_phone": event_details["definition"].get("contact", {}).get("phone", {}).get("value"),
                            "isFull": event_details.get("isFull", False),
                            "registrationClosed": event_details.get("registrationClosed", False),
                            "numberRegistered": event_details.get("numberRegistered"),
                            "numberWaitlistRegistered": event_details.get("numberWaitlistRegistered"),
                            # 你可以根据需要添加更多字段
                        }
                        all_events_data.append(extracted_event)
            else:
                print(f"No results or entities.events found on page {current_page}.")
        elif page_data and "error" in page_data:
            print(f"Error fetching page {current_page}: {page_data['error']}")
            break # 遇到错误则停止
        else:
            print(f"No data returned for page {current_page}. Stopping.")
            break # 没有数据则停止

        current_page += 1
        # 为了避免对服务器造成过大压力，每次请求后等待一段时间
        if current_page <= total_pages: # 只有在还有更多页面时才等待
            time.sleep(1) # 1秒的延迟，可以根据需要调整

    print(f"Finished scraping. Total events extracted: {len(all_events_data)}")
    return all_events_data

if __name__ == "__main__":
    extracted_data = scrape_all_bibliocommons_events(initial_limit=50) # 可以增加每页的限制以减少请求次数

    # 将数据保存到 JSON 文件
    output_filename = "bibliocommons_events.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)
    print(f"All extracted event data saved to {output_filename}")

    # 打印前5个事件的标题和开始时间作为示例
    if extracted_data:
        print("\n--- First 5 extracted events (Title and Start Time) ---")
        for i, event in enumerate(extracted_data[:5]):
            print(f"{i+1}. Title: {event.get('title', 'N/A')}")
            print(f"   Start Time: {event.get('start_time', 'N/A')}")
            print("-" * 30)
    else:
        print("No events were extracted.")
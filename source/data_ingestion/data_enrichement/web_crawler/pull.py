import requests
import os
import json
from pathlib import Path
import time


def get_existing_offsets():
    files = Path(".").glob("carnegie_data_*.json")
    offsets = []
    for f in files:
        try:
            offset = int(f.stem.split("_")[-1])
            offsets.append(offset)
        except:
            continue
    return sorted(offsets)


def save_chunk(data, offset):
    filename = f"carnegie_data_{offset}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存文件: {filename}")


def fetch_sparql_data():
    endpoint = "https://data.carnegiehall.org/sparql/"
    headers = {
        "Accept": "application/sparql-results+json,*/*;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "data.carnegiehall.org",
        "Origin": "https://data.carnegiehall.org",
        "Referer": "https://data.carnegiehall.org/sparql/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    }

    cookies = {
        "_gid": "GA1.2.32874385.1738724542",
        "_gat_gtag_UA_2067858_22": "1",
        "_ga_X251FGTHG0": "GS1.1.1738724541.14.1.1738726327.0.0.0",
        "_ga": "GA1.1.610338854.1734055248"
    }
    chunk_size = 10000
    save_interval = 10000
    max_retries = 3
    existing_offsets = get_existing_offsets()
    initial_offset = existing_offsets[-1] + \
        save_interval if existing_offsets else 0
    offset = initial_offset

    while True:
        current_file_offset = offset - (offset % save_interval)
        if current_file_offset in existing_offsets:
            print(f"跳过已存在的offset: {offset}")
            offset += chunk_size
            continue

        query = f"""
        SELECT DISTINCT ?object
        WHERE {{
          ?subject ?predicate ?object .
        }}
        ORDER BY ?object
        LIMIT {chunk_size}
        OFFSET {offset}
        """

        data = {"query": query}
        current_chunk = []

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    endpoint, headers=headers, cookies=cookies, data=data)
                if response.status_code != 200:
                    raise ValueError(f"HTTP错误 {response.status_code}")

                json_data = response.json()
                current_chunk = json_data['results']['bindings']
                break
            except Exception as e:
                time.sleep(10 * attempt)
                print(f"请求失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    return
                continue

        if not current_chunk:
            print("没有更多数据")
            break

        all_data = []
        all_data.extend(current_chunk)

        if (offset + chunk_size) % save_interval == 0:
            save_chunk(all_data, current_file_offset)
            all_data = []

        offset += chunk_size
        print(f"当前进度: {offset} 条")

    if all_data:
        save_chunk(all_data, current_file_offset)


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    os.chdir("data")
    fetch_sparql_data()
    print("数据抓取完成")

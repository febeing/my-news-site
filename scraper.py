import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 超时设置，保持高效
socket.setdefaulttimeout(15)

SOURCES = {
    # 顽固信源（使用 RSSHub 中转）
    "Nature Careers": "https://rsshub.app/nature/careers/scientific-community",
    "Science Careers": "https://rsshub.app/science/careers",
    "Reuters AI": "https://rsshub.app/reuters/technology/artificial-intelligence",
    "联合早报 (实时)": "https://rsshub.app/zaobao/realtime/china",
    "Scientific American": "https://rsshub.app/scientificamerican/latest",
    "Inside Higher Ed": "https://rsshub.app/insidehighered/news",
    
    # 标准 RSS 信源
    "SCMP (南华早报)": "https://www.scmp.com/rss/318217/feed",
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "New Scientist": "https://www.newscientist.com/section/news/feed/",
    "VnExpress": "https://e.vnexpress.net/rss/news.rss"
}

def run_scraper():
    all_results = {}
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]

    for name, url in SOURCES.items():
        print(f">>> 正在处理: {name}")
        headers = {'User-Agent': random.choice(ua_list)}
        
        try:
            articles = []
            # 统一使用 requests + feedparser 模式
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    
                    # 提取摘要并清理 HTML
                    raw_summary = entry.get("summary", entry.get("description", "点击查看原文详情"))
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:130] + "..."
                    
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "date": date_str,
                        "summary": clean_summary
                    })

            if articles:
                all_results[name] = articles
                print(f"✅ {name} 成功！当前累计有效板块: {len(all_results)}")
            else:
                print(f"⚠️ {name} 抓取结果为空")

        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            continue

    # 最终保存
    print(f"--- 任务结束，准备写入文件 ---")
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"写入成功，共计 {len(all_results)} 个信源。")

if __name__ == "__main__":
    run_scraper()

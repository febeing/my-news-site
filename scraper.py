import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 超时设置，保持高效
socket.setdefaulttimeout(20)

SOURCES = {
    # 顽固信源：改用原始 RSS 或 Google News 镜像绕过封锁
    "Nature Careers": "https://www.nature.com/naturecareers/articles.rss",
    "Science Careers": "https://www.science.org/rss/careers.xml",
    "Reuters AI": "https://news.google.com/rss/search?q=Reuters+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "联合早报 (实时)": "https://www.zaobao.com.sg/realtime/china/rss",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    "Inside Higher Ed": "https://www.insidehighered.com/feed",
    
    # 稳定信源
    "SCMP (南华早报)": "https://www.scmp.com/rss/318217/feed",
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "New Scientist": "https://www.newscientist.com/section/news/feed/",
    "VnExpress": "https://e.vnexpress.net/rss/news.rss"
}

def run_scraper():
    all_results = {}
    # 更加真实的浏览器请求头
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ]

    for name, url in SOURCES.items():
        print(f">>> 正在同步: {name}")
        headers = {
            'User-Agent': random.choice(ua_list),
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        try:
            articles = []
            # 统一使用 requests 先获取，再用 feedparser 解析
            resp = requests.get(url, headers=headers, timeout=20)
            
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                # 如果普通解析失败，尝试直接解析 text
                if not feed.entries:
                    feed = feedparser.parse(resp.text)

                for entry in feed.entries[:5]:
                    # 提取日期
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    
                    # 提取标题和链接
                    title = entry.get("title", "无题")
                    link = entry.get("link", "")
                    
                    # 提取摘要并清理 HTML 标签
                    raw_summary = entry.get("summary", entry.get("description", "点击查看原文详情"))
                    # 使用 BeautifulSoup 清理 HTML 内容
                    soup = BeautifulSoup(raw_summary, "html.parser")
                    clean_summary = soup.get_text()[:130] + "..."
                    
                    articles.append({
                        "title": title,
                        "link": link,
                        "date": date_str,
                        "summary": clean_summary
                    })

            if articles:
                all_results[name] = articles
                print(f"✅ {name} 成功！目前有效板块数: {len(all_results)}")
            else:
                print(f"⚠️ {name} 抓取结果为空 (Status: {resp.status_code})")

        except Exception as e:
            print(f"❌ {name} 出错: {e}")
            continue

    # 最终保存到 news.json
    print(f"--- 所有同步任务结束 ---")
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"写入完成，最终获得 {len(all_results)} 个信源数据。")

if __name__ == "__main__":
    run_scraper()

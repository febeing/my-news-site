import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

socket.setdefaulttimeout(20)

SOURCES = {
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    "Nature Careers": "https://www.nature.com/naturecareers/articles.rss",
    "Inside Higher Ed": "https://www.insidehighered.com/feed",
    "The Chronicle of Higher Ed": "https://www.chronicle.com/section/news.rss",
    "Reuters AI": "https://news.google.com/rss/search?q=Reuters+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "MIT Tech Review": "https://news.google.com/rss/search?q=MIT+Technology+Review&hl=en-US",
    "The Guardian Edu": "https://www.theguardian.com/education/rss",
    "SCMP Hong Kong": "https://www.scmp.com/rss/2/feed",
    "联合早报 (中国)": "https://www.zaobao.com.sg/realtime/china/rss",
    "New Scientist": "https://www.newscientist.com/section/news/feed/",
    "VnExpress Global": "https://e.vnexpress.net/rss/news.rss"
}

def run_scraper():
    all_results = {}
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]

    for name, url in SOURCES.items():
        print(f">>> 正在同步: {name}")
        # 随机休眠防封
        time.sleep(random.uniform(1.0, 2.5))
        headers = {'User-Agent': random.choice(ua_list), 'Accept-Language': 'en-US,en;q=0.9'}
        
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                articles = []
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    
                    raw_summary = entry.get("summary", entry.get("description", "点击查看详情"))
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:140] + "..."
                    
                    articles.append({
                        "title": entry.get("title", "无题"),
                        "link": entry.get("link", ""),
                        "date": date_str,
                        "summary": clean_summary
                    })
                
                if articles:
                    all_results[name] = articles
                    print(f"✅ {name} 成功！当前累计: {len(all_results)}")
        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            continue

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"写入完成，共计 {len(all_results)} 个信源。")

if __name__ == "__main__":
    run_scraper()

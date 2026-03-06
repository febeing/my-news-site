import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 超时设置
socket.setdefaulttimeout(20)

SOURCES = {
    # --- 顶级名校 (运行稳定) ---
    "MIT News": "https://news.mit.edu/rss/topic/research",
    "Harvard Gazette": "https://news.google.com/rss/search?q=Harvard+University+source:Harvard+Gazette&hl=en-US",
    "Stanford News": "https://news.google.com/rss/search?q=Stanford+University+News&hl=en-US",
    
    # --- 修复后的学术 & 职业 (重点修复 404) ---
    "Nature Careers": "https://www.nature.com/nature/articles.rss?type=nature-jobs", # 修复后的路径
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Scientific American": "https://www.scientificamerican.com/rss/all/", # 修复后的路径
    
    # --- 科技 & AI ---
    "Reuters AI": "https://news.google.com/rss/search?q=Reuters+Artificial+Intelligence&hl=en-US",
    "MIT Tech Review": "https://news.google.com/rss/search?q=MIT+Technology+Review&hl=en-US",
    "Phys.org": "https://phys.org/rss-feed/",
    
    # --- 修复后的高等教育政策 ---
    "Inside Higher Ed": "https://www.insidehighered.com/rss/news", # 修复后的路径
    "The Chronicle": "https://www.chronicle.com/rss", # 修复后的路径
    "The Guardian Edu": "https://www.theguardian.com/education/rss",
    
    # --- 综合 & 实时 ---
    "SCMP Hong Kong": "https://www.scmp.com/rss/2/feed",
    "联合早报 (实时)": "https://www.zaobao.com.sg/rss/realtime/china", # 修复后的路径
    "New Scientist": "https://www.newscientist.com/section/news/feed/"
}

def run_scraper():
    all_results = {}
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]

    for name, url in SOURCES.items():
        print(f">>> 正在同步: {name}")
        time.sleep(random.uniform(1.5, 2.5))
        headers = {'User-Agent': random.choice(ua_list), 'Accept': 'application/rss+xml, application/xml, text/xml, */*'}
        
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                articles = []
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    
                    raw_summary = entry.get("summary", entry.get("description", "点击查看原文"))
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:130] + "..."
                    
                    articles.append({
                        "title": entry.get("title", "无题"),
                        "link": entry.get("link", "#"),
                        "date": date_str,
                        "summary": clean_summary
                    })
                
                if articles:
                    all_results[name] = articles
                    print(f"✅ {name} 成功！当前累计: {len(all_results)}")
            else:
                print(f"❌ {name} 失败 (状态码: {resp.status_code})")
        except Exception as e:
            print(f"❌ {name} 错误: {e}")
            continue

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"🎉 任务完成！共计 {len(all_results)} 个信源数据。")

if __name__ == "__main__":
    run_scraper()

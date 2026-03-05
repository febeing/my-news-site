import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 超时时间设短一点，15秒不回话就“分手”，不耽误下一个
socket.setdefaulttimeout(15)

SOURCES = {
    "Nature Careers": "https://www.nature.com/naturecareers/articles.rss",
    "Science Careers": "https://www.science.org/rss/careers.xml",
    "SCMP (南华早报)": "https://www.scmp.com/rss/318217/feed",
    "Reuters AI (路透社)": "https://www.reuters.com/arc/outboundfeeds/v1/topic/technology/artificial-intelligence/?size=10",
    "联合早报 (实时)": "https://www.zaobao.com.sg/realtime/rss",
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    "Inside Higher Ed": "https://www.insidehighered.com/feed",
    "NSFC (自然科学基金委)": "https://www.nsfc.gov.cn/p1/3381/2822/tzsm1.html",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "New Scientist": "https://www.newscientist.com/section/news/feed/",
    "VnExpress": "https://e.vnexpress.net/rss/news.rss"
}

def run_scraper():
    # 1. 先尝试读取现有的数据，实现增量更新
    try:
        with open('news.json', 'r', encoding='utf-8') as f:
            structured_data = json.load(f)
    except:
        structured_data = {}

    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]

    for name, url in SOURCES.items():
        print(f">>> 尝试同步: {name}")
        headers = {'User-Agent': random.choice(ua_list)}
        
        try:
            articles = []
            # 特殊处理 NSFC
            if "nsfc.gov.cn" in url:
                resp = requests.get(url, headers=headers, timeout=15)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.select(".main-list li a") or soup.select(".list-txt li a")
                for a in links[:5]:
                    articles.append({"title": a.text.strip(), "link": "https://www.nsfc.gov.cn" + a['href'], "date": "官方发布", "summary": "项目通知。"})
            else:
                # 处理 RSS
                resp = requests.get(url, headers=headers, timeout=20)
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    raw_summary = entry.get("summary", entry.get("description", "查看原文"))
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:120] + "..."
                    articles.append({"title": entry.title, "link": entry.link, "date": date_str, "summary": clean_summary})

            if articles:
                structured_data[name] = articles
                # 【核心】：抓完一个存一个，不留遗憾
                with open('news.json', 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, ensure_ascii=False, indent=2)
                print(f"✅ {name} 成功，目前总计: {len(structured_data)} 个板块")

        except Exception as e:
            print(f"❌ {name} 失败: {e}，跳过看下一个")
            continue

if __name__ == "__main__":
    run_scraper()

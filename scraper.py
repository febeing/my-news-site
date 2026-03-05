import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 超时缩短，快速跳过不响应的
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
    # 核心修正：初始化一个空的字典来装载所有成功的信源
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
            # 1. NSFC 特殊处理
            if "nsfc.gov.cn" in url:
                resp = requests.get(url, headers=headers, timeout=15)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.select(".main-list li a") or soup.select(".list-txt li a")
                for a in links[:5]:
                    articles.append({"title": a.text.strip(), "link": "https://www.nsfc.gov.cn" + a['href'], "date": "官方发布", "summary": "项目通知。"})
            # 2. RSS 处理
            else:
                resp = requests.get(url, headers=headers, timeout=15)
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    raw_summary = entry.get("summary", entry.get("description", "查看原文"))
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:120] + "..."
                    articles.append({"title": entry.title, "link": entry.link, "date": date_str, "summary": clean_summary})

            # 如果抓到了内容，就存进总字典
            if articles:
                all_results[name] = articles
                print(f"✅ {name} 成功！当前累计有效板块数: {len(all_results)}")
            else:
                print(f"⚠️ {name} 没抓到内容")

        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            continue

    # 3. 循环结束后，一次性写入文件
    print(f"--- 抓取结束，准备保存 ---")
    print(f"最终成功板块列表: {list(all_results.keys())}")
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"文件写入完成，共计 {len(all_results)} 个板块。")

if __name__ == "__main__":
    run_scraper()

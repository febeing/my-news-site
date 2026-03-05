import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 大幅拉长超时时间，给国外网站更多时间响应
socket.setdefaulttimeout(30)

# 确保这 13 个信源一个不少
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
    structured_data = {}
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ]

    for name, url in SOURCES.items():
        print(f"正在尝试抓取: {name}")
        headers = {'User-Agent': random.choice(ua_list)}
        
        try:
            articles = []
            # 1. NSFC 特殊解析
            if "nsfc.gov.cn" in url:
                resp = requests.get(url, headers=headers, timeout=20)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.select(".main-list li a") or soup.select(".list-txt li a")
                for a in links[:5]:
                    articles.append({
                        "title": a.text.strip(),
                        "link": "https://www.nsfc.gov.cn" + a['href'] if a['href'].startswith('/') else a['href'],
                        "date": "官方发布",
                        "summary": "国家自然科学基金委动态。"
                    })
            # 2. 其他 RSS 解析
            else:
                resp = requests.get(url, headers=headers, timeout=25)
                # 核心：即使返回状态码不是200，也尝试解析已获取的内容
                feed = feedparser.parse(resp.content)
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    raw_summary = entry.get("summary", entry.get("description", "点击查看原文"))
                    # 简单去除 HTML 标签
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:120] + "..."
                    
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "date": date_str,
                        "summary": clean_summary
                    })

            if articles:
                structured_data[name] = articles
                print(f"✅ {name} 抓取成功，目前累计板块: {len(structured_data)}")
            else:
                print(f"⚠️ {name} 抓取结果为空")

        except Exception as e:
            # 即使某个报错了，也要记录错误原因，并继续下一个，不要崩溃
            print(f"❌ {name} 遇到严重错误: {e}")
            continue

    # 3. 最终存盘
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    print(f"任务结束，共保存 {len(structured_data)} 个信源。")

if __name__ == "__main__":
    run_scraper()

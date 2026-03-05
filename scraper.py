import feedparser
import json
import socket

# 设置全局超市，防止卡死
socket.setdefaulttimeout(10) 

SOURCES = {
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    "The Crimson": "https://www.thecrimson.com/feeds/section/news/",
    "Inside Higher Ed": "https://www.insidehighered.com/feed"
}

def run_scraper():
    all_news = []
    for name, url in SOURCES.items():
        print(f"尝试抓取: {name}")
        try:
            # 加入 timeout 参数，双重保险
            feed = feedparser.parse(url)
            if feed.bozo: # 检查是否解析出错
                print(f"⚠️ {name} 数据格式有问题，跳过")
                continue
                
            for entry in feed.entries[:5]:
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": name,
                    "summary": entry.get("summary", entry.get("description", ""))[:100] + "..."
                })
            print(f"✅ {name} 成功")
        except Exception as e:
            print(f"❌ {name} 超时或失败，跳过")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

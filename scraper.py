import feedparser
import json
import time

# 定义你的信源
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
    print("开始抓取...")
    
    for name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            # 每个信源只取前5条
            for entry in feed.entries[:5]:
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": name,
                    # 简易摘要：取正文前100字
                    "summary": entry.get("summary", entry.get("description", ""))[:100] + "..."
                })
            print(f"✅ {name} 抓取成功")
        except Exception as e:
            print(f"❌ {name} 抓取失败: {e}")

    # 将结果保存为 news.json 供网页读取
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print("全部抓取完成，数据已存入 news.json")

if __name__ == "__main__":
    run_scraper()

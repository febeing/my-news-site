import feedparser
import json
import socket
import os
import requests
from datetime import datetime

socket.setdefaulttimeout(20)

# 补全你提供的所有信源
SOURCES = {
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    "Inside Higher Ed": "https://www.insidehighered.com/feed",
    "The Crimson": "https://www.thecrimson.com/feeds/section/news/",
    "VnExpress": "https://e.vnexpress.net/rss/news.rss",
    "New Scientist": "https://www.newscientist.com/section/news/feed/",
    "Higher Ed Dive": "https://www.highereddive.com/feeds/news/",
}

def get_ai_summary(title, text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "翻译不可用"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"请将学术新闻总结成80字以内的通顺中文摘要。标题: {title} 内容: {text[:400]}"
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except: return "摘要生成失败"

def run_scraper():
    structured_data = {} # 使用字典按来源分类
    
    for name, url in SOURCES.items():
        print(f"正在处理: {name}")
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:5]:
                # 提取时间并格式化
                dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "未知时间"
                
                summary = get_ai_summary(entry.title, entry.get("summary", ""))
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "date": date_str,
                    "summary": summary
                })
            # 按时间倒序排列该板块内的文章
            articles.sort(key=lambda x: x['date'], reverse=True)
            structured_data[name] = articles
        except Exception as e:
            print(f"跳过 {name}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import time
    run_scraper()

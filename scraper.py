import feedparser
import json
import socket
import os
import requests

socket.setdefaulttimeout(15)

# 这里填入你想抓取的信源
SOURCES = {
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    "The Guardian Education": "https://www.theguardian.com/education/rss"
}

def get_ai_summary(title, text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return text[:100] + "..." # 如果没配置Key，回退到普通截取
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"请将以下学术新闻标题和内容翻译并总结成100字以内的中文摘要。标题: {title} 内容: {text[:500]}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    except:
        return "翻译暂不可用: " + text[:100]

def run_scraper():
    all_news = []
    for name, url in SOURCES.items():
        print(f"抓取并翻译: {name}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                # 调用 AI 进行摘要和翻译
                summary = get_ai_summary(entry.title, entry.get("summary", entry.get("description", "")))
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": name,
                    "summary": summary
                })
        except Exception as e:
            print(f"跳过 {name}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

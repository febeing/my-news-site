import feedparser
import json
import socket
import os
import requests
import time
from datetime import datetime

# 设置超时
socket.setdefaulttimeout(30)

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
    if not api_key:
        return "错误：未配置 API KEY"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # 限制内容长度，防止内容过长导致请求失败
    clean_text = text[:800].replace('"', "'")
    prompt = f"请将学术新闻总结成80字以内的通顺中文。标题: {title} 内容: {clean_text}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # 增加延迟，避免触发频率限制
        time.sleep(2) 
        response = requests.post(url, json=payload, timeout=20)
        res_json = response.json()
        
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"AI 报错详情: {res_json}") # 可以在 Action 日志里看到报错
            return "摘要解析失败，请检查 API 额度"
    except Exception as e:
        print(f"请求异常: {e}")
        return "连接 AI 超时"

def run_scraper():
    structured_data = {}
    
    for name, url in SOURCES.items():
        print(f"正在抓取: {name}")
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:5]:
                # 尝试获取多种格式的时间
                dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "最近发布"
                
                # 获取正文：尝试读取 content 或 summary
                content_text = ""
                if 'content' in entry:
                    content_text = entry.content[0].value
                else:
                    content_text = entry.get("summary", "")

                summary = get_ai_summary(entry.title, content_text)
                
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "date": date_str,
                    "summary": summary
                })
            
            # 内部按时间倒序
            articles.sort(key=lambda x: x['date'], reverse=True)
            structured_data[name] = articles
            print(f"✅ {name} 完成")
        except Exception as e:
            print(f"❌ {name} 失败: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

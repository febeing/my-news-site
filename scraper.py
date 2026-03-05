import feedparser
import json
import socket
import os
import requests
import time

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
    # 默认摘要（如果AI坏了，就用这个）
    default_summary = text[:150].strip() + "..." if text else "点击查看原文详情。"
    
    if not api_key:
        return default_summary
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    clean_text = text[:600].replace('"', "'")
    prompt = f"请将学术新闻总结成80字以内的通顺中文。标题: {title} 内容: {clean_text}"
    
    try:
        # 增加到 4 秒延迟，彻底避开每分钟 15 次的频率限制
        time.sleep(4) 
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        res_json = response.json()
        
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            # 如果 AI 报额度错误，直接回退到英文原始摘要
            return default_summary
    except:
        return default_summary

def run_scraper():
    structured_data = {}
    for name, url in SOURCES.items():
        print(f"正在抓取: {name}")
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:5]:
                dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "Recently"
                
                raw_content = entry.get("summary", entry.get("description", ""))
                summary = get_ai_summary(entry.title, raw_content)
                
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "date": date_str,
                    "summary": summary
                })
            articles.sort(key=lambda x: x['date'], reverse=True)
            structured_data[name] = articles
        except Exception as e:
            print(f"跳过 {name}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

import feedparser
import json
import socket
import os
import requests
import time

# 设置全局超时
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
    # 默认截取作为保底
    default_text = (text[:150] + "...") if text else "点击查看原文详情。"
    
    if not api_key:
        return default_text
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # 预处理文本
    clean_text = text[:600].replace('"', "'") if text else ""
    prompt = f"请将以下学术新闻总结成80字以内的通顺中文。标题: {title} 内容: {clean_text}"
    
    try:
        time.sleep(4) # 严格控制频率，每分钟不超过15次
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return default_text
    except:
        return default_text

def run_scraper():
    structured_data = {}
    # 模拟浏览器头，防止被屏蔽
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for name, url in SOURCES.items():
        print(f"正在处理: {name}")
        try:
            # 使用 requests 先获取内容，再交给 feedparser 解析，这样更稳定
            resp = requests.get(url, headers=headers, timeout=20)
            feed = feedparser.parse(resp.content)
            
            articles = []
            for entry in feed.entries[:5]:
                # 尝试抓取时间
                dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "最近发布"
                
                # 强化内容提取逻辑
                raw_content = ""
                if 'content' in entry:
                    raw_content = entry.content[0].value
                elif 'description' in entry:
                    raw_content = entry.description
                else:
                    raw_content = entry.get("summary", "")

                summary = get_ai_summary(entry.title, raw_content)
                
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "date": date_str,
                    "summary": summary
                })
            
            if articles:
                articles.sort(key=lambda x: x['date'], reverse=True)
                structured_data[name] = articles
                print(f"✅ {name} 成功抓取 {len(articles)} 条")
            else:
                print(f"⚠️ {name} 抓取结果为空")
                
        except Exception as e:
            print(f"❌ {name} 失败: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

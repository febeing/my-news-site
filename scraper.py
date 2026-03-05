import feedparser
import json
import socket
import os
import requests
import time

# 设置全局超时
socket.setdefaulttimeout(30)

# 1. 这里就是你以后增加新信源的地方
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
    "The Chronicle of Higher Ed": "https://www.chronicle.com/section/news.rss",
    "The College Fix": "https://www.thecollegefix.com/feed/",
    "Campus Reform": "https://www.campusreform.org/rss",
    "Academic Jobs": "https://www.academicjobs.com/higher-education-news/rss.xml",
    "NSFC (自然科学基金委)": "https://www.nsfc.gov.cn/p1/3381/2822/tzsm1.html", # 网页版
}

def get_ai_summary(title, text):
    api_key = os.getenv("GEMINI_API_KEY")
    default_text = (text[:150] + "...") if text else "点击查看详情。"
    if not api_key: return default_text
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    clean_text = text[:600].replace('"', "'") if text else ""
    prompt = f"你是一个高等教育资深编辑。请将新闻总结成80字以内中文。标题: {title} 内容: {clean_text}"
    
    try:
        time.sleep(4) # 严格控制频率
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return default_text
    except:
        return default_text

def run_scraper():
    structured_data = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for name, url in SOURCES.items():
        print(f"正在处理: {name}")
        try:
            # 针对 NSFC 这种非 RSS 的网页做特殊处理
            if "nsfc.gov.cn" in url:
                resp = requests.get(url, headers=headers, timeout=20)
                resp.encoding = 'utf-8'
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select(".main-list li")[:5]
                articles = []
                for item in items:
                    a = item.find('a')
                    articles.append({
                        "title": a.text.strip(),
                        "link": "https://www.nsfc.gov.cn" + a['href'],
                        "date": "官方发布",
                        "summary": "中国自然科学基金委最新通知公告。"
                    })
                structured_data[name] = articles
                continue

            # 普通 RSS 处理
            resp = requests.get(url, headers=headers, timeout=20)
            feed = feedparser.parse(resp.content)
            articles = []
            for entry in feed.entries[:5]:
                dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期发布"
                raw_content = entry.get("summary", entry.get("description", ""))
                summary = get_ai_summary(entry.title, raw_content)
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "date": date_str,
                    "summary": summary
                })
            if articles:
                structured_data[name] = articles
        except Exception as e:
            print(f"跳过 {name}: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

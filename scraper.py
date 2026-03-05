import feedparser
import json
import socket
import os
import requests
import time
from bs4 import BeautifulSoup

# 增加超时容忍度
socket.setdefaulttimeout(35)

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

def get_ai_summary(title, text):
    api_key = os.getenv("GEMINI_API_KEY")
    default_text = (text[:120] + "...") if text else "点击查看详情。"
    if not api_key: return default_text
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    # 缩短发送内容，降低负载
    clean_text = text[:400].replace('"', "'") if text else ""
    prompt = f"翻译并总结成80字以内中文: {title} 内容: {clean_text}"
    
    try:
        # 严格限制：每 5 秒发一次请求，彻底避开 15RPM 限制
        time.sleep(5) 
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=25)
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
        print(f">>> 正在同步: {name}")
        try:
            # 针对不同类型的信源分别处理
            if "nsfc.gov.cn" in url:
                resp = requests.get(url, headers=headers, timeout=25)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.select(".main-list li a") or soup.select(".list-txt li a")
                articles = []
                for a in links[:5]:
                    articles.append({
                        "title": a.text.strip(),
                        "link": "https://www.nsfc.gov.cn" + a['href'] if a['href'].startswith('/') else a['href'],
                        "date": "官方发布",
                        "summary": "国家自然科学基金委最新通知与项目动态。"
                    })
                if articles: structured_data[name] = articles
            else:
                resp = requests.get(url, headers=headers, timeout=25)
                feed = feedparser.parse(resp.content)
                articles = []
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    summary = get_ai_summary(entry.title, entry.get("summary", entry.get("description", "")))
                    articles.append({"title": entry.title, "link": entry.link, "date": date_str, "summary": summary})
                if articles: structured_data[name] = articles
                
            # 每抓完一个信源，实时打印进度，防止 Actions 误判为卡死
            print(f"✅ {name} 同步成功，当前总板块数: {len(structured_data)}")

        except Exception as e:
            print(f"❌ {name} 遇到错误跳过: {e}")
            continue # 核心：即便一个信源失败，也要继续下一个

    # 最终保存
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

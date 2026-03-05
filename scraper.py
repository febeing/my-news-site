import feedparser
import json
import socket
import os
import requests
import time
from bs4 import BeautifulSoup

# 设置全局超时
socket.setdefaulttimeout(30)

# 全量信源字典
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
    # 基础截取保底
    default_text = (text[:150] + "...") if text else "点击链接查看原文详情。"
    if not api_key: return default_text
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    clean_text = text[:600].replace('"', "'") if text else ""
    prompt = f"你是一位科研资深编辑。请将新闻标题和内容翻译并总结成80字以内通顺中文。标题: {title} 内容: {clean_text}"
    
    try:
        # 频率控制：每分钟约 12-15 次请求
        time.sleep(4.5) 
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return default_text
    except:
        return default_text

def run_scraper():
    structured_data = {}
    # 模拟浏览器身份
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
    }

    for name, url in SOURCES.items():
        print(f"正在同步: {name}")
        try:
            # 1. 处理非 RSS 网页 (NSFC)
            if "nsfc.gov.cn" in url:
                resp = requests.get(url, headers=headers, timeout=20)
                resp.encoding = 'utf-8'
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.select(".main-list li a") or soup.select(".list-txt li a")
                articles = []
                for a in links[:5]:
                    articles.append({
                        "title": a.text.strip(),
                        "link": "https://www.nsfc.gov.cn" + a['href'] if a['href'].startswith('/') else a['href'],
                        "date": "官方发布",
                        "summary": "中国自然科学基金委最新动态、通知及成果公示。"
                    })
                if articles: structured_data[name] = articles
                continue

            # 2. 处理标准 RSS (Nature, Science, Reuters, etc.)
            resp = requests.get(url, headers=headers, timeout=20)
            feed = feedparser.parse(resp.content)
            
            articles = []
            for entry in feed.entries[:5]:
                dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "最近发布"
                
                # 尽量获取完整描述
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
                print(f"✅ {name} 同步成功")
                
        except Exception as e:
            print(f"❌ {name} 失败: {e}")

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_scraper()

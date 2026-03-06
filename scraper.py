import feedparser
import json
import socket
import requests
import time
import random
from bs4 import BeautifulSoup

# 超时设置，防止个别网站卡死整个流程
socket.setdefaulttimeout(20)

SOURCES = {
    # --- 顶级名校 & 研究机构 ---
    "MIT News": "https://news.mit.edu/rss/topic/research",
    "Harvard Gazette": "https://news.google.com/rss/search?q=Harvard+University+source:Harvard+Gazette&hl=en-US",
    "Stanford News": "https://news.google.com/rss/search?q=Stanford+University+News&hl=en-US",
    
    # --- 学术动态 & 撤稿观察 ---
    "Nature Careers": "https://www.nature.com/naturecareers/articles.rss",
    "Science News": "https://www.science.org/rss/news_current.xml",
    "Retraction Watch": "https://retractionwatch.com/feed/",
    "Scientific American": "https://www.scientificamerican.com/latest/rss",
    
    # --- 科技 & AI 前沿 ---
    "Reuters AI": "https://news.google.com/rss/search?q=Reuters+Artificial+Intelligence&hl=en-US",
    "MIT Tech Review": "https://news.google.com/rss/search?q=MIT+Technology+Review&hl=en-US",
    "Phys.org (物理/科技)": "https://phys.org/rss-feed/",
    
    # --- 高等教育政策 ---
    "Inside Higher Ed": "https://www.insidehighered.com/feed",
    "The Chronicle of Higher Ed": "https://www.chronicle.com/section/news.rss",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    
    # --- 综合 & 实时 ---
    "SCMP Hong Kong": "https://www.scmp.com/rss/2/feed",
    "联合早报 (实时)": "https://www.zaobao.com.sg/realtime/china/rss",
    "New Scientist": "https://www.newscientist.com/section/news/feed/"
}

def run_scraper():
    all_results = {}
    # 扩展浏览器指纹库
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
    ]

    for name, url in SOURCES.items():
        print(f">>> 正在同步信源: {name}")
        # 随机休眠 1-2 秒，模拟真人阅读翻页，降低被封概率
        time.sleep(random.uniform(1.0, 2.0))
        
        headers = {
            'User-Agent': random.choice(ua_list),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        
        try:
            # 统一使用 requests 抓取，处理编码和反爬
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                articles = []
                
                for entry in feed.entries[:5]: # 每个信源取最新的 5 条
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期发布"
                    
                    # 清理摘要中的 HTML 标签
                    raw_summary = entry.get("summary", entry.get("description", "点击标题查看详情"))
                    soup = BeautifulSoup(raw_summary, "html.parser")
                    clean_summary = soup.get_text()[:140] + "..."
                    
                    articles.append({
                        "title": entry.get("title", "无题"),
                        "link": entry.get("link", "#"),
                        "date": date_str,
                        "summary": clean_summary
                    })
                
                if articles:
                    all_results[name] = articles
                    print(f"✅ {name} 成功！当前累计有效板块: {len(all_results)}")
                else:
                    print(f"⚠️ {name} 抓取结果为空")
            else:
                print(f"❌ {name} 访问失败 (状态码: {resp.status_code})")
                
        except Exception as e:
            print(f"❌ {name} 发生错误: {e}")
            continue

    # 将最终合并后的数据写入 JSON
    print(f"--- 抓取结束，准备保存数据 ---")
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"🎉 成功！最终获得 {len(all_results)} 个信源的最新情报。")

if __name__ == "__main__":
    run_scraper()

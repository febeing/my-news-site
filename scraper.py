import   进口   进口实现feedparser feedparser
import   进口   进口json json
import   进口   进口套接字 socket
import   进口   进口的请求 requests
import   进口   导入的时间 time
import   进口   进口随机 random
from从 BeautifulSoup 导入 BeautifulSoup bs4    从import BeautifulSoup

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
    all_results = {}"VnExpress Global": "https://e.vnexpress.net/rss   All_results = {}
ews.rss"
    ua_list = ["New Scientist": "https://www.newscientist.com/section   Ua_list = [
ews/feed/",
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'," Lianhe Zaobao (China) : " https://www.zaobao.com.sg/realtime/china/rss" ,“Mozilla/5.0（Windows NT 10.0；Win64；x64）AppleWebKit/537.36（KHTML，如 Gecko）Chrome/122.0.0.0 Safari/537.36”
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'Mozilla/5.0（Macintosh；Intel Mac OS X 10_15_7）AppleWebKit/537.36（KHTML，如 Gecko）Chrome/121.0.0.0 Safari/537.36
    ]

    for name, url in SOURCES.items():对于名称、网址在来源项中：
        print(f">>> 正在同步: {name}")print(f'>>> Synchronizing: {name}')
        # 随机休眠防封
        time.sleep(random.uniform(1.0, 2.5))
        headers = {'User-Agent': random.choice(ua_list), 'Accept-Language': 'en-US,en;q=0.9'}
        
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
                articles = []
                for entry in feed.entries[:5]:
                    dt = entry.get("published_parsed", entry.get("updated_parsed", None))
                    date_str = time.strftime("%Y-%m-%d %H:%M", dt) if dt else "近期"
                    
                    raw_summary = entry.get("summary", entry.get("description", "点击查看详情"))
                    clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text()[:140] + "..."
                    
                    articles.append({
                        "title": entry.get("title", "无题"),
                        "link": entry.get("link", ""),
                        "date": date_str,
                        "summary": clean_summary
                    })
                
                if articles:
                    all_results[name] = articles
                    print(f"✅ {name} 成功！当前累计: {len(all_results)}")
        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            continue

    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"写入完成，共计 {len(all_results)} 个信源。")

if __name__ == "__main__":
    run_scraper()

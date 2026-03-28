import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def crawl_spiegel_integrated(max_pages=10):
    # 1. 다중 키워드 구성 (독일어 및 영어 포괄)
    # 슈피겔 검색창에 "Anthropozän OR Anthropocene" 형태로 입력하는 것과 동일
    search_keywords = "Anthropozän OR Anthropocene"
    base_url = "https://www.spiegel.de/suche/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    all_articles = []

    try:
        for page in range(1, max_pages + 1):
            # q 파라미터에 통합 쿼리 전달
            params = {
                "q": search_keywords,
                "page": page,
                "sort": "datum" # 최신순 정렬 (필요 시)
            }
            
            print(f"📂 Spiegel {page}페이지 수집 중... (Query: {search_keywords})", flush=True)
            
            try:
                response = requests.get(base_url, params=params, headers=headers, timeout=15)
                if response.status_code != 200:
                    print(f"⚠️ {page}페이지 접속 실패 (Status: {response.status_code})")
                    break
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                items = soup.select("article")
                
                if not items:
                    print("🏁 더 이상 결과가 없습니다.")
                    break

                for item in items:
                    try:
                        # 제목 및 링크
                        title_elem = item.select_one("header h2 a")
                        if not title_elem: continue
                        
                        title = title_elem.get("title") or title_elem.text.strip()
                        link = title_elem.get("href")
                        if not link.startswith("http"):
                            link = "https://www.spiegel.de" + link

                        # 본문 요약
                        summary_elem = item.select_one("section")
                        summary = summary_elem.text.strip() if summary_elem else ""

                        # 날짜 추출
                        footer_text = item.select_one("footer").text.strip() if item.select_one("footer") else ""
                        date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', footer_text)
                        std_date = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}" if date_match else "N/A"

                        # 발견된 키워드 태깅 (분석용)
                        found_kw = "German" if "anthropozän" in (title + summary).lower() else "English"
                        if "anthropocene" in (title + summary).lower() and found_kw == "German":
                            found_kw = "Both"

                        all_articles.append({
                            "Date Published": std_date,
                            "Headline": title,
                            "Content": summary,
                            "Link": link,
                            "Source": "Der Spiegel (Germany)",
                            "Keyword_Lang": found_kw,
                            "Language": "German/Mixed"
                        })
                    except Exception:
                        continue
                
                print(f"   ㄴ 현재까지 {len(all_articles)}건 누적됨.")
                time.sleep(2.5) # 다중 키워드 검색 시 서버 부하를 고려해 약간 더 대기

            except requests.exceptions.Timeout:
                print(f"⏰ {page}페이지 시간 초과. 다음 단계로.")
                break

    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단되었습니다.")

    finally:
        if all_articles:
            df = pd.DataFrame(all_articles).drop_duplicates(subset=['Headline'])
            # 날짜순 정렬
            df = df.sort_values(by="Date Published", ascending=False)
            filename = "./dataset/spiegel_anthropocene_multilang.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n✅ 통합 수집 완료: 총 {len(df)}건 저장 ({filename})")
        else:
            print("\n🔍 검색 결과가 없습니다.")

if __name__ == "__main__":
    crawl_spiegel_integrated(max_pages=15)
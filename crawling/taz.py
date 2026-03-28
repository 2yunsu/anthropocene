import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def crawl_taz_anthropocene(keyword="Anthropozän"):
    # taz 검색 URL (독일어 키워드 사용 권장)
    search_url = f"https://taz.de/!s={keyword}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    articles = []
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ 접속 실패: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # taz의 검색 결과 기사 단위 추출 (보통 article 또는 div.sect_article)
        items = soup.select("div.sect_article, article")
        print(f"🚀 taz에서 {len(items)}건의 후보 기사를 발견했습니다.")

        for item in items:
            try:
                # 제목 추출
                title_elem = item.select_one("h4, h3, .news")
                if not title_elem: continue
                title = title_elem.text.strip()
                
                # 링크 추출
                link = "https://taz.de" + item.find("a")["href"] if item.find("a") else ""
                
                # 요약 추출
                summary_elem = item.select_one("p.subtitle, p.teaser")
                summary = summary_elem.text.strip() if summary_elem else "Keine Beschreibung"
                
                # 날짜 추출
                date_elem = item.select_one("span.date, time")
                date_text = date_elem.text.strip() if date_elem else "N/A"

                articles.append({
                    "Date Published": date_text,
                    "Headline": title,
                    "Content": summary,
                    "Link": link,
                    "Source": "taz (Germany)",
                    "Language": "German"
                })
            except Exception:
                continue

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

    # 데이터 저장
    if articles:
        df = pd.DataFrame(articles)
        df.to_csv("./dataset/taz_anthropocene_results.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 수집 완료: {len(df)}건의 독일어 기사를 저장했습니다.")
        return df
    else:
        print("🔍 검색 결과가 없습니다.")
        return None

# 실행
crawl_taz_anthropocene()
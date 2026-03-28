import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def crawl_faz_anthropocene(max_pages=5):
    options = webdriver.ChromeOptions()
    # 서버 환경용 필수 설정
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_articles = []
    
    # 독일어(Anthropozän)와 영어(Anthropocene)를 대소문자 구분 없이 검색
    search_query = "Anthropozän OR Anthropocene"
    
    try:
        for page in range(1, max_pages + 1):
            # FAZ 검색 URL 패턴 (GE_S=페이지 시작점, 보통 10개 단위)
            start_index = (page - 1) * 10
            url = f"https://www.faz.net/suche/?query={search_query}&resultsPerPage=10&pageNumber={page}"
            
            print(f"🚀 FAZ {page}페이지 접속 중... (Query: {search_query})")
            driver.get(url)
            
            # 1. 기사 목록 로딩 대기
            try:
                wait = WebDriverWait(driver, 15)
                # FAZ 검색 결과 기사 블록(article 태그) 대기
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.search-result")))
            except:
                print("🏁 검색 결과가 더 이상 없거나 로딩에 실패했습니다.")
                break

            # 2. 기사 정보 추출
            items = driver.find_elements(By.CSS_SELECTOR, "article.search-result")

            for item in items:
                try:
                    # 제목 및 링크 추출
                    title_elem = item.find_element(By.CSS_SELECTOR, "h2.search-result__title a")
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    
                    # 요약(Teaser)
                    try:
                        summary = item.find_element(By.CSS_SELECTOR, "div.search-result__teaser").text.strip()
                    except:
                        summary = ""
                    
                    # 날짜 및 섹션 정보 추출
                    try:
                        date_text = item.find_element(By.CSS_SELECTOR, "time.search-result__date").get_attribute("datetime")
                        if not date_text:
                            date_text = item.find_element(By.CSS_SELECTOR, "time.search-result__date").text.strip()
                    except:
                        date_text = "N/A"

                    all_articles.append({
                        "Date Published": date_text[:10] if date_text != "N/A" else "N/A",
                        "Headline": title,
                        "Content": summary,
                        "Link": link,
                        "Source": "FAZ (Germany)",
                        "Language": "German/English Mixed"
                    })
                except Exception:
                    continue
            
            print(f"   ㄴ 현재까지 {len(all_articles)}건 누적됨.")
            time.sleep(3) # 서버 부하 방지

    except Exception as e:
        print(f"❌ FAZ 크롤링 중 오류 발생: {e}")
    finally:
        driver.quit()

    # 3. 데이터 저장
    if all_articles:
        df = pd.DataFrame(all_articles).drop_duplicates(subset=['Headline'])
        filename = "faz_anthropocene_results.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✅ 완료: 총 {len(df)}건 저장됨 ({filename})")
        return df
    return None

if __name__ == "__main__":
    # 연구 데이터 확보를 위해 10페이지 정도 수집 권장
    crawl_faz_anthropocene(max_pages=10)
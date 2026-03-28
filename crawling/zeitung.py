import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def crawl_sz_anthropocene(max_pages=5):
    options = webdriver.ChromeOptions()
    # 서버 환경을 위한 필수 설정
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_articles = []
    
    # 1. 다중 키워드 검색 (SZ 검색 엔진은 기본적으로 대소문자 무구분)
    # 독일어와 영어를 OR로 조합하여 검색 범위를 넓힙니다.
    search_query = "Anthropozän OR Anthropocene"
    
    try:
        for page in range(1, max_pages + 1):
            # SZ 검색 URL 패턴 (p=페이지 번호)
            url = f"https://www.sueddeutsche.de/search?q={search_query}&page={page}"
            print(f"🚀 SZ {page}페이지 접속 중... (Query: {search_query})")
            driver.get(url)
            
            # 2. 기사 목록 로딩 대기
            try:
                wait = WebDriverWait(driver, 15)
                # 기사 아이템들을 포함하는 컨테이너가 나타날 때까지 대기
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='search-result-title']")))
            except:
                print("🏁 더 이상 결과가 없거나 로딩에 실패했습니다.")
                break

            # 3. 기사 정보 추출
            # SZ의 검색 결과 구조에 맞춘 선택자 사용
            items = driver.find_elements(By.CSS_SELECTOR, "div.css-1m8y0w") # 각 기사 블록

            for item in items:
                try:
                    # 제목 및 링크
                    title_elem = item.find_element(By.CSS_SELECTOR, "a[data-testid='search-result-title']")
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute("href")
                    
                    # 요약(Teaser)
                    try:
                        summary = item.find_element(By.CSS_SELECTOR, "p.css-15uymv9").text.strip()
                    except:
                        summary = ""
                    
                    # 날짜 추출
                    try:
                        date_text = item.find_element(By.CSS_SELECTOR, "time").text.strip()
                    except:
                        date_text = "N/A"

                    all_articles.append({
                        "Date Published": date_text,
                        "Headline": title,
                        "Content": summary,
                        "Link": link,
                        "Source": "Süddeutsche Zeitung (Germany)",
                        "Language": "German/English Mixed"
                    })
                except Exception:
                    continue
            
            print(f"   ㄴ 현재까지 {len(all_articles)}건 누적됨.")
            time.sleep(3) # 서버 부하 방지 및 렌더링 대기

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        driver.quit()

    # 4. 데이터 저장
    if all_articles:
        df = pd.DataFrame(all_articles).drop_duplicates(subset=['Headline'])
        filename = "./dataset/sz_anthropocene_results.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✅ 완료: 총 {len(df)}건 저장됨 ({filename})")
        return df
    return None

if __name__ == "__main__":
    crawl_sz_anthropocene(max_pages=10)
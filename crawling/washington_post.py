import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def crawl_wapo_stable(keyword="Anthropocene"):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled') # 자동화 감지 회피
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # 자동화 감지 우회를 위한 스크립트 실행
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    articles = []
    try:
        url = f"https://www.washingtonpost.com/search/?query={keyword}&sort=relevance"
        print(f"🚀 접속 시도: {url}")
        driver.get(url)
        
        # 1. 페이지 로딩 대기 (최대 20초)
        wait = WebDriverWait(driver, 20)
        # WaPo 검색 결과는 보통 'article' 태그나 특정 클래스 내부에 나타납니다.
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))
        except:
            print("⚠️ 검색 결과 요소를 찾지 못했습니다. 페이지 소스를 확인합니다.")
            # 페이지 로딩 실패 시 현재 화면 텍스트 확인 (디버깅용)
            if "No results" in driver.page_source:
                print("🔍 검색 결과가 실제로 없습니다.")
                return None

        # 2. 강제 스크롤 및 렌더링 대기
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)

        # 3. 데이터 추출 (태그 기반으로 범용성 확보)
        # WaPo는 검색 결과 기사를 article 태그로 묶습니다.
        items = driver.find_elements(By.TAG_NAME, "article")
        print(f"📦 발견된 기사 후보: {len(items)}건")

        for item in items:
            try:
                # 제목 추출 (h2 또는 특정 클래스)
                title_elem = item.find_elements(By.CSS_SELECTOR, "h2, .font--headline, [data-testid='headline']")
                title = title_elem[0].text if title_elem else "N/A"
                
                # 링크 추출
                link_elem = item.find_elements(By.TAG_NAME, "a")
                link = link_elem[0].get_attribute("href") if link_elem else "N/A"
                
                # 요약 추출
                summary_elem = item.find_elements(By.CSS_SELECTOR, "p, .font--body, [data-testid='description']")
                summary = summary_elem[0].text if summary_elem else "No description"
                
                if title != "N/A":
                    articles.append({
                        "Date Published": "N/A", # 날짜는 추후 정밀 추출 필요
                        "Headline": title,
                        "Content": summary,
                        "Link": link,
                        "Source": "The Washington Post"
                    })
            except:
                continue

    finally:
        driver.quit()

    if articles:
        df = pd.DataFrame(articles).drop_duplicates(subset=['Headline'])
        df.to_csv("./dataset/wapo_anthropocene_results.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 성공: {len(df)}건 저장 완료.")
        return df
    return None

if __name__ == "__main__":
    crawl_wapo_stable()
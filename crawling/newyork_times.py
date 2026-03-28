import requests
import pandas as pd
import time

def fetch_nyt_anthropocene_data(api_key, start_year=2000, end_year=2024):
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    all_articles = []
    
    # NYT API는 페이지당 10개씩 결과를 반환합니다 (0~100페이지까지 지원)
    # 기사 제목(headline)이나 본문(body)에 Anthropocene이 들어간 경우만 검색
    query = 'body:("Anthropocene") OR' \
    'headline:("Anthropocene") OR' \
    
    for page in range(0, 20): # 예시로 상위 200개 기사 수집
        params = {
            "q": query,
            "api-key": api_key,
            "page": page,
            "begin_date": f"{start_year}0101",
            "end_date": f"{end_year}1231",
            "sort": "newest"
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                docs = data['response']['docs']
                
                if not docs:
                    print(f"🏁 {page}페이지에서 더 이상 검색 결과가 없습니다.")
                    break
                    
                for doc in docs:
                    all_articles.append({
                        "Date Published": doc.get('pub_date', ''),
                        "Headline": doc['headline'].get('main', ''),
                        "Content": doc.get('abstract', '') + " " + doc.get('lead_paragraph', ''),
                        "Link": doc.get('web_url', ''),
                        "Source": "The New York Times",
                        "Section": doc.get('section_name', '')
                    })
                
                print(f"✅ {page+1}페이지 수집 완료 ({len(all_articles)}건)")
                
                # NYT API의 초당 요청 제한(Rate Limit)을 준수하기 위해 6초 대기
                time.sleep(6) 
                
            elif response.status_code == 429:
                print("⚠️ 요청 제한 초과! 10초 대기 후 재시도합니다.")
                time.sleep(12)
                continue
            else:
                print(f"❌ 에러 발생: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ 네트워크 오류: {e}")
            break

    # 데이터프레임 변환 및 저장
    if all_articles:
        df = pd.DataFrame(all_articles)
        # 이전 통합 분석 코드의 컬럼명 규격과 맞춤
        df['Date Published'] = pd.to_datetime(df['Date Published']).dt.strftime('%Y-%m-%d')
        df.to_csv("./dataset/nyt_anthropocene_api_results.csv", index=False, encoding='utf-8-sig')
        print(f"\n🎉 총 {len(df)}건의 'Anthropocene' 기사를 저장했습니다.")
        return df
    else:
        print("🔍 검색 결과가 없습니다.")
        return None

API_KEY = "" #Insert your API Key
fetch_nyt_anthropocene_data(API_KEY)
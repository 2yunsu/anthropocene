import requests
import pandas as pd
import time

def fetch_guardian_anthropocene(api_key, start_date="2000-01-01"):
    url = "https://content.guardianapis.com/search"
    all_articles = []
    
    # 1. 파라미터 설정
    # q: 검색어 (대소문자 구분 없음)
    # section: 환경 및 기후 위기 섹션으로 한정 가능 (필요 시)
    # show-fields: 본문 요약(trailText) 및 본문(bodyText) 포함
    params = {
        "q": "Anthropocene",
        "api-key": api_key,
        "from-date": start_date,
        "show-fields": "headline,trailText,bodyText,webPublicationDate",
        "page-size": 50, # 한 페이지당 최대 50개
        "page": 1
    }

    try:
        while True:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"❌ 에러 발생: {response.status_code}")
                break
                
            data = response.json()['response']
            results = data.get('results', [])
            
            if not results:
                print("🏁 모든 데이터를 수집했습니다.")
                break
            
            for art in results:
                fields = art.get('fields', {})
                all_articles.append({
                    "Date Published": art.get('webPublicationDate', '')[:10], # YYYY-MM-DD
                    "Headline": fields.get('headline', ''),
                    "Content": fields.get('trailText', '') + " " + fields.get('bodyText', '')[:500], # 분석용 본문 일부
                    "Link": art.get('webUrl', ''),
                    "Source": "The Guardian",
                    "Section": art.get('sectionName', '')
                })
            
            print(f"✅ {params['page']}페이지 수집 완료 (누적 {len(all_articles)}건)")
            
            # 다음 페이지 확인
            if params['page'] >= data.get('pages', 0):
                break
            
            params['page'] += 1
            time.sleep(1) # Guardian API는 비교적 관대하지만 매너 타임 준수

    except Exception as e:
        print(f"❌ 오류: {e}")

    # 2. 데이터 저장
    if all_articles:
        df = pd.DataFrame(all_articles)
        # 중복 제거 및 정렬
        df = df.drop_duplicates(subset=['Headline']).sort_values('Date Published', ascending=False)
        df.to_csv("./dataset/guardian_anthropocene_results.csv", index=False, encoding='utf-8-sig')
        print(f"🎉 총 {len(df)}건의 가디언 기사를 저장했습니다.")
        return df
    return None

API_KEY = "" #Insert your API Key
fetch_guardian_anthropocene(API_KEY)
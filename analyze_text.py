import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_and_filter_comprehensive():
    all_data = []
    keyword_stats = [] # 유사어별 통계를 저장할 리스트
    
    # 1. 분석할 확장 키워드 정의 (정규표현식 패턴)
    keywords = {
        'Anthropocene': r'Anthropocene|Anthropozän',
        'Great Acceleration': r'Great Acceleration',
        'Sixth Extinction': r'Sixth Extinction|Mass Extinction',
        'Capitalocene': r'Capitalocene|Chthulucene',
        'Climate Crisis': r'Climate Crisis|Climate Emergency'
    }

    file_configs = [
        {'file': './dataset/News_Category_Dataset_v3.json', 'type': 'json', 't_col': 'headline', 'd_col': 'date', 'name': 'HuffPost'},
        {'file': './dataset/guardian_environment_news.csv', 'type': 'csv', 't_col': 'Title', 'd_col': 'Date Published', 'name': 'The Guardian'},
        {'file': './dataset/climate_headlines_sentiment.csv', 'type': 'csv', 't_col': 'Headline', 'd_col': 'Date Published', 'name': 'Climate Sentiment'},
        {'file': './dataset/twitter_sentiment_data.csv', 'type': 'csv', 't_col': 'message', 'd_col': 'date', 'name': 'Twitter'},
        {'file': './dataset/guardian_anthropocene_results.csv','type': 'csv', 't_col': 'Headline', 'd_col': 'Date', 'name': 'The Guardian anthropocene'},
        {'file': './dataset/nyt_anthropocene_api_results.csv','type': 'csv', 't_col': 'Headline', 'd_col': 'Date', 'name': 'The New York Times anthropocene'},
        {'file': './dataset/taz.csv','type': 'csv', 't_col': 'Headline', 'd_col': 'Date', 'name': 'Taz'},
    ]

    for config in file_configs:
        fname = config['file']
        if not os.path.exists(fname): continue
            
        try:
            # 데이터 로드
            df = pd.read_json(fname, lines=True) if config['type'] == 'json' else pd.read_csv(fname)
            total_rows = len(df)
            actual_t_col = config['t_col'] if config['t_col'] in df.columns else config['t_col'].lower()
            actual_d_col = config['d_col'] if config['d_col'] in df.columns else config['d_col'].lower()

            # 2. 각 유사어별 개별 통계 계산
            for label, pattern in keywords.items():
                mask = df[actual_t_col].str.contains(pattern, case=False, na=False)
                match_count = len(df[mask])
                
                # 통계 리스트에 추가
                keyword_stats.append({
                    'Source': config['name'],
                    'Keyword_Type': label,
                    'Total_Articles': total_rows,
                    'Mentions': match_count,
                    'Percentage': (match_count / total_rows * 100) if total_rows > 0 else 0
                })

                # 3. 시계열 분석용 통합 데이터 수집 (필터링된 데이터가 있을 경우)
                if match_count > 0:
                    matched_df = df[mask].copy()
                    matched_df.rename(columns={actual_t_col: 'title'}, inplace=True)
                    if actual_d_col in df.columns:
                        matched_df.rename(columns={actual_d_col: 'date'}, inplace=True)
                    else:
                        matched_df['date'] = pd.NaT
                    
                    matched_df['source'] = config['name']
                    matched_df['keyword_type'] = label
                    all_data.append(matched_df[['date', 'title', 'source', 'keyword_type']])

        except Exception as e:
            print(f"⚠️ {fname} 처리 중 에러: {e}")

    # --- 통계 출력부 ---
    stats_df = pd.DataFrame(keyword_stats)
    print("\n" + "="*70)
    print("📊 데이터셋 및 유사어별 담론 비중 분석 (Detailed Summary)")
    print("="*70)
    # 가독성을 위해 출처와 키워드 유형순으로 정렬하여 출력
    print(stats_df.sort_values(['Source', 'Mentions'], ascending=[True, False]).to_string(index=False))
    print("="*70 + "\n")

    # 데이터 저장
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_csv('anthropocene_expanded_results.csv', index=False, encoding='utf-8-sig')
        stats_df.to_csv('anthropocene_keyword_stats.csv', index=False, encoding='utf-8-sig')
        return final_df
    return None

# def visualize_keywords(df):
#     if df is None or df.empty: return
    
#     # 키워드별 분포 시각화
#     plt.figure(figsize=(12, 6))
#     sns.barplot(data=df['keyword_type'].value_counts().reset_index(), x='count', y='keyword_type', palette='magma')
#     plt.title('Total Mentions by Keyword Category', fontsize=15)
#     plt.xlabel('Number of Hits')
#     plt.savefig("combined_result.png")

# 실행
integrated_df = load_and_filter_comprehensive()
visualize_keywords(integrated_df)
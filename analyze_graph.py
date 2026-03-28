import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
file_list = [f for f in os.listdir(DATASET_DIR) if f.endswith('.csv') or f.endswith('.json')]

# 파일명-언론사 매핑 (필요시 직접 수정)
MEDIA_MAP = {
    'guardian': 'The Guardian',
    'nyt': 'NYT',
    'taz': 'TAZ',
    'twitter': 'Twitter',
    'news': 'Huff',
}

media_year_count = defaultdict(lambda: defaultdict(int))
anthro_pattern = re.compile(r'anthropocene', re.IGNORECASE)

for file_name in file_list:
    file_path = os.path.join(DATASET_DIR, file_name)
    media_key = file_name.split('_')[0].lower()
    media = MEDIA_MAP.get(media_key, media_key.capitalize())
    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith('.json'):
            df = pd.read_json(file_path, lines=True)
        else:
            continue
    except Exception as e:
        print(f"[경고] {file_name} 읽기 실패: {e}")
        continue

    text_cols = [c for c in df.columns if any(x in c.lower() for x in ['content', 'headline', 'title', 'message'])]
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    if not text_cols or not date_cols:
        continue
    text_col = text_cols[0]
    date_col = date_cols[0]

    for _, row in df.iterrows():
        text = str(row[text_col])
        if not anthro_pattern.search(text):
            continue
        date_val = str(row[date_col])
        year = None
        # YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
        m = re.match(r'(\\d{4})[-/.]', date_val)
        if m:
            year = m.group(1)
        # DD.MM.YYYY or DD/MM/YYYY
        m = re.match(r'(\\d{1,2})[./-](\\d{1,2})[./-](\\d{4})', date_val)
        if m:
            year = m.group(3)
        # YYYY
        m = re.match(r'(\\d{4})$', date_val)
        if m:
            year = m.group(1)
        # 기타: 날짜 파싱 시도
        if not year:
            try:
                dt = pd.to_datetime(date_val, errors='coerce')
                if pd.notnull(dt):
                    year = str(dt.year)
            except:
                pass
        if year and year.isdigit():
            media_year_count[media][int(year)] += 1

# 그래프 그리기
plt.figure(figsize=(12, 7))
for media, year_count in media_year_count.items():
    years = sorted(year_count.keys())
    counts = [year_count[y] for y in years]
    plt.plot(years, counts, marker='o', label=media)

plt.title('Yearly Frequency of "Anthropocene" Mentions by Media')
plt.xlabel('Year')
plt.ylabel('Mention Count')
plt.legend()
plt.tight_layout()
plt.savefig("result.png")
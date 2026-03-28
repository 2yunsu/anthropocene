# 🌍 Global Anthropocene Media Discourse Analysis

This repository contains a comprehensive data collection and analysis pipeline for tracking the **"Anthropocene"** discourse across major global news outlets.

## 📂 Project Structure

```text
.
├── crawling/                # Multi-national news scraping scripts
│   ├── newyork_times.py     # NYT API-based collector
│   ├── washington_post.py   # Selenium-based scraper for WaPo
│   ├── the_guardian.py      # Guardian Open Platform API collector
│   ├── faz.py               # FAZ (Frankfurter Allgemeine Zeitung) scraper
│   ├── spiegel.py           # Der Spiegel (Magazine) scraper
│   ├── taz.py               # Die Tageszeitung (taz) historical scraper
│   └── zeitung.py           # SZ (Süddeutsche Zeitung) scraper
├── dataset/                 # Collected data (CSVs) - *Git-ignored if >100MB*
├── analyze_text.py          # NLP & Semantic similarity (Word2Vec) logic
├── analyze_graph.py         # Visualization and trend plotting
└── requirements.txt         # Python dependencies
```
## 🛠 Tech Stack & Installation
Prerequisites
```
Python 3.10+
```
Google Chrome & ChromeDriver (Required for Selenium-based scrapers)

Installation
Clone the repository:
```
git clone [https://github.com/2yunsu/anthropocene.git](https://github.com/2yunsu/anthropocene.git)
cd anthropocene
```
Install dependencies:
```
pip install -r requirements.txt
```

## Usage
To collect data from a specific outlet, execute the corresponding script(Some scripts needs your own API keys):
```
python crawling/newyork_times.py
```
📈 Analysis Pipeline (Planned)
```
python analyze_graph.py
python analyze_text.py
```
## References
[News Category Dataset]: https://www.kaggle.com/datasets/rmisra/news-category-dataset?resource=download
[Environment News Dataset]: https://www.kaggle.com/datasets/beridzeg45/guardian-environment-related-news
[Twitter Climate Change Sentiment Dataset]: https://www.kaggle.com/datasets/edqian/twitter-climate-change-sentiment-dataset
[Climate Change News]: https://www.kaggle.com/datasets/fringewidth/climate-change-news

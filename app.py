import os
import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Shivohm.AI - Financial News Analyzer", layout="wide")
st.title("Shivohm.AI — Financial News Analyzer (Open Source Mode)")

NEWSAPI_KEY = st.sidebar.text_input("NewsAPI Key (optional)", value=os.getenv("NEWSAPI_KEY") or "")
max_articles = st.sidebar.slider("Max articles to fetch", 1, 10, 6)
use_demo = st.sidebar.checkbox("Use demo data (if no NewsAPI key)", value=not bool(NEWSAPI_KEY))

SAMPLE_ARTICLES = [
    {"title":"RBI keeps repo rate unchanged, signals careful stance","source":"Economic Times","publishedAt":"2025-10-05T10:00:00Z","url":"https://example.com/rbi-repo","content":"RBI maintained repo rate..."},
    {"title":"Infosys reports 8% YoY revenue growth but lowers FY guidance","source":"Business Standard","publishedAt":"2025-10-04T09:00:00Z","url":"https://example.com/infosys-q2","content":"Infosys announced its quarterly results..."},
    {"title":"Oil prices surge after OPEC announces cuts","source":"Reuters","publishedAt":"2025-10-03T08:00:00Z","url":"https://example.com/oil-opec","content":"Crude oil futures jumped..."}
]

def fetch_news_newsapi(key, query='finance', page_size=5):
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "pageSize": page_size, "sortBy":"publishedAt", "language":"en", "apiKey":key}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "ok":
            out = []
            for a in data.get("articles", []):
                out.append({
                    "title": a.get("title"),
                    "source": a.get("source", {}).get("name"),
                    "publishedAt": a.get("publishedAt"),
                    "url": a.get("url"),
                    "content": a.get("content") or a.get("description") or ""
                })
            return out
        else:
            return []
    except:
        return []

def simple_summary(text):
    sents = [s.strip() for s in text.split('.') if s.strip()]
    return '. '.join(sents[:2]) + ('.' if len(sents)>=1 else '')

def decide_action(sentiment, confidence):
    if sentiment == "Positive" and confidence >= 0.7:
        return "Buy"
    if sentiment == "Positive":
        return "Hold"
    if sentiment == "Neutral":
        return "Hold"
    if sentiment == "Negative" and confidence >= 0.7:
        return "Sell"
    return "Hold"

def analyze_article(a):
    content = (a.get('content') or a.get('title') or '')[:2000]
    summary = simple_summary(content)
    sentiment = "Neutral"
    confidence = 0.6
    if any(w in content.lower() for w in ['rise','surge','beat','gain','profit','positive']):
        sentiment = "Positive"; confidence = 0.8
    if any(w in content.lower() for w in ['cut','lower','decline','drop','loss','weak','negative']):
        sentiment = "Negative"; confidence = 0.8
    impact = ''
    if 'bank' in content.lower() or 'rbi' in content.lower():
        impact = 'Banking & Financials'
    if 'oil' in content.lower() or 'opec' in content.lower():
        impact = 'Energy'
    action = decide_action(sentiment, confidence)
    return {'summary': summary, 'sentiment': sentiment, 'confidence': confidence, 'impact': impact, 'action': action}

col1, col2 = st.columns([3,1])
with col1:
    st.header("Articles & Insights")
    if st.button("Fetch & Analyze"):
        if not NEWSAPI_KEY and use_demo:
            articles = SAMPLE_ARTICLES[:max_articles]
        else:
            articles = fetch_news_newsapi(NEWSAPI_KEY, query='markets OR stock OR economy OR finance OR rates', page_size=max_articles)
            if not articles:
                st.warning("No articles found; using demo data.")
                articles = SAMPLE_ARTICLES[:max_articles]
        results = [ {**a, **analyze_article(a)} for a in articles ]
        st.session_state['results'] = results
        for r in results:
            st.markdown('---')
            st.subheader(r['title'])
            st.write(f"**Source:** {r['source']}  •  **Published:** {r['publishedAt']}")
            st.write(f"**Summary:** {r['summary']}")
            st.write(f"**Sentiment:** {r['sentiment']}  •  **Confidence:** {r['confidence']}")
            st.write(f"**Impact:** {r['impact']}")
            st.write(f"**Action:** {r['action']}")
            st.write(f"[Read original]({r['url']})")

with col2:
    st.header('Sentiment Dashboard')
    rs = st.session_state.get('results', SAMPLE_ARTICLES[:3])
    pos = sum(1 for x in rs if x.get('sentiment')=='Positive')
    neu = sum(1 for x in rs if x.get('sentiment')=='Neutral')
    neg = sum(1 for x in rs if x.get('sentiment')=='Negative')
    df = pd.DataFrame({'Sentiment':['Positive','Neutral','Negative'], 'Count':[pos,neu,neg]})
    st.table(df)
    st.bar_chart(df.set_index('Sentiment'))

st.markdown('---')
st.info('This is a starter scaffold that uses simple heuristics for sentiment/action. Replace with HF model or API for production.')

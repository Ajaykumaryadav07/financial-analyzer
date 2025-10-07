Shivohm.AI - Financial News Analyzer (Open-Source Mode)

Files:
- app.py
- requirements.txt
- README.md

Quick Replit steps:
1. Create a new Repl -> Python
2. Upload the three files
3. Add Secrets (🔒 icon):
   - NEWSAPI_KEY (optional)
4. Run:
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0

Notes:
- This scaffold uses simple heuristics for sentiment and Buy/Hold/Sell decisions.
- To use HF models, set up HF API and modify app.py to call that endpoint.

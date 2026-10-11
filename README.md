# financial-risk-engine

## How to run

Start the FastAPI backend in one terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Then start the dashboard in another terminal:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

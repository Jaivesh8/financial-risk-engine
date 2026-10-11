# Financial Risk Engine - S&P Global & Crisil Campus Hackathon

Candidate Name: Jaivesh Chopra

College Email ID: jchopra_be24@thapar.edu

College / Campus: Thapar Institute of Engineering and Technology

Demo Video Link: [to be added]

## 1. Project Overview / Problem Statement & Approach (2-3 paragraphs)

Financial news can introduce rapid portfolio risk through geopolitical developments, macroeconomic conditions, credit events, corporate actions, and regulatory announcements. This project provides a small, demonstrable risk-engine workflow that turns a news headline into a sentiment score, an event category, an impact score, and, when appropriate, a transparent portfolio stress scenario.

The application ingests either deterministic sample headlines or articles from optional GDELT and NewsAPI connectors. It analyzes text with FinBERT sentiment scoring and BART zero-shot event classification, then applies the existing impact heuristic. The FastAPI service exposes analysis, ingestion, and stress-test endpoints; the Streamlit dashboard presents the feed, stress-test asset breakdown, and stored stress-test history.

## 2. Architecture & Tech Stack

```text
Sources: sample headlines | GDELT | NewsAPI
                    |
                    v
NLP engine: FinBERT sentiment | BART zero-shot event classification | impact heuristic
                    |
                    v
FastAPI + SQLite
                    |
                    v
Stress test module
                    |
                    v
Streamlit dashboard
```

Tech stack: Python 3.12, FastAPI, Pydantic, Transformers, PyTorch, SQLite, Streamlit, Plotly, pandas, and requests.

## 3. Dataset Used

The repository includes a deterministic sample-headline corpus for the demo, covering geopolitical, macroeconomic, credit, merger/acquisition, earnings, regulatory, and product-launch scenarios. The ingestion layer also includes connectors for GDELT and NewsAPI; both safely return no articles when unavailable or not configured.

The portfolio and its stress shocks are synthetic, illustrative assumptions rather than holdings, market data, or calibrated risk factors. The fixed portfolio asset classes and the scenario shock percentages are intended to make the stress-test mechanics transparent, not to represent investment advice or real-world valuation.

## 4. Quickstart & Installation

Prerequisite: Python 3.12 on Windows.

```powershell
git clone https://github.com/Jaivesh8/financial-risk-engine.git
cd financial-risk-engine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal, from the project directory with the virtual environment activated:

```powershell
streamlit run dashboard/app.py
```

Run the tests with:

```powershell
python -m pytest tests -q
```

## 5. Key Results & Domain Impact

The code accepts a headline, classifies it into a fixed financial-event taxonomy, produces a sentiment score, and calculates an impact score using the configured event severity and small corroboration, sector, and sentiment adjustments. It can run defined stress scenarios on the illustrative portfolio and returns both total portfolio changes and a per-asset-class breakdown.

For a demo workflow, the application can load sample news, display the resulting analyses, run a forced stress test when needed, and retain stress-test records in SQLite for the history endpoint. The implementation does not claim predictive accuracy, live portfolio valuation, calibrated risk metrics, or investment outcomes.

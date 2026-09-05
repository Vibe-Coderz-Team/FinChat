import os, json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FinChat API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_BASE = os.getenv("API_BASE", "https://openrouter.ai/api/v1")
API_KEY = os.getenv("API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "liquid/lfm-2.5-2.6b:free")

class TraceEngine:
    def __init__(self):
        self.gateway = pd.read_csv("gateway.csv").fillna("")
        self.bank = pd.read_csv("bank.csv").fillna("")
        self.ledger = pd.read_csv("ledger.csv").fillna("")
        
        master = self.gateway.copy()
        master = master.merge(self.bank, on="transaction_id", how="left", suffixes=("", "_bank"))
        master = master.merge(self.ledger, on="transaction_id", how="left", suffixes=("", "_ledger"))
        master = master.fillna("")
        
        def get_status(row):
            if row["status"] == "captured" and row.get("bank_name", "") == "":
                return "exception"
            if row.get("status_bank") == "pending":
                return "pending"
            if row.get("status_bank") == "settled":
                return "settled"
            return row["status"]
            
        master["master_status"] = master.apply(get_status, axis=1)
        self.master = master

    def search(self, filters: dict):
        df = self.master.copy()
        if filters.get("merchant_name"):
            df = df[df["merchant_name"].str.contains(filters["merchant_name"], case=False, na=False)]
        if filters.get("bank_name"):
            df = df[df["bank_name"].str.contains(filters["bank_name"], case=False, na=False)]
        if filters.get("status"):
            df = df[df["master_status"] == filters["status"].lower()]
        if filters.get("transaction_id"):
            df = df[df["transaction_id"] == filters["transaction_id"]]
        if filters.get("amount_approx"):
            amt = float(filters["amount_approx"])
            df = df[(df["amount"] >= amt - 10) & (df["amount"] <= amt + 10)]
        if filters.get("payment_method"):
            df = df[df["payment_method"] == filters["payment_method"].lower()]
        return df

    def trace(self, txn_id: str) -> dict:
        gw = self.gateway[self.gateway["transaction_id"] == txn_id].to_dict('records')
        bk = self.bank[self.bank["transaction_id"] == txn_id].to_dict('records')
        ld = self.ledger[self.ledger["transaction_id"] == txn_id].to_dict('records')
        
        gw_data = gw[0] if gw else None
        bk_data = bk[0] if bk and bk[0].get('bank_name') else None
        
        discrepancies = []
        if gw_data and gw_data['status'] == 'captured':
            if not bk_data:
                discrepancies.append("MISSING_BANK_RECORD: Payment captured by gateway but no bank settlement found.")
        
        return {
            "transaction_id": txn_id,
            "gateway": gw_data,
            "bank": bk_data,
            "ledger": ld,
            "discrepancies": discrepancies,
            "status_summary": "exception" if discrepancies else "settled" if bk_data and bk_data.get('status') == 'settled' else "pending"
        }

engine = TraceEngine()

def extract_intent(user_query: str, custom_api_key: str = None) -> dict:
    try:
        key_to_use = custom_api_key if custom_api_key else API_KEY
        if not key_to_use:
            raise Exception("No API Key provided. Please enter one in the UI settings.")
            
        client = OpenAI(base_url=API_BASE, api_key=key_to_use)
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Extract JSON filters from query: merchant_name, bank_name, status (settled/pending/failed/exception), amount_approx, payment_method (card/wallet/upi), transaction_id. Return ONLY valid JSON."},
                {"role": "user", "content": user_query}
            ],
            temperature=0.0
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```json"): raw = raw[7:]
        if raw.endswith("```"): raw = raw[:-3]
        return json.loads(raw)
    except Exception as e:
        # If the LLM fails, we raise an explicit error so the user knows it's an API limit
        raise Exception(f"LLM_ERROR: {str(e)}")

def generate_html_cards(traces: list, error_msg: str = None) -> str:
    if error_msg:
        return f"<span style='color:#ff0000; font-weight:bold;'>[LLM ERROR]</span> <span style='color:#ffffff;'>{error_msg}</span>"
        
    if not traces:
        return "<span style='color:#ff0000; font-weight:bold;'>[NOT FOUND]</span> <span style='color:#ffffff;'>No matching transactions found in the database. Please try another search.</span>"
    
    parts = ["<h2 style='color:#ffffff; margin-bottom:20px; font-size:1.2rem; display:flex; align-items:center; gap:8px;'>⚡ Live Trace Complete</h2>"]
    
    for t in traces:
        tid = t.get('transaction_id', 'Unknown')
        status = t.get('status_summary', '').upper()
        
        color = "#00ff00" if status == "SETTLED" else "#ff0000" if status == "EXCEPTION" else "#ffff00"
        
        parts.append(f"<div style='background-color:#111111; padding:16px; border-radius:12px; margin-bottom:16px; border:1px solid #222; border-left:4px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>")
        
        parts.append(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #333; padding-bottom:8px;'>")
        parts.append(f"<strong style='color:#ffffff; font-size:1.1rem; font-family:monospace;'>{tid}</strong>")
        parts.append(f"<span style='color:{color}; font-weight:800; letter-spacing:1px; font-size:0.85rem;'>[{status}]</span>")
        parts.append("</div>")
        
        gw = t.get('gateway')
        if gw:
            parts.append(f"<div style='color:#cccccc; margin-bottom:6px;'><strong style='color:#ffffff; min-width:80px; display:inline-block;'>Gateway:</strong> Captured on <span style='color:#a5b4fc;'>{gw.get('captured_at', 'N/A')}</span> for <span style='color:#00ff00;'>Rs. {gw.get('amount', 0)}</span></div>")
        else:
            parts.append("<div style='color:#ff0000; margin-bottom:6px;'><strong style='color:#ffffff; min-width:80px; display:inline-block;'>Gateway:</strong> [EXCEPTION] No record found.</div>")
            
        bk = t.get('bank')
        if bk:
            parts.append(f"<div style='color:#cccccc; margin-bottom:12px;'><strong style='color:#ffffff; min-width:80px; display:inline-block;'>Bank:</strong> Settled on <span style='color:#a5b4fc;'>{bk.get('settled_at', 'N/A')}</span> <span style='color:#64748b; font-size:0.85rem;'>(UTR: {bk.get('utr_number', 'N/A')})</span></div>")
        else:
            parts.append("<div style='color:#ff0000; margin-bottom:12px;'><strong style='color:#ffffff; min-width:80px; display:inline-block;'>Bank:</strong> [EXCEPTION] Missing settlement record.</div>")
            
        discs = t.get('discrepancies', [])
        if discs:
            parts.append(f"<div style='background-color:rgba(255,0,0,0.1); border:1px solid rgba(255,0,0,0.2); padding:10px; border-radius:8px;'>")
            parts.append(f"<div style='color:#ff0000; margin-bottom:4px;'><strong>⚠️ Anomalies Detected:</strong> {', '.join(discs)}</div>")
            parts.append("<div style='color:#ffff00; font-size:0.9rem;'><strong>Next Action:</strong> Please escalate to the banking partner or verify Gateway capture logs.</div>")
            parts.append("</div>")
        else:
            parts.append(f"<div style='background-color:rgba(0,255,0,0.05); border:1px solid rgba(0,255,0,0.1); padding:10px; border-radius:8px;'>")
            parts.append("<div style='color:#00ff00; font-size:0.9rem;'><strong>Status:</strong> Fully reconciled. No further action needed.</div>")
            parts.append("</div>")
        
        parts.append("</div>")
        
    return "".join(parts)

class ChatRequest(BaseModel):
    query: str
    api_key: str = None

@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        filters = extract_intent(request.query, request.api_key)
        # Execute search
        results = engine.search(filters)
        traces = [engine.trace(row["transaction_id"]) for _, row in results.head(5).iterrows()]
        html = generate_html_cards(traces)
        return {"explanation": html, "traces": traces}
    except Exception as e:
        error_str = str(e)
        if "LLM_ERROR" in error_str:
            return {"explanation": generate_html_cards([], error_msg=error_str), "traces": []}
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

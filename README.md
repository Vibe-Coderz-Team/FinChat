<div align="center">
  
  <h1>⚡ FinChat Enterprise</h1>
  <h3>Automated Ledger Reconciliation & Anomaly Detection Intelligence</h3>

  [![Build Status](https://img.shields.io/badge/build-passing-success?style=for-the-badge)](#)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)](#)
  [![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688?style=for-the-badge&logo=fastapi&logoColor=white)](#)
  [![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](#)
  [![License](https://img.shields.io/badge/License-MIT-gray?style=for-the-badge)](#)

  <p align="center">
    <strong>A high-throughput NLP agent designed to seamlessly trace, reconcile, and audit millions of payment gateway transactions against core banking ledgers.</strong>
  </p>

</div>

---

## 📑 Executive Summary

Financial institutions and major payment aggregators lose millions of dollars annually due to orphaned transactions, hidden gateway failures, and delayed bank settlements. Manual reconciliation across fragmented databases (Gateways, Bank Logs, and Internal Ledgers) is computationally expensive and prone to human error.

**FinChat** is an enterprise-grade AI solution that abstracts complex SQL/NoSQL queries into natural language. By ingesting massive datasets into an optimized Pandas vectorization engine, FinChat allows financial operators to instantly trace missing funds, detect anomalies, and audit payment flows in real-time.

---

## ✨ Core Capabilities

- **🔍 Natural Language Querying (NLP to SQL/Pandas):** Support agents can query massive financial databases using plain English (e.g., *"Trace failed card payments over Rs. 10000"*).
- **📊 Tri-Layer Reconciliation:** Automatically merges and validates data across three distinct boundaries:
  - **Payment Gateway Logs** (Capture status, Network)
  - **Core Bank Settlements** (UTR mapping, Settlement timestamps)
  - **Internal Ledgers** (Platform fees, Tax deductions, Net payouts)
- **⚡ Real-Time Anomaly Detection:** Instantly flags `[EXCEPTION]` scenarios where funds were captured by the gateway but missing from the bank settlement.
- **🛡️ Air-Gapped / Local LLM Support:** Built-in `.env` configuration allows institutions to route NLP intent-extraction through local, secure LLMs (like Gemma/Llama via Ollama) to maintain strict data privacy and regulatory compliance.

---

## 🏗️ System Architecture & Specifications

### 1. Presentation Layer (`frontend.html`)
- **Framework:** Vanilla JavaScript + Tailwind CSS.
- **Design:** Dark-mode optimized, chat-based UI with dynamic HTML component rendering.
- **Performance:** Asynchronous data fetching with sub-100ms UI rendering capabilities.

### 2. Application Engine (`backend.py`)
- **Web Framework:** FastAPI running on Uvicorn (ASGI) for asynchronous, high-concurrency request handling.
- **Data Processor:** Pandas DataFrame engine optimized for vectorized searching and merging of multi-million-row datasets.
- **NLP Router:** OpenAI-compatible SDK integration. Uses advanced prompt-engineering to extract structured JSON filters (`merchant_name`, `status`, `amount`, `payment_method`) from unstructured queries.

### 3. Data Layer (`*.csv`)
The system is currently configured to process a simulated high-volume dataset:
- `gateway.csv`: 30,000+ transaction records.
- `bank.csv`: 27,000+ settlement records.
- `ledger.csv`: 27,000+ ledger entries.
- *(Note: Data is loaded in-memory for sub-second retrieval times).*

---

## ⚙️ Deployment & Operations

### Prerequisites
- Python 3.11 or higher
- Git

### Local Environment Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/FinChat-Enterprise.git
   cd FinChat-Enterprise
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment (`.env`):**
   Set your preferred LLM provider. The system supports enterprise cloud APIs (OpenRouter) or on-premise local models (Ollama/LM Studio) for strict data compliance.

4. **Initialize the Core Engine:**
   ```bash
   python backend.py
   ```
   *The FastAPI server will bind to `0.0.0.0:8000`.*

5. **Launch Client UI:**
   Open `frontend.html` in any modern web browser.

---

## 🚀 Production Deployment (Cloud)
To deploy FinChat into a production cloud environment (e.g., Render, AWS, Railway):

1. Connect your GitHub repository to your cloud provider.
2. Define the build command: `pip install -r requirements.txt`
3. Define the start command: `uvicorn backend:app --host 0.0.0.0 --port 10000`
4. Update the client-side `fetch()` URL in `frontend.html` to target your new cloud API endpoint.

---

<div align="center">
  <small>© 2026 FinChat Enterprise Systems. Built for high-scale financial reconciliation.</small>
</div>

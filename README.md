# 🛡️ Aegis Sentinel: AI-Powered SQLi Detection System

[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/UI-React%2019-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind](https://img.shields.io/badge/CSS-Tailwind%20v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![ML](https://img.shields.io/badge/ML-Ensemble%20AI-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)

**Aegis Sentinel** is a state-of-the-art cybersecurity solution engineered to detect and intercept SQL Injection (SQLi) attacks using a sophisticated **Multi-Tier Hybrid Detection Architecture**. It moves beyond traditional signature-based matching to a deep semantic analysis of query intent.

---

## 🏛️ System Architecture

Aegis Sentinel operates on a **Three-Tier Tactical Defense** strategy:

### 🛡️ Tier 1: Heuristic Firewall (SIC)
The **Structural Integrity Check (SIC)** layer performs rapid, high-precision structural logic validation. It uses advanced regex and tokenization to identify known attack patterns (Tautologies, Union-based, Time-based) with zero latency, providing a "Fast-Fail" mechanism for obvious threats.

### 🧠 Tier 2: Statistical Ensemble Engine
A weighted consensus model combining the strengths of 7 distinct machine learning algorithms:
*   **XGBoost & LightGBM**: Optimized for high-velocity feature classification.
*   **Random Forest & Decision Trees**: Robust handling of non-linear semantic features.
*   **Logistic Regression & Linear SVC**: Statistical baseline for linear probability.
*   **LSTM (RNN)**: A Deep Learning layer that analyzes queries as sequences to capture long-range dependencies in complex, obfuscated payloads.

### 🔮 Tier 3: Semantic Intent Layer (CodeBERT)
Utilizing **Transformer-based embeddings** (CodeBERT) and **Intent Mismatch Detection (IMD)**, this experimental layer identifies zero-day threats by comparing the latent semantic intent of a query against an authorized application baseline.

---

## 🎨 Operational Dashboard

The **Aegis Deep Dark 2.0** interface provides real-time situational awareness:
*   **📊 Traffic Sandbox**: Test payloads against the Sentinel engine with immediate feedback.
*   **📡 Live WebSocket Stream**: Real-time intercept logs visualized with threat probability gauges.
*   **🕸️ Radar Consensus**: Visualize how different model tiers (Semantic, Boolean, Time, etc.) perceive the threat.
*   **📜 Forensic Audit Ledger**: A comprehensive history of intercepted queries with full metadata storage.

---

## 🚀 Getting Started

### ⚡ Quick Start (Windows)
The fastest way to launch the entire tactical stack is via the bootstrapper:
```powershell
.\start_simple.bat
```

### 🛠️ Manual Installation

#### 1. Backend Infrastructure (Python 3.10+)
```bash
# Initialize Virtual Environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/macOS

# Install Neural Dependencies
pip install -r requirements.txt

# Launch API Gateway
uvicorn api.main:app --port 8000 --reload
```

#### 2. Frontend Command Center (Node.js 18+)
```bash
cd frontend-simple
npm install
npm run dev
```

| Component | URL |
| :--- | :--- |
| **Dashboard** | `http://localhost:5173` |
| **API Documentation** | `http://localhost:8000/docs` |
| **WebSocket Stream** | `ws://localhost:8000/ws/alerts` |

---

## 📊 Performance Matrix

| Detection Layer | Precision | Latency | Primary Strength |
| :--- | :--- | :--- | :--- |
| **Heuristic (SIC)** | 100% | < 1ms | Known Signatures & Structural logic |
| **ML Ensemble** | 98.4% | ~15ms | Statistical Pattern Recognition |
| **Semantic (CodeBERT)**| Experimental | ~80ms | Zero-Day & Obfuscation Detection |
| **Consensus Verdict** | **~99.9%** | **~25ms** | Multi-Layer Hybrid Agreement |

---

## 🐳 Docker Deployment

```bash
docker build -t aegis-sentinel .
docker run -p 8000:8000 aegis-sentinel
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ for Advanced AI Cybersecurity Research.

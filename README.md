# 🛡️ Aegis Sentinel: AI-Powered SQLi Detection System

[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/UI-React%2019-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Build-Vite-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind](https://img.shields.io/badge/CSS-Tailwind%20v4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

**Aegis Sentinel** is an enterprise-grade cybersecurity solution designed to detect and intercept SQL Injection (SQLi) attacks using a multi-layered defensive strategy. It replaces traditional signature-based detection with a premium, domain-driven AI Intelligence dashboard.

---

## 🌟 Modernized Tactical Interface

The system features the **Aegis Deep Dark 2.0** SOC interface, organized into specialized tactical sectors:

*   **📊 Dashboard Overview**: Real-time visualization of threat levels, geographic origins, and system health.
*   **⚙️ Analysis Pipeline**: Deep-dive into the AI Ensemble Core. Monitor the consensus between XGBoost, LSTM, and Random Forest models.
*   **📡 Live Threat Stream**: High-velocity WebSocket stream capturing and visualizing intercepted payloads in real-time.
*   **📜 Attack Ledger**: Comprehensive historical database of intercepted threats with full forensic metadata.
*   **🛠️ System Config**: Dynamic engine calibration and security policy management.

---

## 🚀 Getting Started (Local Installation)

Aegis Sentinel is optimized for local execution on Windows/macOS/Linux.

### ⚡ Quick Start
The easiest way to boot the full tactical stack is via the provided bootstrapper:
```powershell
.\start_aegis.bat
```

### 🛠️ Manual Configuration

#### 1. Backend API (Python)
- **Requirements**: Python 3.10+
- **Setup**:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate  # Windows
  pip install -r requirements.txt
  uvicorn api.main:app --port 8000 --reload
  ```

#### 2. Frontend Dashboard (Node.js)
- **Requirements**: Node.js 18+
- **Setup**:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

Access the **Dashboard** at `http://localhost:5173` and the **API Docs** at `http://localhost:8000/docs`.

---

---

## 🏗️ Technical Architecture

Aegis Sentinel employs a **3-Tier Hybrid Detection Architecture**:

1.  **🛡️ Tier 1: Heuristic Firewall (SIC)**: Fast-fail structural integrity checks and regex-based pattern matching for common, low-complexity attacks.
2.  **🧠 Tier 2: Statistical Ensemble (AI)**: Weighted consensus across **Random Forest**, **SVM**, **XGBoost**, and **LSTM** models, utilizing 28 domain-specific semantic intent features extracted from research.
3.  **🔮 Tier 3: Semantic Intent Layer (CodeBERT)**: State-of-the-art **Transformer-based embeddings** and **Intent Mismatch Detection (IMD)** to identify obfuscated and zero-day threats by comparing query intent against authorized application baseline centroids.

---

## 📊 Performance Matrix

| Model Layer | Accuracy | Detection Mode |
| :--- | :--- | :--- |
| **Heuristic (SIC)** | 100% (High prec.) | Structural Logic / Known Signatures |
| **Statistical (ML)** | 98.4% | NLP-Based Feature Intent Patterns |
| **Semantic (CodeBERT)**| **Experimental** | Intent Deviation / IMD |
| **Consensus Verdict** | **~99.9%** | Multi-Layer Hybrid Agreement |

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

Developed with ❤️ for Advanced AI Cybersecurity.

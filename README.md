# 👁️ Project Prajā-Netra (प्रजा-नेत्र)
**AI-Powered Multimodal Corruption Tracking & Intelligence Platform**

Project Prajā-Netra is a production-grade, next-generation platform designed to dismantle corruption in public offices. It empowers citizens to report grievances in their native language via text or multimedia evidence. The system uses advanced AI orchestration to translate, triage, and validate reports, transforming raw citizen data into actionable intelligence for authorities.

---

## 🚀 Core Features & Intelligence Layers

### 1. Radical Accessibility (Multilingual Triage)
* **Automatic Language Detection:** Citizens can report in Marathi, Hindi, English, or mixed "Hinglish."

* **Administrative Translation:** The system automatically generates standardized English titles and summaries for every report while preserving the original cultural context.


### 2. Multimodal "Truth Engine"
* **Visual Verification:** Google Gemini 1.5 Flash validates if uploaded photos (evidence) actually support the text description.

* **Forensic Metadata Check:** The system extracts embedded EXIF data (GPS and Timestamp). If a photo is "stale" (older than 30 days) or taken in a different city, the system automatically penalizes the trust score.


### 3. The Case Connector (Semantic Clustering)
* **Systemic Pattern Detection:** Using **ChromaDB**, the system identifies similar complaints filed by different people in the same neighborhood.

* **Recursive Back-linking:** When a "hotspot" is identified, all related past complaints are automatically grouped into a single **Case Cluster**.

* **Sliding Scale Boosting:** Severity scores are dynamically boosted based on the density of similar reports in a specific zone.


### 4. Scalable Asynchronous Architecture
* **Non-Blocking API:** All heavy AI processing (Vision/Text/Vectors) is offloaded to a **Celery Worker** fleet via **Redis**, ensuring the user interface remains lightning-fast.


---

## 🧠 The AI Engine: Where and How it is Used
AI is not a wrapper in this project; it is the primary data processor. It is used in three specific areas:

* **Automated Severity Scoring:** When a complaint is filed, the AI analyzes the text and images to assign a severity score (1-10). High scores (e.g., "Live wire on road") are automatically escalated.

* **Multilingual Summarization:** Since citizens may report in local languages (Marathi/Hindi), the AI generates a concise English summary for official review, ensuring no data is lost in translation.

* **Duplicate Detection:** The AI compares incoming reports against existing ones to identify "clusters" (e.g., 50 people reporting the same pothole), preventing department backlog and identifying hotspots.

---

## ⛓️ The Blockchain: What it is Doing

Blockchain serves as the Immutable Truth Layer. While the main data lives in PostgreSQL for speed, the "Integrity Hash" lives on the ledger.

* **Proof of Existence:** At the moment of filing, a cryptographic hash of the complaint is generated and "anchored" to the blockchain.

* **Anti-Tamper Audit Trail:** If an official tries to delete a complaint or alter its filing date to hide negligence, the hash stored on the blockchain will no longer match the database record.

* **Verifiable Resolution:** When a case is "Resolved," the final evidence is hashed again. Citizens can verify that the "After" state was officially logged and cannot be faked.

---

## 🛠️ Technical Stack
- **Frontend:** React 18, Vite, Tailwind CSS, Chart.js.
- **Backend:** FastAPI (Python 3.10+), SQLAlchemy (Async), Celery, Redis.
- **Database:** PostgreSQL (Relational storage).
- **AI Orchestration:**
  - **Groq (Llama 3.3 70B):** For lightning-fast multilingual text analysis and translation.
  - **Google Gemini 1.5 Flash:** For multimodal vision analysis and evidence cross-validation.
  - **Sentence-Transformers:** Local vector embedding generation (`all-MiniLM-L6-v2`).
- **ORM:** SQLAlchemy 2.0 (Async)
- **Validation:** Pydantic V2
- **Integrity:** Bcrypt (Hashing), JWT (Sessions), Blockchain (Transparency).

---

## 📂 Repository Structure

```
praja-netra/
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── api/                # Axios configuration & interceptors
│   │   ├── context/            # Auth & Theme State Management
│   │   ├── components/         # Reusable UI (Sidebar, KPI Cards)
│   │   └── pages/              # Role-specific Dashboards
│   ├── vercel.json             # Vercel Deployment Rules
│   └── tailwind.config.js      # Custom Design System
└── backend/                    # FastAPI Backend
    ├── app/
    │   ├── api/v1/endpoints/   # Auth, Complaints, & Admin Routes
    │   ├── core/               # Configuration & Security (JWT)
    │   ├── models/             # SQLAlchemy Database Schema
    │   └── services/           # AI & Blockchain Logic
    ├── fix_hash.py             # Security utility for credential seeding
    └── requirements.txt        # Production dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
* Node.js 18+
* Python 3.10+
* PostgreSQL 14+

### 2. Clone the repo: 
```
git clone <repository_url>
```

### 3. Database Setup

1. Create a database named `praja_netra` in pgAdmin.
2. Seed the required Official and Admin accounts:
```
-- Seed Super Admin
INSERT INTO users (email, full_name, role, hashed_password, is_active)
VALUES ('admin.alpha@prajanetra.in', 'System Auditor Alpha', 'SUPER_ADMIN', 'password123', true);

-- Seed Road Dept Official
INSERT INTO users (email, full_name, role, department_id, hashed_password, is_active)
VALUES ('road_officer@pmc.gov.in', 'PMC Road Officer', 'OFFICIAL', 1, 'password123', true);
```

### 4. Start Redis: 
```
docker run -p 6379:6379 redis
```

### 5. Run Worker: 
```
celery -A app.worker.celery_app worker --loglevel=info -P solo
```

### 6. Setup Env: 
Create `.env` with `DATABASE_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`


### 7. Backend Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

### 8. Frontend Installation

```bash
cd frontend
npm install
npm run dev
```

---

## 🏗️ System Architecture
Prajā-Netra uses a **distributed architecture** to ensure high performance under heavy load.
1. **API Layer:** Handles user requests and file uploads.
2. **Message Broker (Redis):** Manages the queue of pending AI analyses.
3. **Worker Layer (Celery):** Independent workers that perform heavy AI computations (Groq/Gemini calls) without slowing down the user experience.

---

## 🔌 API Architecture (v1)

The system uses a RESTful API built with FastAPI, utilizing Pydantic for strict data validation.

### Public / Citizen APIs
| Method | Endpoint             | Description                                                    |
|:-------|:---------------------|:---------------------------------------------------------------|
| `POST` | `/auth/login/google` | Handles OAuth2 tokens and returns a JWT.                       |
| `POST` | `/complaints/`       | Accepts multipart form data (Title, Description, Images, GPS). |
| `GET`  | `/complaints/my`     | Retrieves the logged-in citizen's history.                     |


**POST Body Example:**
```json
{
    "title": "पाणी टँकर माफिया",
    "description": "बाणेर बालेवाडी पट्ट्यात टँकर चालक ५०० रुपये लाच मागत आहेत.",
    "complaint_type": "others",
    "location": "Baner, Pune",
    "is_anonymous": true
}
```

### 📁 Evidence & Intelligence
| Method | Endpoint                           | Description                                                                    |
|:-------|:-----------------------------------|:-------------------------------------------------------------------------------|
| `POST` | `/auth/login/internal`             | Secure endpoint for staff using plain-text (dev) or hashed (prod) credentials. |
| `POST` | `/official/complaints`             | Returns cases filtered by the official's department ID.                        |
| `POST` | `/official/complaints/{id}/status` | Transitions a case status and triggers a blockchain update.                    |
| `POST` | `/analytics/stats/summary`         | Aggregates city-wide data for the Super Admin dashboard.                       |

**Analyze Response Example:**
```json
{
    "status": "Accepted",
    "message": "AI analysis has started in the background.",
    "complaint_id": 1
}
```

---
## ⚙️ Environment Variables (`.env`)
```dotenv
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/praja_netra
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
```

---

## ✅ Features Implemented Until Now
- [x] **Async CRUD Engine:** Full asynchronous database interaction.
- [x] **Multilingual Translation:** Automatic detection and translation of Marathi/Hindi/Spanish etc., into English.
- [x] **AI Triage:** Automated categorization and 1-10 severity scoring.
- [x] **Truth Engine (Vision):** Gemini-powered validation to detect if images match the complaint or are "spam/placeholders."
- [x] **Multi-Image Support:** Weighted scoring based on multiple pieces of evidence.
- [x] **Production Logging:** Comprehensive server and worker logs for debugging.
- [x] **The Case Connector:** Integrated **ChromaDB (Vector DB)** to detect clusters of corruption across different reports.

---

## 📅 Future Roadmap
- **Smart Contracts:** Automated penalty collection for departments that miss SLA deadlines.
- **Edge AI:** Real-time object detection on the citizen's phone to verify issues before they are even submitted.
- **Predictive Maintenance:** AI models to predict where water leakages or road cracks are likely to occur next.

---

## Project Demo Video: 

[Demo Video Links](https://drive.google.com/drive/folders/1oQgb7lOd2AhQGzmGiaZh1zdwz_e5VA_m?usp=sharing)

---
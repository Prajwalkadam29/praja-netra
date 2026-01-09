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

## 🛠️ Technical Stack (Current)
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL (Primary Store)
- **Async Task Queue:** Celery + Redis
- **AI Orchestration:**
  - **Groq (Llama 3.3 70B):** For lightning-fast multilingual text analysis and translation.
  - **Google Gemini 1.5 Flash:** For multimodal vision analysis and evidence cross-validation.
  - **Sentence-Transformers:** Local vector embedding generation (`all-MiniLM-L6-v2`).
- **ORM:** SQLAlchemy 2.0 (Async)
- **Validation:** Pydantic V2

---

## 🏗️ System Architecture
Prajā-Netra uses a **distributed architecture** to ensure high performance under heavy load.
1. **API Layer:** Handles user requests and file uploads.
2. **Message Broker (Redis):** Manages the queue of pending AI analyses.
3. **Worker Layer (Celery):** Independent workers that perform heavy AI computations (Groq/Gemini calls) without slowing down the user experience.



---

## 📁 API Documentation (Implemented)

### 📝 Complaint Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/complaints/` | Submit a new complaint (Multilingual). |
| `GET` | `/api/v1/complaints/` | List all complaints with pagination. |
| `GET` | `/api/v1/complaints/{id}` | Get detailed status of a specific complaint. |
| `PATCH` | `/api/v1/complaints/{id}` | Update status or severity (Admin). |
| `DELETE` | `/api/v1/complaints/{id}` | Remove complaint and associated evidence. |

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
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/complaints/{id}/evidence` | Upload images/documents as proof. |
| `POST` | `/api/v1/complaints/{id}/analyze` | **Trigger Background AI Analysis.** (Returns immediate receipt). |

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
- **Module 6: Blockchain Integrity:** Hashing report data on-chain to prevent record tampering.
- **Module 7: Anonymization Layer:** Auto-redacting PII (Names/Faces) from public-facing data.
- **Module 8: Dashboard & GIS:** Next.js frontend with heatmaps showing "Corruption Hotspots" in Pune.
- **Module 9: Notifications:** Real-time updates via WebSockets and SMS/Email.

---

## 🛠️ Setup & Installation
1. **Clone the repo:** `git clone <repository_url>`
2. **Setup Env:** Create `.env` with `DATABASE_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`.
3. **Start Redis:** `docker run -p 6379:6379 redis`
4. **Run Worker:** `celery -A app.worker.celery_app worker --loglevel=info -P solo`
5. **Run Server:** `python -m app.main`
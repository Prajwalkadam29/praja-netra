# 👁️ Project Prajā-Netra (प्रजा-नेत्र)
**AI-Powered Multimodal Corruption Tracking & Intelligence Platform**

Project Prajā-Netra is a production-grade, next-generation platform designed to dismantle corruption in public offices. It empowers citizens to report grievances in their native language via text or multimedia evidence. The system uses advanced AI orchestration to translate, triage, and validate reports, transforming raw citizen data into actionable intelligence for authorities.

---

## 🚀 Core Pillars
- **Radical Accessibility:** Report in any language (Marathi, Hindi, English, etc.) via text or image.
- **AI-Driven Triage:** Automated severity scoring and categorization using LLMs.
- **Evidence Validation:** A "Truth Engine" that cross-references visual evidence with text descriptions.
- **Scalable Architecture:** Built with an asynchronous, non-blocking background tasking system.

---

## 🛠️ Technical Stack (Current)
- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL (Primary Store)
- **Async Task Queue:** Celery + Redis
- **AI Orchestration:**
  - **Groq (Llama 3.3 70B):** For lightning-fast multilingual text analysis and translation.
  - **Google Gemini 1.5 Flash:** For multimodal vision analysis and evidence cross-validation.
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

### 📁 Evidence & Intelligence
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/complaints/{id}/evidence` | Upload images/documents as proof. |
| `POST` | `/api/v1/complaints/{id}/analyze` | **Trigger Background AI Analysis.** (Returns immediate receipt). |

---

## ✅ Features Implemented Until Now
- [x] **Async CRUD Engine:** Full asynchronous database interaction.
- [x] **Multilingual Translation:** Automatic detection and translation of Marathi/Hindi/Spanish etc., into English.
- [x] **AI Triage:** Automated categorization and 1-10 severity scoring.
- [x] **Truth Engine (Vision):** Gemini-powered validation to detect if images match the complaint or are "spam/placeholders."
- [x] **Multi-Image Support:** Weighted scoring based on multiple pieces of evidence.
- [x] **Production Logging:** Comprehensive server and worker logs for debugging.

---

## 📅 Future Roadmap
- **Module 5: The Case Connector:** Integrating **ChromaDB (Vector DB)** to detect clusters of corruption across different reports.
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
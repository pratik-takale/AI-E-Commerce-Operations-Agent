# System Architecture
```mermaid
flowchart LR
  U[React Customer Chat] --> API[FastAPI Backend]
  A[React Admin Dashboard] --> API
  API --> SUP[Supervisor Agent - LangGraph]
  SUP --> PA[Product Agent]
  SUP --> IA[Inventory Agent]
  SUP --> OA[Order Agent]
  SUP --> CA[Support Agent]
  PA --> VDB[(Vector DB)]
  PA --> SVC[Service Layer]
  IA --> SVC
  OA --> SVC
  CA --> SVC
  SVC --> PG[(PostgreSQL)]
  API --> R[(Redis)]
  SUP --> LLM[LLM Provider]
```
ai-ecommerce-ops-agent/
├── backend/
│   └── app/
│       ├── api/        (routers)
│       ├── agents/     (LangGraph nodes, tools)
│       ├── services/   (business logic)
│       ├── models/     (SQLAlchemy)
│       ├── schemas/    (Pydantic)
│       └── core/       (config, security)
├── frontend/
│   └── src/
│       ├── pages/
│       ├── components/
│       └── api/
├── docs/
└── README.md
> Status: Draft
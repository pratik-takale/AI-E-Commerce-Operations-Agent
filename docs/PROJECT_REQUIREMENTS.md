# Project Requirements

> Status: Draft v1
> Project: AI E-Commerce Operations Agent

## 1. Overview

AI E-Commerce Operations Agent is an AI-powered platform where specialized agents assist customers and operations teams. The system answers product questions, checks inventory, tracks orders, handles customer issues and coordinates operational workflows, while maintaining conversation and transaction state.

**Objective:** Build an agentic commerce assistant that understands customer requests, retrieves product and order information, calls operational APIs, decides the right action and replies with context.

**Users:**
- **Customer:** chats with the assistant to get help.
- **Admin:** manages products, inventory, orders and complaints from a web dashboard.

**Tech stack:** React (frontend), FastAPI (backend), PostgreSQL, Redis, LangChain/LangGraph, RAG with a vector database, Postman, Git and GitHub, PaaS deployment.

## 2. AI Agents

### 2.1 Agent Summary

| # | Agent | Responsibility | Tools | Needs Human Approval |
|---|-------|----------------|-------|----------------------|
| 1 | Supervisor (Router) | Classify intent, route to agents, manage conversation state, compose final reply | LangGraph router, Redis session | No |
| 2 | Product Knowledge | Answer product questions and search products (RAG) | Vector DB, GET /products, GET /products/search | No |
| 3 | Inventory | Check stock, low-stock alerts, admin stock updates | GET/PATCH /inventory | Stock updates: admin only |
| 4 | Order Tracking | Order status, shipment details, order history | GET /orders/{id}, GET /orders/my | No |
| 5 | Support & Escalation | Cancellation requests, complaints, refunds, escalation | POST /orders/{id}/cancel, POST /complaints | Shipped-order cancellation and refunds |

### 2.2 Agent Details

#### Agent 1: Supervisor Agent
- **Input:** user message, session_id, conversation history
- **Output:** selected agent(s) and final reply
- **Example:** "Where is my order?" is routed to the Order Tracking Agent.
- **Limitations:** does not access the database directly; asks a clarifying question when intent is unclear.

#### Agent 2: Product Knowledge Agent
- **Input:** product question or search keywords
- **Output:** product information or a list of matching products
- **Example:** "Is this phone waterproof?" or "Show headphones under 5000."
- **Limitations:** answers only from retrieved documents and database results; never invents product facts.

#### Agent 3: Inventory Agent
- **Input:** product id or name, variant or size
- **Output:** available quantity and in-stock or out-of-stock status
- **Example:** "Is size M available?"
- **Limitations:** only admins can change stock; customers can only read it.

#### Agent 4: Order Tracking Agent
- **Input:** order id and the logged-in user
- **Output:** order status, tracking number, estimated delivery date
- **Example:** "Where is my order #1042?"
- **Limitations:** a customer can see only their own orders; another user's order returns "not found".

#### Agent 5: Support & Escalation Agent
- **Input:** complaint text, order id, cancellation reason
- **Output:** ticket or request id and the next step
- **Example:** "I want to cancel this order." or "I received a damaged item."
- **Limitations:** creates requests only; final approval for shipped-order cancellation and refunds belongs to the admin.

### 2.3 Agent Interaction
- The customer talks only to the Supervisor Agent.
- The Supervisor routes the request to one or more agents.
- Agents call tools (service layer, vector DB) and return results.
- The Supervisor composes the final reply.
- If one message contains two intents (multi-intent), both agents run and the reply is combined.

### 2.4 Human-in-the-Loop Rules

| Action | Agent can do alone? | Approver |
|--------|---------------------|----------|
| Show order status | Yes | None |
| Check stock | Yes | None |
| Cancel a pending order | Yes (by rule) | None |
| Cancel a shipped order | No | Admin |
| Issue refund | No | Admin |
| Change stock or price | No | Admin (dashboard) |

## 3. Use Cases

### 3.1 Summary

| ID | Actor | Use Case | Agent |
|----|-------|----------|-------|
| CU-01 | Customer | Ask product questions | Product Knowledge |
| CU-02 | Customer | Search products | Product Knowledge |
| CU-03 | Customer | Check stock | Inventory |
| CU-04 | Customer | Track order | Order Tracking |
| CU-05 | Customer | Request cancellation | Support & Escalation |
| CU-06 | Customer | Raise complaint | Support & Escalation |
| AD-01 | Admin | Manage products | Dashboard (CRUD) |
| AD-02 | Admin | Update inventory | Dashboard |
| AD-03 | Admin | View all orders | Dashboard |
| AD-04 | Admin | Handle complaints | Dashboard |
| AD-05 | Admin | Approve or reject cancellations | Dashboard |
| AD-06 | Admin | Monitor operations | Dashboard |

### 3.2 Customer Use Cases

#### CU-01: Ask a product question
- **Actor:** Customer
- **Trigger:** Customer types a product question in chat.
- **Main flow:**
  1. Supervisor classifies the intent as a product question.
  2. Product Agent retrieves relevant content from the vector DB.
  3. The reply is generated from the retrieved content.
- **Failure case:** No relevant content is found. The agent says it does not know and offers to contact support.

#### CU-02: Search products
- **Actor:** Customer
- **Trigger:** "Show headphones under 5000."
- **Main flow:**
  1. Supervisor identifies a search intent.
  2. Product Agent calls `GET /products/search` with keyword, category and price.
  3. A list of matching products (name, price, stock) is shown.
- **Failure case:** No product matches. The agent says so and suggests similar options.

#### CU-03: Check stock
- **Actor:** Customer
- **Trigger:** "Is size M available?"
- **Main flow:**
  1. Supervisor identifies a stock intent.
  2. Inventory Agent finds the product and calls `GET /inventory/{product_id}`.
  3. The reply shows availability and quantity.
- **Failure case:** The product name is ambiguous. The agent asks which product the customer means.

#### CU-04: Track order
- **Actor:** Customer (logged in)
- **Trigger:** "Where is my order #1042?"
- **Main flow:**
  1. Supervisor identifies an order intent.
  2. Order Agent calls `GET /orders/1042`.
  3. The system checks that the order belongs to the user.
  4. The reply shows status, tracking number and estimated delivery.
- **Failure case:** Wrong id or another user's order. The agent says the order was not found and reveals nothing else.

#### CU-05: Request cancellation
- **Actor:** Customer
- **Trigger:** "I want to cancel this order."
- **Main flow:**
  1. Supervisor routes to the Support Agent.
  2. The agent checks the order status.
  3. If `pending`, the order is cancelled by rule.
  4. If `shipped`, a cancellation request is created and sent to the admin.
  5. The customer receives a request id.
- **Failure case:** The order is already `delivered`. Cancellation is refused and the agent suggests return or refund.

#### CU-06: Raise complaint
- **Actor:** Customer
- **Trigger:** "I received a damaged product."
- **Main flow:**
  1. Support Agent asks for the subject and order id.
  2. `POST /complaints` creates the complaint.
  3. The customer receives a ticket id.
  4. The complaint appears on the admin dashboard.
- **Failure case:** No order id given. The complaint is saved as general and the agent asks for the order id if possible.

### 3.3 Admin Use Cases

#### AD-01: Manage products
- **Actor:** Admin
- **Trigger:** Admin clicks Add or Edit Product on the dashboard.
- **Main flow:**
  1. Admin fills in name, description, price and category.
  2. `POST /products`, `PUT /products/{id}` or `DELETE /products/{id}` is called.
  3. The product list updates.
  4. The product text is re-indexed in the vector DB for RAG.
- **Failure case:** A required field is missing. A 422 validation error is returned.

#### AD-02: Update inventory
- **Actor:** Admin
- **Trigger:** New stock arrives or stock is counted.
- **Main flow:**
  1. Admin selects a product and enters the new quantity.
  2. `PATCH /inventory/{product_id}` is called.
  3. If quantity is below `reorder_level`, a low-stock warning is shown.
- **Failure case:** A negative quantity is rejected.

#### AD-03: View all orders
- **Actor:** Admin
- **Trigger:** Admin opens the Orders page.
- **Main flow:**
  1. `GET /admin/orders` is called.
  2. Admin filters by status, date or customer.
  3. Clicking an order shows items and shipment details.
- **Failure case:** A non-admin user receives 403 Forbidden.

#### AD-04: Handle complaints
- **Actor:** Admin
- **Trigger:** A new complaint appears on the dashboard.
- **Main flow:**
  1. Admin opens the complaint and sets priority.
  2. Admin assigns it to a staff member or self.
  3. Admin writes a reply.
  4. Status moves from `open` to `in_progress` to `resolved`.
- **Failure case:** A resolved complaint cannot be reopened. The customer raises a new one.

#### AD-05: Approve or reject cancellations
- **Actor:** Admin
- **Trigger:** A cancellation request for a shipped order arrives.
- **Main flow:**
  1. Admin reads the request and reason.
  2. `PATCH /admin/cancellations/{id}` sets `approved` or `rejected`.
  3. If approved, the order becomes `cancelled` and stock is restored.
  4. The customer is informed.
- **Failure case:** The order was delivered in the meantime. The request is rejected automatically.

#### AD-06: Monitor operations
- **Actor:** Admin
- **Trigger:** Admin opens the dashboard home.
- **Main flow:**
  1. `GET /admin/stats` shows orders today, open complaints and low-stock products.
  2. `GET /admin/agent-logs` shows what each agent did.
- **Failure case:** Data fails to load. That widget shows a Retry option and the rest of the page keeps working.

## 4. Project Scope

### 4.1 In Scope (MVP)

| Customer functionality | Admin functionality |
|------------------------|---------------------|
| Ask product questions | Manage products |
| Search products | Update inventory |
| Check stock | View all orders |
| Track orders | Handle complaints |
| Request cancellation | Monitor operations |

Technical scope:
- React frontend (customer chat and admin dashboard)
- FastAPI REST backend
- PostgreSQL and Redis
- Five AI agents with LangGraph
- RAG with a vector database
- JWT authentication with customer and admin roles
- API testing with Postman
- Deployment on a PaaS with a public URL

### 4.2 Out of Scope

| Item | Reason |
|------|--------|
| Real payment gateway | Not the focus; adds time |
| Real courier integration | Mock shipping data is used instead |
| Multi-language support | English first |
| Voice input | Extra complexity |
| Mobile app | Web only |
| Email and SMS notifications | Dashboard status is enough |
| Reviews and recommendations | Later phase |

## 5. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The system shall let users register and log in with email and password. |
| FR-02 | The system shall support two roles: customer and admin. |
| FR-03 | The system shall accept chat messages and route them to the correct agent. |
| FR-04 | The system shall answer product questions using RAG over product data. |
| FR-05 | The system shall search products by keyword, category and price. |
| FR-06 | The system shall show stock availability for a product. |
| FR-07 | The system shall show order status and shipment details to the order owner only. |
| FR-08 | The system shall let customers request order cancellation. |
| FR-09 | The system shall let customers raise complaints and return
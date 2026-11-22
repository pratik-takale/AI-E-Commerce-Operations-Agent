# Project Requirements

## 1. Overview

AI E-Commerce Operations Agent is a platform where specialized AI agents
help customers and admins with product questions, inventory, order
tracking, and customer issues.

## 2. AI Agents

### 2.1 Agent Summary

| #   | Agent                | Responsibility                                                                  | Tools                                          | Needs Human Approval                   |
| --- | -------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------- | -------------------------------------- |
| 1   | Supervisor (Router)  | Classify intent, route to agent, manage conversation state, compose final reply | LangGraph router, Redis session                | No                                     |
| 2   | Product Knowledge    | Answer product questions, search products (RAG)                                 | Vector DB, GET /products, GET /products/search | No                                     |
| 3   | Inventory            | Check stock, low-stock alerts, admin stock updates                              | GET/PATCH /inventory                           | Stock updates: admin only              |
| 4   | Order Tracking       | Order status, shipment details, order history                                   | GET /orders/{id}, GET /orders/my               | No                                     |
| 5   | Support & Escalation | Cancellation requests, complaints, refunds, escalation                          | POST /orders/{id}/cancel, POST /complaints     | Shipped-order cancellation and refunds |

### 2.2 Agent Details

#### Supervisor Agent

- **Input:** user message, session_id, conversation history
- **Output:** selected agent and final reply
- **Example:** "Where is my order?" -> routes to Order Tracking Agent
- **Limitations:** does not access the database directly

(Repeat the same format for the other four agents:
Input, Output, Example, Limitations)

### 2.3 Agent Interaction

- The customer talks only to the Supervisor.
- The Supervisor routes the request to one or more agents.
- Agents call tools (APIs, vector DB) and return results.
- The Supervisor composes the final reply.

### 2.4 Human-in-the-Loop Rules

- Shipped-order cancellation requires admin approval.
- Refunds require admin approval.
- Customers can access only their own orders.
- Inventory and price changes are admin-only.

## 3. Use Cases

### 3.1 Summary

| ID    | Actor    | Use Case                     | Agent                 |
| ----- | -------- | ---------------------------- | --------------------- |
| CU-01 | Customer | Ask product questions        | Product Knowledge     |
| CU-02 | Customer | Search products              | Product Knowledge     |
| CU-03 | Customer | Check stock                  | Inventory             |
| CU-04 | Customer | Track order                  | Order Tracking        |
| CU-05 | Customer | Request cancellation         | Support & Escalation  |
| CU-06 | Customer | Raise complaint              | Support & Escalation  |
| AD-01 | Admin    | Manage products              | Dashboard (CRUD)      |
| AD-02 | Admin    | Update inventory             | Dashboard / Inventory |
| AD-03 | Admin    | View all orders              | Dashboard             |
| AD-04 | Admin    | Handle complaints            | Dashboard             |
| AD-05 | Admin    | Approve/reject cancellations | Dashboard             |
| AD-06 | Admin    | Monitor operations           | Dashboard             |

### 3.2 Customer Use Cases

#### CU-01: Ask a product question

- **Actor:** Customer
- **Trigger:** Customer types a product question in chat
- **Main flow:**
  1. Supervisor classifies intent as product question
  2. Product Agent retrieves relevant content from the vector DB
  3. Reply is generated from retrieved content
- **Failure case:** No relevant content found -> agent says it does not
  know and offers to contact support

(Repeat for CU-02 to CU-06, then AD-01 to AD-06)

> Status: Draft

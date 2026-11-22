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
  > Status: Draft

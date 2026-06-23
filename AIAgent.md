# AI Data Analysis Agent Architecture

## Overview

An AI Data Analysis Agent combines:

- A Large Language Model (LLM)
- Tool Calling
- Databases
- Knowledge Bases (RAG)
- Action Systems

The agent acts as an intelligent orchestrator that can:

1. Understand user requests
2. Retrieve data from databases
3. Search documentation or knowledge bases
4. Analyze results
5. Make decisions
6. Trigger actions
7. Generate reports

---

# High-Level Architecture

```text
                    ┌─────────────────────┐
                    │      User Query     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Agent          │
                    │  (Reasoning Layer)  │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼

   ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
   │ SQL Database  │  │ Vector Search  │  │ External APIs  │
   │ PostgreSQL    │  │ ChromaDB       │  │ ERP / CRM      │
   │ MySQL         │  │ Pinecone       │  │ Weather APIs   │
   └───────┬───────┘  └───────┬────────┘  └────────┬───────┘
           │                  │                    │
           └──────────────────┼────────────────────┘
                              ▼

                    ┌─────────────────────┐
                    │ Data Analysis Layer │
                    │ Statistics          │
                    │ Trends              │
                    │ Anomalies           │
                    └──────────┬──────────┘
                               │
                               ▼

                    ┌─────────────────────┐
                    │ Action Layer        │
                    │ Alerts              │
                    │ Emails              │
                    │ Tickets             │
                    └──────────┬──────────┘
                               │
                               ▼

                    ┌─────────────────────┐
                    │ Final Response      │
                    └─────────────────────┘
```

---

# Core Components

## 1. LLM Layer

The LLM acts as the brain of the system.

Responsibilities:

- Understand user intent
- Decide which tools to use
- Analyze tool outputs
- Generate recommendations
- Determine whether actions are required

Example:

```python
agent = Agent(
    model=model,
    tools=[query_database, search_kb, send_alert]
)
```

---

## 2. Tool Layer

Tools allow the LLM to interact with external systems.

Examples:

```python
@tool
def query_database(sql: str):
    pass

@tool
def search_kb(query: str):
    pass

@tool
def send_alert(message: str):
    pass
```

The LLM chooses when to call these tools.

---

## 3. Structured Data Sources

Examples:

- PostgreSQL
- MySQL
- Snowflake
- BigQuery
- SQL Server

Example Table:

```sql
temperature_readings

id
timestamp
temperature
location
```

Example Query:

```sql
SELECT *
FROM temperature_readings
WHERE timestamp > NOW() - INTERVAL '7 days';
```

---

## 4. Knowledge Base (RAG)

Used for:

- PDFs
- Documentation
- Wikis
- Support tickets
- Incident reports

Common Vector Databases:

- ChromaDB
- Pinecone
- Weaviate
- Qdrant

Example Flow:

```text
Question
    ↓
Vector Search
    ↓
Relevant Documents
    ↓
LLM Analysis
```

---

## 5. Analytics Layer

For large datasets, calculations should be done by code instead of the LLM.

Example:

```python
@tool
def calculate_statistics(data):
    import pandas as pd

    return {
        "mean": data.mean(),
        "max": data.max(),
        "min": data.min()
    }
```

Advantages:

- More accurate
- Faster
- Handles large datasets

---

## 6. Action Layer

Actions allow the agent to affect external systems.

Examples:

### Email

```python
send_email()
```

### Slack

```python
send_slack_message()
```

### Jira

```python
create_ticket()
```

### Database Update

```python
update_record()
```

### Webhook

```python
requests.post(...)
```

---

# Example Agent Implementation

## Database Tool

```python
from strands import tool
import sqlite3

@tool
def query_database(sql: str) -> str:
    conn = sqlite3.connect("sensor_data.db")

    cursor = conn.cursor()
    cursor.execute(sql)

    rows = cursor.fetchall()

    conn.close()

    return str(rows)
```

---

## Alert Tool

```python
from strands import tool

@tool
def send_alert(message: str) -> str:
    print(f"ALERT: {message}")
    return "Alert sent"
```

---

## Knowledge Search Tool

```python
@tool
def search_knowledge_base(query: str) -> str:
    results = vector_db.similarity_search(query, k=5)

    return "\n".join(
        doc.page_content
        for doc in results
    )
```

---

## Create Model

```python
from strands.models.anthropic import AnthropicModel

model = AnthropicModel(
    model_id="claude-3-5-sonnet-latest",
    max_tokens=2000
)
```

---

## System Prompt

```python
SYSTEM_PROMPT = """
You are a senior data analyst.

Responsibilities:

1. Analyze database records.
2. Identify trends.
3. Detect anomalies.
4. Search knowledge base if needed.
5. Recommend actions.
6. Trigger alerts when thresholds are exceeded.

Always provide:

- Summary
- Findings
- Risks
- Recommendations
"""
```

---

## Create Agent

```python
from strands import Agent

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        query_database,
        search_knowledge_base,
        send_alert
    ]
)
```

---

# Example User Request

```python
result = agent("""
Analyze temperature data for the last 7 days.

Tasks:

1. Calculate averages.
2. Detect anomalies.
3. Compare with historical patterns.
4. Send alert if temperature > 80.
5. Provide recommendations.
""")
```

---

# Internal Agent Workflow

```text
User Request
      │
      ▼
Understand Intent
      │
      ▼
Need Data?
      │
      ▼
Query Database
      │
      ▼
Receive Results
      │
      ▼
Need More Context?
      │
      ▼
Search Knowledge Base
      │
      ▼
Analyze Findings
      │
      ▼
Decision Making
      │
      ├───────────────┐
      ▼               ▼

Normal          Critical

Generate        Send Alert
Report             │
      │            ▼
      └────► Final Response
```

---

# Example Scenario

## User Request

```text
Analyze last month's sales performance.
```

---

## Step 1: Query Database

```sql
SELECT *
FROM sales
WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days';
```

---

## Step 2: Analyze

Agent discovers:

```text
Revenue dropped by 35%.
```

---

## Step 3: Search Knowledge Base

Agent searches:

```text
Revenue decline causes
```

Finds:

```text
Inventory shortage reported.
```

---

## Step 4: Action

Agent sends alert:

```python
send_alert(
    "Revenue down 35% due to inventory shortage"
)
```

---

## Step 5: Final Output

```text
Sales Analysis Report

Summary:
Revenue decreased by 35%.

Findings:
Inventory shortages impacted key products.

Risk:
Continued shortages may affect next quarter.

Recommendation:
Increase inventory levels and review suppliers.

Action:
Alert sent to operations team.
```

---

# Production Architecture

```text
                     ┌───────────────┐
                     │     User      │
                     └───────┬───────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ API Gateway        │
                  └─────────┬──────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ Agent Service      │
                  └─────────┬──────────┘
                            │
         ┌──────────────────┼───────────────────┐
         │                  │                   │
         ▼                  ▼                   ▼

 ┌──────────────┐  ┌────────────────┐  ┌────────────────┐
 │ LLM Service  │  │ Tool Registry  │  │ Memory Layer   │
 └──────┬───────┘  └───────┬────────┘  └────────┬───────┘
        │                  │                    │
        ▼                  ▼                    ▼

 ┌──────────────┐  ┌────────────────┐  ┌────────────────┐
 │ PostgreSQL   │  │ Vector DB      │  │ Redis Cache    │
 │ MySQL        │  │ Pinecone       │  │ Session Store  │
 └──────────────┘  └────────────────┘  └────────────────┘

                            │
                            ▼

                 ┌────────────────────┐
                 │ Action Services    │
                 │ Slack              │
                 │ Email              │
                 │ Jira               │
                 │ Webhooks           │
                 └────────────────────┘
```

---

# Best Practices

## Use the LLM for

- Reasoning
- Planning
- Summarization
- Recommendations

## Use Code for

- Calculations
- Statistics
- Data transformations
- SQL execution

## Use Vector Search for

- Documentation
- Historical incidents
- Knowledge retrieval

## Use Action Tools for

- Notifications
- Ticket creation
- Workflow automation

---

# Key Principle

The LLM should act as the **orchestrator**, not the database, analytics engine, or notification system.

A production AI agent works best when:

```text
LLM
  +
Tools
  +
Databases
  +
Knowledge Base
  +
Action Systems
  =
Autonomous Business Agent
```

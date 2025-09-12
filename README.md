# Noma Security Home Assignment

# 1. Define the Problem Space

## Context

I believe that the onboarding process looks like this:

1. Identify and dig into the client's pain.
2. Show a demo of Noma's solution.
3. Connect to the client's agent platform (e.g., LangChain, Bedrock, Databricks) in monitor-only mode to surface how many vulnerabilities exist, emphasizing the need for Noma.
4. Noma's Solutions Engineering team then works with the prospect to sign a trade-off policy agreement.

Noma cannot block all vulnerabilities by default:

- Some vulnerabilities must be blocked no matter what (non-negotiable security).
- Some should only trigger alerts (so the workflow continues).
- Some the client may prefer to allow, even if risky, because breaking the agent workflow would hurt usability or user experience.

Noma therefore needs the prospect to agree on this trade-off policy, which requires buy-in from both the CISO's security team and the Product leadership (CPO/VP Product) on the client side.

In enterprise sales, time kills deals: the longer the process drags, the lower the chances of closing. Every week shaved off onboarding translates directly into faster revenue recognition and higher growth.

I decided to choose to tackle this issue - making the tradeoff policy process faster and easier, so that the whole onboarding process will be shorter and therefore the success rate will grow.

## Primary Users

The Solutions Engineering team at Noma. They are responsible for guiding clients through onboarding, negotiating the trade-off policies, and ensuring a smooth technical rollout.

## Core Outcomes to Improve

1. **Reduce time-to-onboard-** Faster alignment on policy means more customers can be onboarded per quarter.
2. **Increase deal conversion rate-** Streamlining a friction-heavy process increases the percentage of pilots that convert into paying customers.
3. **Save valuable Solutions Engineering time-** Free SEs from manual back-and-forth so they can support more customers and avoid becoming a bottleneck.

---

# 2. Design Options & Prioritization

## Option 1 - Manual Internal Scenario Team

Noma can create a dedicated internal team of Solutions Engineers and Product Managers who "put themselves in the client's shoes." For each onboarding, they would manually review the client's environment, brainstorm possible agent scenarios, debate trade-offs internally, and then present the client with a set of options and a recommended policy.

- **Quality of Output:** Medium - depends on human judgment, inconsistent across teams.
- **Complexity to Build:** Low - relies mostly on meetings and manual work.
- **Scalability:** Low - extremely time-consuming, requiring long multi-person meetings and multiple iterations per client. SE team becomes a bottleneck.
- **Time-to-First-Value:** High - can start immediately, but at a heavy time cost.

---

## Option 2 - AI Tool Using External Data (Speculative)

An AI system scrapes or collects external information (press releases, job postings, public talks) to speculate which agents a company might be using, what their goals are, and where risks could exist. It then generates trade-off policy recommendations based on those assumptions.

- **Quality of Output:** Low-Medium - speculative, often inaccurate or irrelevant.
- **Complexity to Build:** Medium-High - requires scraping pipelines, data processing, and scenario simulation logic.
- **Scalability:** Medium - once built, could be applied across many accounts, but usefulness is limited by poor accuracy.
- **Time-to-First-Value:** Medium - results appear quickly, but quality is questionable.

---

## Option 3 - AI Tool Using Monitoring Data (Simulation-Driven)

After the client connects Noma in **monitor-only mode**, the system uses real agent data (which agents exist, what their roles and tools are, and which risks have already surfaced). It then simulates multiple scenarios where vulnerabilities might appear, analyzes fallout if actions were blocked vs allowed, and generates trade-off policy recommendations with options (Block / Alert / Allow). The result is a structured draft of the agreement for review and signoff.

- **Quality of Output:** High - grounded in real client environment, evidence-based.
- **Complexity to Build:** Medium-High - similar to Option 2, requires scenario simulation and data processing, but with accurate inputs.
- **Scalability:** High - once built, can be reused across many clients with minimal incremental cost.
- **Time-to-First-Value:** Medium - requires a few weeks after monitor-only access, but delivers highly credible results.

## Quick Comparison of Options

| 📊 Criteria | Option 1 - Manual Internal Scenario Team | Option 2 - External Data (Speculative) | Option 3 - Monitoring Data (Simulation-Driven) |
|-------------|----------------------------------------|---------------------------------------|---------------------------------------------|
| Quality of Output | Medium | Low-Medium | High |
| Complexity to Build | Low | Medium-High | Medium-High |
| Scalability | Low | Medium | High |
| Time-to-First-Value | High | Medium | Medium |

## Prioritization & Choice

I choose **Option 3 - Monitoring-Driven Simulation**.

**Why:**

- Option 1 is structured but fatally unscalable. It would consume enormous time from SEs and PMs, with long, multi-person meetings for every client. It eases the customer's process slightly, but at the cost of Noma's growth capacity.
- Option 2 may look innovative, but it is speculative and inaccurate. The complexity is just as high as Option 3, but the quality of output is too low to earn client trust.
- Option 3 uses real client data to generate evidence-based policy drafts. Clients can trust and act on these quickly, cutting onboarding time, saving Solutions Engineering resources, and allowing Noma to scale to more deals per quarter.

For this project we focus on normalizing LangChain and LangSmith exports into a small set of clean CSV tables that preserve the run tree and key details, so all downstream logic in our simulator and policy UI works off the normalized CSVs only, not the raw trace format.

---

# 3. Mock Database

## agents.csv

**Columns:**
- `agent_id`
- `agent_name` 
- `purpose_summary`
- `created_at` (ISO 8601)

**Why:** Keep it lean. This file is just the catalog of agents you'll reference from runs. You don't need more here to drive the mock or UI.

## runs.csv

**Columns:**
- `run_id`
- `agent_id` ← FK to agents
- `started_at` (ISO 8601)
- `ended_at` (ISO 8601)
- `status` (`success` | `error`)
- `user_input_summary` ← short plain text like "plan BBQ for 12 people"

## actions.csv

**Columns:**
- `action_id`
- `run_id` ← FK to runs
- `action_type` (`tool` | `retrieval`)
- `action_name`
- `started_at` (ISO 8601)
- `ended_at` (ISO 8601)
- `success` (true|false)
- `destination_domain` ← null for retrievals
- `data_classes_detected_json` ← e.g. `["PII","PCI"]`

## monitoring.csv

**Columns:**
- `scenario_id`
- `action_id` ← FK to actions
- `vuln_type` ← e.g. `PII_to_third_party`, `PHI_to_sentiment_api`, `Secrets_to_GitHub`
- `severity` (`low` | `medium` | `high`)
- `recommended_option` (`Block` | `Alert` | `Sanitize_and_allow` | `Allow`)

---

# 4. Agents Architecture

## 1. Data Analyzer Agent

**Job:** First component in the workflow - analyzes customer data to understand their AI agent capabilities

**Responsibilities:**
- Processes customer CSV data (agents.csv, actions.csv, runs.csv, monitoring.csv)
- Builds capability maps for each customer agent
- Identifies tools, endpoints, and sensitive data access patterns
- Creates structured profiles that inform prospect agent creation
- Sends analyzed data to Prospect Agent Factory for agent creation

**Output:** Capability maps that define what each customer agent can do, what tools they use, and what data they access

**Data Flow:** Data Analyzer → Prospect Agent Factory → Prospect Agents

---

## 2. Prospect Agents

**Job:** Represent the target AI agents that get attacked during security testing

**Responsibilities:**
- Simulate realistic company agent behavior
- Respond to social engineering attempts
- Use tools and access data as defined by their capability maps
- Provide realistic responses to hacker agent probes
- Exhibit both secure and vulnerable behaviors based on their design

**Output:** Realistic AI agent responses that reveal security vulnerabilities

---

## 3. Hacker Agent

**Job:** Intelligent attacker that conducts sophisticated security assessments

**Responsibilities:**
- Conducts reconnaissance to learn about target agents
- Adapts attack strategies based on discovered information
- Uses memory systems to learn from previous interactions
- Applies sophisticated social engineering techniques
- Generates evidence of successful attacks
- Makes strategic decisions about when to continue, pivot, or switch targets
- Implements different attack approaches (GitHub secrets, PHI leaks, card data)
- Generates realistic malicious customer personas
- Provides variety in attack methodologies

**Output:** Detailed attack episodes with evidence of security vulnerabilities

---

## 4. Vulnerability Analyzer Agent

**Job:** Analyzes attack results to extract specific security vulnerabilities

**Responsibilities:**
- Processes conversation logs from attack episodes
- Identifies specific vulnerability scenarios using LLM analysis
- Categorizes vulnerabilities by type and risk level
- Extracts evidence from actual conversations
- Provides concrete proof of security issues

**Output:** Structured vulnerability scenarios with evidence and risk assessments

---

## 5. Policy Generator Agent

**Job:** Creates comprehensive security policies with tradeoff analysis

**Responsibilities:**
- Analyzes vulnerability scenarios to generate policy options
- Provides three policy approaches: Block, Sanitize, Allow
- Conducts detailed tradeoff analysis for each option
- Considers business impact and user experience
- Recommends optimal policy approaches
- Generates implementation guidance

**Output:** Comprehensive security policies with detailed tradeoff analysis

## Supporting Components (Not Agents)

### Workflow Manager

**Job:** Orchestrates the complete end-to-end workflow and coordinates all agents

### Prospect Agent Factory

**Job:** Factory class that creates prospect agents based on capability maps from Data Analyzer

### A2A Communication Framework

**Job:** Enables realistic AI-to-AI agent interactions using the A2A SDK

**Responsibilities:**
- Facilitates authentic agent-to-agent conversations
- Manages A2A session lifecycle and message routing
- Provides structured communication protocols for security testing
- Enables realistic social engineering scenarios between agents

---

# 5. Challenge: Ineffective Hacker Agent Strategies

## Problem

The hacker agent failed at realistic security testing because it stayed in discovery too long, ignored revealed intel, repeated failing tactics, and had no memory of past interactions.

## Symptoms

- Asked about tools but ignored answers
- Continued generic questions after learning specifics
- Reused the same social engineering trick
- No escalation or pivots when blocked

## Root Cause

No decision-making framework or persistent memory to guide adaptive attacks.

## Fixes

1. **Memory Systems-** working context, semantic memory (tools/endpoints), profile memory, attack history.
2. **Strategy Tools-** authority role, exploit mentioned features, compliance pressure, urgent scenarios, technical escalation.
3. **Decision-Making-** phased attack flow (recon → discovery → exploitation), real-time context analysis, dynamic strategy selection, adaptive escalation.

---

# 6. Business Impact Metrics & KPIs

## Primary Business Impact: Accelerated Deal Closure

**Core Value Proposition:** Transform policy alignment from a major bottleneck into a competitive advantage

## Key Performance Indicators (KPIs)

### 1. Leading KPI: Policy Agreement Time

- **Metric:** Time from starting work on policy agreement until completion
- **Target:** Significant reduction in policy alignment duration
- **Impact:** This is the primary driver that affects all downstream metrics

### 2. Secondary KPIs (Driven by Policy Agreement Time)

#### A. Customer Onboarding Time

- **Metric:** Time from deal close to successful customer implementation
- **Target:** 20-30% reduction in onboarding duration
- **Driver:** Faster policy agreement enables quicker onboarding start

#### B. Customer Onboarding Success Rate

- **Metric:** Percentage of customers successfully onboarded
- **Target:** Improve success rate by 5%+
- **Driver:** Clear, evidence-backed policies reduce implementation friction


---

# 7. Quick Start Guide

## Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

## Run the Workflow Manager

```bash
python workflow_manager.py --episode <episode_number> --rounds <number_of_rounds>
```

**Example:**
```bash
python workflow_manager.py --episode 1 --rounds 5
```

**Parameters:**
- `episode_number`: Which simulation episode to run (integer)
- `rounds`: Number of interaction rounds to simulate (integer)

## Output Files

The simulation will generate three main outputs:

1. **PDF Report** - Complete tradeoff policy analysis and recommendations
2. **Hacker Simulation Results** - Saved to `hacker_simulation_results_<timestamp>.json`
3. **Policy Analysis Data** - Detailed vulnerability and policy scenario analysis

You can find the PDF report path and analysis summaries in the workflow completion output.


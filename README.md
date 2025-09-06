# Noma Security – Agent Risk Simulator

## Purpose
When Noma Security onboards a new customer, a big challenge is aligning on the **tradeoff policy** — deciding where to prioritize security controls and where to allow product flexibility.  
This tool speeds up that process by simulating the customer's agents, mapping out risky behaviors, and highlighting the key issues that need discussion.

## Architecture
- **Blue Agents (normal workers)**  
  - Instances modeled after the customer's real agent roles (using logs like `agents.csv`, `actions.csv`, `runs.csv`).  
  - Reproduce typical workflows so the simulation is grounded in reality.  

- **Red Agents (stress testers)**  
  - Adversarial personas that push limits — skip approvals, escalate scopes, exfiltrate data, or misuse tools.  
  - Designed to expose vulnerabilities that normal workflows might hide.  

- **Tool Router (traffic controller)**  
  - Central gateway for all actions.  
  - Routes calls to stubs/sandbox, attaches metadata (scope, PII tags, env), and logs every step for reproducibility.  

- **Evaluator (referee)**  
  - Applies Noma's security rules and data lineage checks.  
  - Scores each action/trace for risk severity and novelty.  
  - Produces findings that can be directly used in tradeoff policy discussions.

## Why This Matters
- **Faster onboarding** – automatically surfaces the riskiest actions so Noma doesn't start from a blank slate.  
- **Grounded evidence** – findings are tied to reproducible traces from real customer agent data.  
- **Policy-ready output** – the tool outputs a ranked list of issues, helping frame conversations around "what to block" vs "what to allow."

## MVP Approach
- We want to keep this **fairly simple**: focus on simulating real behaviors, pushing boundaries, and recording clear findings.  
- This is an **MVP**, not a full product yet — enough to prove value and accelerate onboarding conversations.  
- **Tech stack**: Python and FastAPI. No heavy infrastructure or extra frameworks at this stage.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file with your Azure OpenAI configuration:
```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
OPENAI_API_VERSION=2024-02-15-preview
GPT_4O_MINI_DEPLOYMENT=gpt-4o-mini

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
DATA_PATH=./data

# Fallback to standard OpenAI (optional)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Server
```bash
python server.py
```

### 4. Test the System
```bash
# Quick simulation test
python run_simulation.py

# Or use the API
curl http://localhost:8000/health
```

## API Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check
- `GET /agents` - List all available agents
- `POST /simulate` - Run a complete simulation
- `GET /results/{simulation_id}` - Get simulation results
- `GET /findings` - Get security findings
- `GET /action-log` - Get action log from tool router
- `GET /agent-stats/{agent_id}` - Get agent statistics

## Example Usage

### Run Full Simulation
```bash
curl -X POST "http://localhost:8000/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_ids": ["a_wm_shopper", "a_wm_developer"],
    "include_red_team": true,
    "max_actions_per_agent": 5
  }'
```

### Get Results
```bash
curl "http://localhost:8000/results/sim_abc123"
```

## Project Structure
```
noma-assignment/
├── data/                   # Mock customer data
│   ├── agents.csv         # Agent definitions
│   ├── actions.csv        # Historical actions
│   ├── runs.csv          # Agent run logs
│   └── monitoring.csv    # Security scenarios
├── models.py             # Pydantic data models
├── data_loader.py        # Data loading utilities
├── blue_agents.py        # Normal worker agents
├── red_agents.py         # Adversarial stress testers
├── tool_router.py        # Action routing and logging
├── evaluator.py          # Security rule evaluation
├── api.py               # FastAPI endpoints
├── server.py            # Main server entry point
├── run_simulation.py    # Quick test runner
├── config.py            # Configuration settings
└── requirements.txt     # Python dependencies
```

## Red Agent Behaviors
The system tests these risky behaviors:
- **Bigger Exports** - Increased data volume and sensitive data access
- **Scope Escalation** - Access to restricted domains and permissions
- **Approval Skipping** - Bypassing required approval workflows
- **Tool Reordering** - Dangerous action sequences
- **Concurrency Spikes** - High-volume parallel execution
- **Environment Flips** - Switching to production/sensitive environments

## Security Rules
The evaluator checks for:
- PII/PHI sent to external APIs
- Secrets exposed to public repositories
- Confidential data sent to advertising partners
- Financial data to unapproved domains
- Privilege escalation attempts
- Approval workflow bypasses

## Output Format
Results are returned as JSON with:
- Ranked findings by severity and confidence
- Evidence-backed recommendations
- Agent statistics and action logs
- Risk scores and policy suggestions

## End Goal
Enable Noma Security to **streamline customer onboarding** by:  
- Quickly mapping agent vulnerabilities.  
- Producing **ranked, evidence-backed findings**.  
- Helping draft the **tradeoff policy** faster and with more clarity.

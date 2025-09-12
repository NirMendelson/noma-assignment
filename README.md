# Noma Security Home Assignment

## **1) Define the Problem Space**

**Context**

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

I believe this trade-off agreement stage creates significant friction in the onboarding process and makes onboarding much longer than it should be. In enterprise sales, time kills deals: the longer the process drags, the lower the chances of closing. Every week shaved off onboarding translates directly into faster revenue recognition and higher growth.

---

**Primary users**

The Solutions Engineering team at Noma. They are responsible for guiding clients through onboarding, negotiating the trade-off policies, and ensuring a smooth technical rollout.

---

**Core outcomes to improve**

1. **Reduce time-to-onboard-** Faster alignment on policy means more customers can be onboarded per quarter.
2. **Increase deal conversion rate-** Streamlining a friction-heavy process increases the percentage of pilots that convert into paying customers.
3. **Save valuable Solutions Engineering time-** Free SEs from manual back-and-forth so they can support more customers and avoid becoming a bottleneck.

## **2) Design Options & Prioritization**

### **Option 1 - Manual Internal Scenario Team**

Noma can create a dedicated internal team of Solutions Engineers and Product Managers who "put themselves in the client's shoes." For each onboarding, they would manually review the client's environment, brainstorm possible agent scenarios, debate trade-offs internally, and then present the client with a set of options and a recommended policy.

- **Quality of Output**: Medium - depends on human judgment, inconsistent across teams.
- **Complexity to Build**: Low - relies mostly on meetings and manual work.
- **Scalability**: Low - extremely time-consuming, requiring long multi-person meetings and multiple iterations per client. SE team becomes a bottleneck.
- **Time-to-First-Value**: High - can start immediately, but at a heavy time cost.

---

### **Option 2 - AI Tool Using External Data (Speculative)**

An AI system scrapes or collects external information (press releases, job postings, public talks) to speculate which agents a company might be using, what their goals are, and where risks could exist. It then generates trade-off policy recommendations based on those assumptions.

- **Quality of Output**: Low-Medium - speculative, often inaccurate or irrelevant.
- **Complexity to Build**: Medium-High - requires scraping pipelines, data processing, and scenario simulation logic.
- **Scalability**: Medium - once built, could be applied across many accounts, but usefulness is limited by poor accuracy.
- **Time-to-First-Value**: Medium - results appear quickly, but quality is questionable.

---

### **Option 3 - AI Tool Using Monitoring Data (Simulation-Driven)**

After the client connects Noma in **monitor-only mode**, the system uses real agent data (which agents exist, what their roles and tools are, and which risks have already surfaced). It then simulates multiple scenarios where vulnerabilities might appear, analyzes fallout if actions were blocked vs allowed, and generates trade-off policy recommendations with options (Block / Alert / Allow). The result is a structured draft of the agreement for review and signoff.

- **Quality of Output**: High - grounded in real client environment, evidence-based.
- **Complexity to Build**: Medium-High - similar to Option 2, requires scenario simulation and data processing, but with accurate inputs.
- **Scalability**: High - once built, can be reused across many clients with minimal incremental cost.
- **Time-to-First-Value**: Medium - requires a few weeks after monitor-only access, but delivers highly credible results.


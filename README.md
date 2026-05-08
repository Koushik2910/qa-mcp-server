# QA MCP Server 🤖

> An AI Agent that connects GitHub Issues → generates test plans → creates Jira tickets automatically

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![MCP](https://img.shields.io/badge/MCP-1.27-purple?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-Llama3-orange?style=flat-square)
![GitHub](https://img.shields.io/badge/GitHub-API-black?style=flat-square&logo=github)
![Jira](https://img.shields.io/badge/Jira-API-blue?style=flat-square&logo=jira)

---

## What it does

One command in Claude Code → the agent automatically:

1. Fetches open issues from your GitHub repository
2. Sends each issue to Groq AI → generates a detailed QA test plan
3. Creates a Jira ticket with the AI-generated test plan in the description
4. Links the Jira ticket back to the original GitHub issue

No manual copy-paste. No context switching. Fully automated QA workflow.

---

## Demo

**Input (typed in Claude Code):**
```
process all open github issues and create jira tickets
```

**What happens automatically:**
```
✅ CRED1-99  → [GitHub #1] Login page crashes when password field is empty
✅ CRED1-100 → [GitHub #2] Search results not filtered by date
✅ CRED1-101 → [GitHub #3] Payment fails for international cards
```

Each Jira ticket contains:
- Link to original GitHub issue
- AI-generated test scenarios (3+ per issue)
- Edge cases and boundary conditions
- Test data recommendations

---

## What is MCP?

Model Context Protocol (MCP) is a standard that lets AI models like Claude connect to external tools and services. Instead of just answering questions, Claude can actually **take actions** — fetch data, create tickets, call APIs — through MCP servers.

This project is a custom MCP server that gives Claude the ability to interact with GitHub and Jira as a QA engineer would.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Protocol | Model Context Protocol (MCP) |
| AI Model | Llama 3.3 70B via Groq API (free) |
| Issue Tracking | GitHub REST API |
| Project Management | Jira REST API v3 |
| Runtime | Python asyncio |
| Interface | Claude Code (terminal) |

---

## Available Tools

The MCP server exposes 4 tools to Claude:

| Tool | What it does |
|---|---|
| `get_github_issues` | Fetch all open issues from the configured GitHub repo |
| `generate_test_plan` | Generate AI test plan for a specific issue number |
| `create_jira_ticket` | Create Jira ticket with AI test plan for a specific issue |
| `process_all_issues` | Process all open issues and create Jira tickets in one go |

---

## Project Structure

```
qa-mcp-server/
├── server.py           # MCP server — all tools, GitHub API, Jira API, Groq AI
├── test_server.py      # Quick test to verify all 3 connections work
├── requirements.txt    # Python dependencies
├── .env                # API keys (never committed)
└── .gitignore
```

---

## How to Run Locally

### Prerequisites
- Python 3.9+
- Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- Free accounts on: Groq, GitHub, Jira (Atlassian)

### Step 1: Clone and install

```bash
git clone https://github.com/Koushik2910/qa-mcp-server.git
cd qa-mcp-server

python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### Step 2: Configure .env

```bash
# Create .env file with your credentials
GITHUB_TOKEN=ghp_your_github_token
GITHUB_REPO=your_username/your_repo
JIRA_URL=https://your_site.atlassian.net
JIRA_EMAIL=your_email@gmail.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=YOUR_PROJECT_KEY
GROQ_API_KEY=your_groq_api_key
```

**Get free API keys:**
- GitHub token → github.com/settings/tokens → classic token → repo scope
- Jira token → id.atlassian.com/manage-profile/security/api-tokens
- Groq key → console.groq.com (free, no card needed)

### Step 3: Test connections

```bash
python test_server.py
```

Expected output:
```
1. GitHub OK — Found X open issues
2. Jira OK — Project: Your Project (KEY)
3. Groq OK — Response: OK
```

### Step 4: Register MCP server with Claude Code

```bash
claude mcp add qa-mcp-server \
  "path/to/venv/Scripts/python.exe" \
  "path/to/qa-mcp-server/server.py"
```

Then update `~/.claude.json` to add environment variables in the `env` section for `qa-mcp-server`.

### Step 5: Use it in Claude Code

```bash
cd qa-mcp-server
claude
```

Then type natural language commands:
```
get all open github issues
generate test plan for issue #1
create jira ticket for issue #2
process all open issues and create jira tickets
```

---

## How It Works

```
Claude Code (natural language)
        ↓
MCP Protocol (tool call)
        ↓
server.py receives the tool call
        ↓
GitHub API → fetch issue title + description
        ↓
Groq API (Llama 3.3 70B) → generate test plan
        ↓
Jira REST API → create ticket with test plan
        ↓
Claude Code shows result
```

---

## Why This Matters

Traditional QA workflow:
1. Developer creates GitHub issue
2. QA engineer reads issue
3. QA engineer manually writes test plan
4. QA engineer creates Jira ticket
5. QA engineer copies test plan to Jira

**With this MCP server:**
1. Developer creates GitHub issue
2. One command → everything else is automated

Saves 15-20 minutes per issue. At 10 issues per sprint, that's 2-3 hours saved per sprint.

---

## What's Next

- [ ] Add webhook support — auto-trigger when GitHub issue is created
- [ ] Two-way sync — update GitHub issue when Jira ticket status changes
- [ ] Priority mapping — map GitHub labels to Jira priority levels
- [ ] Slack notification — notify QA channel when ticket is created
- [ ] Test plan quality scoring — rate generated test plans

---

## Connect

**Koushik** — Senior QA Engineer → AI Quality Engineer

- GitHub: [@Koushik2910](https://github.com/Koushik2910)
- Project 1: [AI Test Case Generator](https://github.com/Koushik2910/ai-test-generator)

---

*Built with MCP + Groq + GitHub API + Jira API · Free to use and extend*

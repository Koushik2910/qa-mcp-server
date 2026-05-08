import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

load_dotenv()

# Config from .env
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
server = Server("qa-mcp-server")

# ── Tool 1: List GitHub Issues ──────────────────────────
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_github_issues",
            description="Fetch open issues from the GitHub repo",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="generate_test_plan",
            description="Generate a QA test plan for a GitHub issue using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_number": {
                        "type": "integer",
                        "description": "GitHub issue number"
                    }
                },
                "required": ["issue_number"]
            }
        ),
        types.Tool(
            name="create_jira_ticket",
            description="Create a Jira ticket with AI-generated test plan from a GitHub issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_number": {
                        "type": "integer",
                        "description": "GitHub issue number to process"
                    }
                },
                "required": ["issue_number"]
            }
        ),
        types.Tool(
            name="process_all_issues",
            description="Process all open GitHub issues and create Jira tickets for each",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

# ── Tool implementations ─────────────────────────────────
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "get_github_issues":
        result = fetch_github_issues()
        return [types.TextContent(type="text", text=result)]

    elif name == "generate_test_plan":
        issue_number = arguments["issue_number"]
        issue = fetch_single_issue(issue_number)
        if "error" in issue:
            return [types.TextContent(type="text", text=issue["error"])]
        test_plan = generate_test_plan_ai(issue)
        return [types.TextContent(type="text", text=test_plan)]

    elif name == "create_jira_ticket":
        issue_number = arguments["issue_number"]
        issue = fetch_single_issue(issue_number)
        if "error" in issue:
            return [types.TextContent(type="text", text=issue["error"])]
        test_plan = generate_test_plan_ai(issue)
        result = create_jira(issue, test_plan)
        return [types.TextContent(type="text", text=result)]

    elif name == "process_all_issues":
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return [types.TextContent(type="text", text=f"GitHub error: {response.text}")]
        issues = response.json()
        results = []
        for issue in issues:
            test_plan = generate_test_plan_ai(issue)
            result = create_jira(issue, test_plan)
            results.append(f"Issue #{issue['number']}: {result}")
        return [types.TextContent(type="text", text="\n".join(results))]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Helper functions ─────────────────────────────────────
def fetch_github_issues() -> str:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error fetching issues: {response.text}"
    issues = response.json()
    if not issues:
        return "No open issues found."
    result = f"Found {len(issues)} open issues in {GITHUB_REPO}:\n\n"
    for issue in issues:
        result += f"#{issue['number']} - {issue['title']}\n"
        result += f"  URL: {issue['html_url']}\n\n"
    return result


def fetch_single_issue(issue_number: int) -> dict:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Issue #{issue_number} not found"}
    return response.json()


def generate_test_plan_ai(issue: dict) -> str:
    title = issue.get("title", "")
    body = issue.get("body", "No description provided")
    prompt = f"""You are a Senior QA Engineer. Generate a detailed test plan for this bug/feature.

Issue Title: {title}
Issue Description: {body}

Generate a test plan with:
1. Summary (1 line)
2. Test Scenarios (at least 3)
3. Test Cases for each scenario (steps + expected result)
4. Edge Cases to consider
5. Test Data needed

Keep it concise but complete. Format it clearly."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )
    return response.choices[0].message.content


def create_jira(issue: dict, test_plan: str) -> str:
    title = issue.get("title", "")
    issue_number = issue.get("number", "")
    github_url = issue.get("html_url", "")

    description = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": f"GitHub Issue: {github_url}",
                    }
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "AI Generated Test Plan:",
                        "marks": [{"type": "strong"}]
                    }
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": test_plan
                    }
                ]
            }
        ]
    }

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"[GitHub #{issue_number}] {title}",
            "description": description,
            "issuetype": {"name": "Story"}
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/3/issue",
        json=payload,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        data = response.json()
        ticket_key = data.get("key", "")
        return f"✅ Jira ticket {ticket_key} created for GitHub issue #{issue_number} - {title}"
    else:
        return f"❌ Failed to create Jira ticket: {response.text}"


# ── Run server ───────────────────────────────────────────
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
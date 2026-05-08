import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("Testing connections...\n")

# Test 1: GitHub
print("1. Testing GitHub connection...")
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open"
response = requests.get(url, headers=headers)
if response.status_code == 200:
    issues = response.json()
    print(f"   GitHub OK — Found {len(issues)} open issues")
    for issue in issues:
        print(f"   #{issue['number']} - {issue['title']}")
else:
    print(f"   GitHub FAILED — {response.status_code}: {response.text}")

print()

# Test 2: Jira
print("2. Testing Jira connection...")
jira_response = requests.get(
    f"{JIRA_URL}/rest/api/3/project/{JIRA_PROJECT_KEY}",
    auth=(JIRA_EMAIL, JIRA_API_TOKEN),
    headers={"Content-Type": "application/json"}
)
if jira_response.status_code == 200:
    project = jira_response.json()
    print(f"   Jira OK — Project: {project.get('name')} ({JIRA_PROJECT_KEY})")
else:
    print(f"   Jira FAILED — {jira_response.status_code}: {jira_response.text}")

print()

# Test 3: Groq
print("3. Testing Groq AI connection...")
groq_client = Groq(api_key=GROQ_API_KEY)
groq_response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say OK in one word"}],
    max_tokens=10
)
print(f"   Groq OK — Response: {groq_response.choices[0].message.content}")

print("\nAll tests done!")
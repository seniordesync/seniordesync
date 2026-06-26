import os
import json
import urllib.request
import urllib.error

USERNAME = "seniordesync"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner"
README_PATH = "README.md"

# Assign specific emojis to known projects, fallback to a default one
EMOJI_MAP = {
    "OctoClash": "🐙",
    "Linux-Graph": "🐧",
    "seniordesync": "👤"
}
DEFAULT_EMOJI = "📦"

def get_repos():
    req = urllib.request.Request(API_URL)
    # Using GITHUB_TOKEN if available to increase rate limit
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching repos: {e}")
        return []

def update_readme():
    repos = get_repos()
    
    # Filter out forks and the profile repo itself
    filtered_repos = [r for r in repos if not r.get("fork", False) and r["name"] != USERNAME]
    
    # Sort: First by has_pages (True before False), then by stargazers_count (descending)
    sorted_repos = sorted(filtered_repos, key=lambda x: (x.get("has_pages", False), x.get("stargazers_count", 0)), reverse=True)
    
    # Generate Markdown table
    table_lines = [
        "| Project | Description |",
        "|---|---|"
    ]
    
    for repo in sorted_repos:
        name = repo["name"]
        url = repo["html_url"]
        desc = repo.get("description") or "No description provided."
        has_pages = repo.get("has_pages", False)
        
        emoji = EMOJI_MAP.get(name, DEFAULT_EMOJI)
        
        # Build the name column with an optional play icon for live apps
        if has_pages:
            pages_url = f"https://{USERNAME}.github.io/{name}"
            name_cell = f"[▶️]({pages_url}) {emoji} **[{name}]({url})**"
        else:
            name_cell = f"{emoji} **[{name}]({url})**"
            
        row = f"| {name_cell} | {desc} |"
        table_lines.append(row)
        
    table_content = "\n".join(table_lines)
    
    # Read README
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace content between markers
    start_marker = "<!-- PROJECTS_START -->"
    end_marker = "<!-- PROJECTS_END -->"
    
    if start_marker in content and end_marker in content:
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]
        new_content = f"{before}{start_marker}\n{table_content}\n{end_marker}{after}"
        
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README updated successfully with dynamic projects!")
    else:
        print("Error: Markers not found in README.md")

if __name__ == "__main__":
    update_readme()

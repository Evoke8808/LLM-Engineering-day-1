import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from IPython.display import Markdown, display

# 1. Connect to Ollama on your Mac instead of OpenAI's servers
MODEL = "llama3.2"
ollama = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# 2. Scraper: download a page and keep its title and visible text
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def fetch_website_contents(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]

# 3. Prompts: the system prompt sets the role, the user prompt carries the content
system_prompt = """
You are a proffesional website summarizer assistant. you should help the user by summarising the website proffesionally and in a easy understandable way
. if th website contains any articles or important news add it  to the summary
"""

user_prompt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.

"""

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website},
    ]

# 4. Glue it together
def summarize(url):
    website = fetch_website_contents(url)
    response = ollama.chat.completions.create(
        model=MODEL,
        messages=messages_for(website),
    )
    return response.choices[0].message.content
url = input("Enter a website URL: ")
print(summarize(url))
import requests
from bs4 import BeautifulSoup

# ✅ Wikipedia (primary source)
def wiki_search(query: str):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")

    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None

        data = res.json()

        if "extract" not in data:
            return None

        return f"""
[Wikipedia]
Title: {data.get("title", "")}
Content: {data.get("extract", "")}
Source: {data.get("content_urls", {}).get("desktop", {}).get("page", "")}
"""
    except:
        return None


# ✅ DuckDuckGo search (fallback)
def duckduckgo_search(query: str):
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.post(url, data={"q": query}, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        results = []

        for r in soup.select(".result")[:3]:
            link = r.select_one("a")["href"]
            snippet = r.select_one(".result__snippet")

            results.append({
                "link": link,
                "snippet": snippet.text if snippet else ""
            })

        return results
    except:
        return []


# ✅ Extract content from web page
def fetch_page(url: str):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        paragraphs = [p.get_text() for p in soup.find_all("p")]
        text = " ".join(paragraphs)

        return text[:1500]
    except:
        return ""


# ✅ Final context builder
def build_context(query: str):
    context_parts = []

    # 1. Wikipedia
    wiki = wiki_search(query)
    if wiki:
        context_parts.append(wiki)

    # 2. DuckDuckGo fallback
    ddg_results = duckduckgo_search(query)

    for r in ddg_results:
        page_text = fetch_page(r["link"])

        if page_text:
            context_parts.append(f"""
[Web Source]
Snippet: {r['snippet']}
Content: {page_text}
Source: {r['link']}
""")

    return "\n\n---\n\n".join(context_parts)
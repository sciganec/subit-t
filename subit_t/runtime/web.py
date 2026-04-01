"""Web search and page-fetch helpers for CLI workflows."""

from __future__ import annotations

import html
import re
from urllib.parse import parse_qs, unquote, urlparse

import requests


AUTO_WEB_PATTERNS = [
    r"\bweather\b",
    r"\bforecast\b",
    r"\btemperature\b",
    r"\bnews\b",
    r"\blatest\b",
    r"\bcurrent\b",
    r"\btoday\b",
    r"\bright now\b",
    r"\brecent\b",
    r"\bprice\b",
    r"\bstock\b",
    r"\bbitcoin\b",
    r"\bcrypto\b",
    r"\bexchange rate\b",
    r"\bversion\b",
    r"\brelease\b",
    r"\bwho is\b",
    r"\bwhen is\b",
    r"\bwhat happened\b",
]


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def extract_ddg_url(raw_url: str) -> str:
    if raw_url.startswith("//"):
        return "https:" + raw_url
    if raw_url.startswith("/l/?"):
        query = parse_qs(urlparse(raw_url).query)
        uddg = query.get("uddg", [raw_url])[0]
        return unquote(uddg)
    return raw_url


def duckduckgo_search(query: str, limit: int = 5, timeout: int = 20) -> list[dict]:
    response = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers={"User-Agent": "subit-t/0.3.0"},
        timeout=timeout,
    )
    response.raise_for_status()
    html_text = response.text

    pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?'
        r'(?:(?:<a[^>]*class="result__snippet"[^>]*>|<div[^>]*class="result__snippet"[^>]*>)(?P<snippet>.*?)</(?:a|div)>)?',
        re.DOTALL,
    )

    results = []
    for match in pattern.finditer(html_text):
        title = html.unescape(strip_tags(match.group("title"))).strip()
        href = extract_ddg_url(html.unescape(match.group("href")).strip())
        snippet = html.unescape(strip_tags(match.group("snippet") or "")).strip()
        if not title or not href:
            continue
        results.append({"title": title, "url": href, "snippet": snippet})
        if len(results) >= limit:
            break
    return results


def format_web_context(results: list[dict]) -> str:
    if not results:
        return ""
    lines = ["Web search results:"]
    for index, item in enumerate(results, start=1):
        lines.append(f"{index}. {item['title']}")
        lines.append(f"   URL: {item['url']}")
        if item["snippet"]:
            lines.append(f"   Snippet: {item['snippet']}")
    return "\n".join(lines)


def extract_page_text(html_text: str, max_chars: int = 1200) -> str:
    match = re.search(r"<body[^>]*>(.*?)</body>", html_text, re.DOTALL | re.IGNORECASE)
    body = match.group(1) if match else html_text
    body = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", body)
    body = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", body)
    text = html.unescape(strip_tags(body))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def fetch_page_summaries(results: list[dict], timeout: int = 15, max_pages: int = 3) -> list[dict]:
    pages = []
    headers = {"User-Agent": "subit-t/0.3.0"}
    for item in results[:max_pages]:
        try:
            response = requests.get(item["url"], headers=headers, timeout=timeout)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                pages.append(
                    {
                        "title": item["title"],
                        "url": item["url"],
                        "content": f"Skipped non-HTML content ({content_type}).",
                    }
                )
                continue
            pages.append(
                {
                    "title": item["title"],
                    "url": item["url"],
                    "content": extract_page_text(response.text),
                }
            )
        except Exception as exc:
            pages.append(
                {
                    "title": item["title"],
                    "url": item["url"],
                    "content": f"Fetch failed: {exc}",
                }
            )
    return pages


def format_page_context(pages: list[dict]) -> str:
    if not pages:
        return ""
    lines = ["Fetched page excerpts:"]
    for index, item in enumerate(pages, start=1):
        lines.append(f"{index}. {item['title']}")
        lines.append(f"   URL: {item['url']}")
        if item["content"]:
            lines.append(f"   Content: {item['content']}")
    return "\n".join(lines)


def needs_web_search(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in AUTO_WEB_PATTERNS)


def prepare_external_context(
    *,
    text: str,
    use_web: bool,
    web_k: int,
    web_timeout: int,
    fetch_pages: int,
    fetch_timeout: int,
) -> tuple[list[dict], list[dict], str]:
    web_results = []
    page_summaries = []

    if use_web:
        web_results = duckduckgo_search(text, limit=web_k, timeout=web_timeout)

    if web_results and fetch_pages:
        page_summaries = fetch_page_summaries(
            web_results,
            timeout=fetch_timeout,
            max_pages=fetch_pages,
        )

    extra_parts = [format_web_context(web_results), format_page_context(page_summaries)]
    extra = "\n\n".join(part for part in extra_parts if part)
    return web_results, page_summaries, extra


def build_user_text(text: str, web_results: list[dict], page_summaries: list[dict]) -> str:
    user_text = text
    if web_results:
        user_text = (
            f"{text}\n\n"
            "Use the supplied web results when they are relevant. "
            "If they conflict, prefer the cited URLs over prior assumptions."
        )
    if page_summaries:
        user_text += (
            "\nUse fetched page excerpts as higher-confidence evidence than search-result titles alone. "
            "Only state facts that are supported by the fetched content."
        )
    return user_text

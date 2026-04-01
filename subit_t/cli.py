"""
SUBIT-T CLI.

Commands:
    subit profile "text"   - encode text, show state and operator
    subit route "text"     - full routing pipeline
    subit canon            - show all 64 states
    subit state NAME       - show details for one state
    subit chain NAME op... - apply an operator chain
"""

import argparse
import html
import json
import re
import sys
from urllib.parse import parse_qs, urlparse, unquote

import requests


def cmd_profile(args):
    from subit_t import encode
    from subit_t.canon import STATE_TYPE, STATE_WEIGHT

    result = encode(args.text)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return

    print("\n" + "-" * 50)
    print("  SUBIT-T PROFILE")
    print("-" * 50)
    print(f"  Input: {args.text[:55]}{'...' if len(args.text) > 55 else ''}")
    print("-" * 50 + "\n")

    state = result.current_state
    print(f"  Current state:  {state.name:<14}  [{STATE_TYPE.get(state.name, '?')}  w={STATE_WEIGHT.get(state.name, 0):.2f}]")
    print(f"    WHO:  {state.who:<10}  orientation of attention")
    print(f"    WHAT: {state.what:<10}  operation on information")
    print(f"    WHEN: {state.when:<10}  phase of cognitive cycle")

    print(f"\n  Operator:  {result.operator.symbol} {result.operator.value}")
    print(f"    {result.operator.description}")
    print(f"    Confidence: {result.op_confidence:.0%}")

    target = result.target_state
    print(f"\n  Next state:     {target.name:<14}  [{STATE_TYPE.get(target.name, '?')}  w={STATE_WEIGHT.get(target.name, 0):.2f}]")

    if not args.brief:
        print("\n  Top states:")
        for name, prob in list(result.state_distribution.items())[:6]:
            bar = "#" * int(prob * 40)
            stype = STATE_TYPE.get(name, "?")
            print(f"    {name:<14} {stype:<10} {prob:.3f}  {bar}")

    print()


def cmd_route(args):
    from subit_t import encode
    from subit_t.injector import build_prompt

    result = encode(args.text)
    transition = result.current_state.apply(result.operator)

    if args.json:
        out = {
            "current": result.current_state.to_dict(),
            "operator": result.operator.value,
            "next": transition.result.to_dict(),
            "prompt": build_prompt(transition.result, result.operator, args.text),
        }
        print(json.dumps(out, indent=2))
        return

    print(f"\n  {result.current_state.name}  {result.operator.symbol}({result.operator.value})  ->  {transition.result.name}\n")

    if args.prompt:
        print(build_prompt(transition.result, result.operator, args.text))
    print()


def cmd_canon(args):
    from subit_t.canon import CANON, STATE_TYPE, STATE_WEIGHT

    who_filter = args.who.upper() if args.who else None
    what_filter = args.what.upper() if args.what else None
    when_filter = args.when.upper() if args.when else None
    type_filter = args.type.lower() if args.type else None

    print(f"\n  {'NAME':<14} {'WHO':<6} {'WHAT':<10} {'WHEN':<10} {'TYPE':<10} {'W'}")
    print(f"  {'-' * 14} {'-' * 6} {'-' * 10} {'-' * 10} {'-' * 10} {'-' * 4}")

    count = 0
    for bits in sorted(CANON.keys()):
        who, what, when, name = CANON[bits]
        stype = STATE_TYPE.get(name, "?")
        weight = STATE_WEIGHT.get(name, 0)

        if who_filter and who != who_filter:
            continue
        if what_filter and what != what_filter:
            continue
        if when_filter and when != when_filter:
            continue
        if type_filter and stype != type_filter:
            continue

        print(f"  {name:<14} {who:<6} {what:<10} {when:<10} {stype:<10} {weight:.2f}")
        count += 1

    print(f"\n  {count} states\n")


def cmd_state(args):
    from subit_t import State
    from subit_t.injector import _ARCHETYPE_ROLE
    from subit_t.core import Op

    try:
        state = State.from_name(args.name.upper())
    except KeyError:
        print(f"Unknown state: {args.name}")
        sys.exit(1)

    print("\n" + "-" * 50)
    print(f"  {state.name}")
    print("-" * 50)
    print(f"  WHO:    {state.who:<12} orientation of attention")
    print(f"  WHAT:   {state.what:<12} operation on information")
    print(f"  WHEN:   {state.when:<12} phase of cognitive cycle")
    print(f"  Bits:   {state.bits:06b} ({state.bits})")
    print(f"  Type:   {state.state_type}")
    print(f"  Weight: {state.state_weight:.2f}")
    print(f"\n  Role: {_ARCHETYPE_ROLE.get(state.name, 'No description')}")

    print("\n  Transitions:")
    for op in Op:
        transition = state.apply(op)
        print(f"    {op.symbol} {op.value:<12} -> {transition.result.name}")
    print()


def cmd_chain(args):
    from subit_t import State
    from subit_t.core import Op

    try:
        current = State.from_name(args.start.upper())
    except KeyError:
        print(f"Unknown state: {args.start}")
        sys.exit(1)

    op_map = {
        "WHO": Op.WHO_SHIFT,
        "WHAT": Op.WHAT_SHIFT,
        "WHEN": Op.WHEN_SHIFT,
        "INV": Op.INV,
        "W": Op.WHO_SHIFT,
        "T": Op.WHAT_SHIFT,
        "N": Op.WHEN_SHIFT,
        "I": Op.INV,
    }

    print(f"\n  {current.name}")
    for op_name in args.ops:
        op = op_map.get(op_name.upper())
        if not op:
            print(f"  Unknown operator: {op_name}. Use WHO/WHAT/WHEN/INV or W/T/N/I")
            sys.exit(1)
        transition = current.apply(op)
        print(f"    {op.symbol}({op.value}) -> {transition.result.name}  [{transition.result.state_type}]")
        current = transition.result
    print()


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _extract_ddg_url(raw_url: str) -> str:
    if raw_url.startswith("//"):
        return "https:" + raw_url
    if raw_url.startswith("/l/?"):
        query = parse_qs(urlparse(raw_url).query)
        uddg = query.get("uddg", [raw_url])[0]
        return unquote(uddg)
    return raw_url


def _duckduckgo_search(query: str, limit: int = 5, timeout: int = 20) -> list[dict]:
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
        title = html.unescape(_strip_tags(match.group("title"))).strip()
        href = _extract_ddg_url(html.unescape(match.group("href")).strip())
        snippet = html.unescape(_strip_tags(match.group("snippet") or "")).strip()
        if not title or not href:
            continue
        results.append({"title": title, "url": href, "snippet": snippet})
        if len(results) >= limit:
            break
    return results


def _format_web_context(results: list[dict]) -> str:
    if not results:
        return ""
    lines = ["Web search results:"]
    for index, item in enumerate(results, start=1):
        lines.append(f"{index}. {item['title']}")
        lines.append(f"   URL: {item['url']}")
        if item["snippet"]:
            lines.append(f"   Snippet: {item['snippet']}")
    return "\n".join(lines)


def _extract_page_text(html_text: str, max_chars: int = 1200) -> str:
    match = re.search(r"<body[^>]*>(.*?)</body>", html_text, re.DOTALL | re.IGNORECASE)
    body = match.group(1) if match else html_text
    body = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", body)
    body = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", body)
    text = html.unescape(_strip_tags(body))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def _fetch_page_summaries(results: list[dict], timeout: int = 15, max_pages: int = 3) -> list[dict]:
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
                    "content": _extract_page_text(response.text),
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


def _format_page_context(pages: list[dict]) -> str:
    if not pages:
        return ""
    lines = ["Fetched page excerpts:"]
    for index, item in enumerate(pages, start=1):
        lines.append(f"{index}. {item['title']}")
        lines.append(f"   URL: {item['url']}")
        if item["content"]:
            lines.append(f"   Content: {item['content']}")
    return "\n".join(lines)


def cmd_ollama(args):
    from subit_t import encode
    from subit_t.injector import build_prompt

    text = args.text
    result = encode(text)
    web_results = []
    page_summaries = []

    if args.web:
        try:
            web_results = _duckduckgo_search(text, limit=args.web_k, timeout=args.web_timeout)
        except Exception as exc:
            print(f"Web search failed: {exc}")
            sys.exit(1)

    if web_results and args.fetch_pages:
        page_summaries = _fetch_page_summaries(
            web_results,
            timeout=args.fetch_timeout,
            max_pages=args.fetch_pages,
        )

    extra_parts = [_format_web_context(web_results), _format_page_context(page_summaries)]
    extra = "\n\n".join(part for part in extra_parts if part)
    prompt = build_prompt(result.target_state, result.operator, text, extra=extra)

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

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": args.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_text},
                ],
            },
            timeout=args.timeout,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("Ollama is not running on http://localhost:11434")
        sys.exit(1)
    except Exception as exc:
        print(f"Ollama request failed: {exc}")
        sys.exit(1)

    content = response.json()["message"]["content"]

    if args.json:
        print(
            json.dumps(
                {
                    "current_state": result.current_state.to_dict(),
                    "operator": result.operator.value,
                    "target_state": result.target_state.to_dict(),
                    "web_results": web_results,
                    "page_summaries": page_summaries,
                    "prompt": prompt,
                    "response": content,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

    print(f"\n  {result.current_state.name}  {result.operator.symbol}({result.operator.value})  ->  {result.target_state.name}\n")
    if web_results:
        print("  Web results:")
        for item in web_results:
            print(f"  - {item['title']}")
            print(f"    {item['url']}")
        print()
    if page_summaries:
        print("  Fetched pages:")
        for item in page_summaries:
            print(f"  - {item['title']}")
            print(f"    {item['url']}")
        print()
    print(content)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="subit",
        description="SUBIT-T - cyclic archetypal routing for multi-agent AI systems",
    )
    sub = parser.add_subparsers(dest="command")

    profile = sub.add_parser("profile", help="Encode text to a cognitive profile")
    profile.add_argument("text")
    profile.add_argument("--json", action="store_true", help="Output as JSON")
    profile.add_argument("--brief", action="store_true", help="Skip state distribution")

    route = sub.add_parser("route", help="Full routing pipeline")
    route.add_argument("text")
    route.add_argument("--json", action="store_true")
    route.add_argument("--prompt", action="store_true", help="Print system prompt")

    canon = sub.add_parser("canon", help="Show all 64 states")
    canon.add_argument("--who", help="Filter by WHO")
    canon.add_argument("--what", help="Filter by WHAT")
    canon.add_argument("--when", help="Filter by WHEN")
    canon.add_argument("--type", help="Filter by state type")

    state = sub.add_parser("state", help="Show details for one state")
    state.add_argument("name", help="State name, for example SCAN")

    chain = sub.add_parser("chain", help="Apply operator chain")
    chain.add_argument("start", help="Starting state name")
    chain.add_argument("ops", nargs="+", help="Operators: WHO WHAT WHEN INV (or W T N I)")

    ollama = sub.add_parser("ollama", help="Route text and send it to a local Ollama model")
    ollama.add_argument("text", help="Input text to route")
    ollama.add_argument("--model", default="llama3.2", help="Ollama model name")
    ollama.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    ollama.add_argument("--web", action="store_true", help="Run a web search first and include results in the prompt")
    ollama.add_argument("--web-k", type=int, default=5, help="Number of web results to include")
    ollama.add_argument("--web-timeout", type=int, default=20, help="Timeout for the web search request in seconds")
    ollama.add_argument("--fetch-pages", type=int, default=0, help="Fetch the top N web result pages and include text excerpts")
    ollama.add_argument("--fetch-timeout", type=int, default=15, help="Timeout for fetching each page in seconds")
    ollama.add_argument("--json", action="store_true", help="Output routing and model response as JSON")

    args = parser.parse_args()

    if args.command == "profile":
        cmd_profile(args)
    elif args.command == "route":
        cmd_route(args)
    elif args.command == "canon":
        cmd_canon(args)
    elif args.command == "state":
        cmd_state(args)
    elif args.command == "chain":
        cmd_chain(args)
    elif args.command == "ollama":
        cmd_ollama(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

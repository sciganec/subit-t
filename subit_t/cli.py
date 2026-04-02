"""
SUBIT-T CLI.

Commands:
    subit profile "text"   - encode text, show state and operator
    subit route "text"     - full routing pipeline
    subit canon            - show all 64 states
    subit state NAME       - show details for one state
    subit chain NAME op... - apply an operator chain
"""

from __future__ import annotations

import argparse
import json
import sys

from .runtime.chat import run_chat_session
from .runtime.ollama import call_ollama
from .runtime.web import build_user_text, needs_web_search, prepare_external_context
from .prompts import build_assistant_extra, list_assistants


def cmd_profile(args):
    from subit_t import encode
    from subit_t.canon import STATE_TYPE, STATE_WEIGHT

    result = encode(
        args.text,
        model_assisted=args.model_assisted_encoder,
        model=args.encoder_model,
        timeout=args.encoder_timeout,
    )

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

    result = encode(
        args.text,
        model_assisted=args.model_assisted_encoder,
        model=args.encoder_model,
        timeout=args.encoder_timeout,
    )
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


def cmd_ollama(args):
    from subit_t import encode
    from subit_t.injector import build_prompt

    text = args.text
    result = encode(
        text,
        model_assisted=args.model_assisted_encoder,
        model=args.encoder_model,
        timeout=args.encoder_timeout,
    )
    use_web = args.web or (args.auto_web and needs_web_search(text))
    auto_web_triggered = bool(args.auto_web and not args.web and use_web)

    try:
        web_results, page_summaries, extra = prepare_external_context(
            text=text,
            use_web=use_web,
            web_k=args.web_k,
            web_timeout=args.web_timeout,
            fetch_pages=args.fetch_pages if use_web else 0,
            fetch_timeout=args.fetch_timeout,
        )
    except Exception as exc:
        print(f"Web search failed: {exc}")
        print("Continuing without external context.")
        web_results, page_summaries, extra = [], [], ""
        use_web = False
        auto_web_triggered = False

    assistant_extra = build_assistant_extra(args.assistant)
    prompt_extra = "\n\n".join(part for part in [assistant_extra, extra] if part)
    prompt = build_prompt(result.target_state, result.operator, text, extra=prompt_extra)
    user_text = build_user_text(text, web_results, page_summaries)

    try:
        content = call_ollama(
            model=args.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text},
            ],
            timeout=args.timeout,
        )
    except RuntimeError as exc:
        print(exc)
        sys.exit(1)

    if args.json:
        print(
            json.dumps(
                {
                    "current_state": result.current_state.to_dict(),
                    "operator": result.operator.value,
                    "target_state": result.target_state.to_dict(),
                    "used_web": use_web,
                    "auto_web_triggered": auto_web_triggered,
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
    if auto_web_triggered:
        print("  Auto-web: enabled for this query\n")
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


def cmd_chat(args):
    run_chat_session(
        model=args.model,
        timeout=args.timeout,
        history_turns=args.history_turns,
        web=args.web,
        auto_web=args.auto_web,
        web_k=args.web_k,
        web_timeout=args.web_timeout,
        fetch_pages=args.fetch_pages,
        fetch_timeout=args.fetch_timeout,
        show_sources=args.show_sources,
        assistant=args.assistant,
        model_assisted_encoder=args.model_assisted_encoder,
        encoder_model=args.encoder_model,
        encoder_timeout=args.encoder_timeout,
    )


def main():
    assistant_names = ", ".join(list_assistants())
    parser = argparse.ArgumentParser(
        prog="subit",
        description="SUBIT-T - cyclic archetypal routing for multi-agent AI systems",
    )
    sub = parser.add_subparsers(dest="command")

    profile = sub.add_parser("profile", help="Encode text to a cognitive profile")
    profile.add_argument("text")
    profile.add_argument("--json", action="store_true", help="Output as JSON")
    profile.add_argument("--brief", action="store_true", help="Skip state distribution")
    profile.add_argument("--model-assisted-encoder", action="store_true", help="Use the optional model-assisted encoder layer")
    profile.add_argument("--encoder-model", default="llama3.2", help="Ollama model for model-assisted encoding")
    profile.add_argument("--encoder-timeout", type=int, default=20, help="Timeout for model-assisted encoding")

    route = sub.add_parser("route", help="Full routing pipeline")
    route.add_argument("text")
    route.add_argument("--json", action="store_true")
    route.add_argument("--prompt", action="store_true", help="Print system prompt")
    route.add_argument("--model-assisted-encoder", action="store_true", help="Use the optional model-assisted encoder layer")
    route.add_argument("--encoder-model", default="llama3.2", help="Ollama model for model-assisted encoding")
    route.add_argument("--encoder-timeout", type=int, default=20, help="Timeout for model-assisted encoding")

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
    ollama.add_argument("--no-auto-web", action="store_false", dest="auto_web", help="Disable automatic web search heuristics")
    ollama.set_defaults(auto_web=True)
    ollama.add_argument("--web-k", type=int, default=5, help="Number of web results to include")
    ollama.add_argument("--web-timeout", type=int, default=20, help="Timeout for the web search request in seconds")
    ollama.add_argument("--fetch-pages", type=int, default=0, help="Fetch the top N web result pages and include text excerpts")
    ollama.add_argument("--fetch-timeout", type=int, default=15, help="Timeout for fetching each page in seconds")
    ollama.add_argument("--json", action="store_true", help="Output routing and model response as JSON")
    ollama.add_argument("--assistant", default="general", help=f"Assistant profile to use ({assistant_names})")
    ollama.add_argument("--model-assisted-encoder", action="store_true", help="Use the optional model-assisted encoder layer")
    ollama.add_argument("--encoder-model", default="llama3.2", help="Ollama model for model-assisted encoding")
    ollama.add_argument("--encoder-timeout", type=int, default=20, help="Timeout for model-assisted encoding")

    chat = sub.add_parser("chat", help="Start an interactive local chat session with Ollama")
    chat.add_argument("--model", default="llama3.2", help="Ollama model name")
    chat.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    chat.add_argument("--history-turns", type=int, default=6, help="Number of previous turns to keep in chat memory")
    chat.add_argument("--web", action="store_true", help="Always use web search for every message")
    chat.add_argument("--no-auto-web", action="store_false", dest="auto_web", help="Disable automatic web search heuristics")
    chat.set_defaults(auto_web=True)
    chat.add_argument("--web-k", type=int, default=5, help="Number of web results to include")
    chat.add_argument("--web-timeout", type=int, default=20, help="Timeout for the web search request in seconds")
    chat.add_argument("--fetch-pages", type=int, default=0, help="Fetch the top N web result pages and include text excerpts")
    chat.add_argument("--fetch-timeout", type=int, default=15, help="Timeout for fetching each page in seconds")
    chat.add_argument("--show-sources", action="store_true", help="Print fetched web source links in chat mode")
    chat.add_argument("--assistant", default="general", help=f"Assistant profile to use ({assistant_names})")
    chat.add_argument("--model-assisted-encoder", action="store_true", help="Use the optional model-assisted encoder layer")
    chat.add_argument("--encoder-model", default="llama3.2", help="Ollama model for model-assisted encoding")
    chat.add_argument("--encoder-timeout", type=int, default=20, help="Timeout for model-assisted encoding")

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
    elif args.command == "chat":
        cmd_chat(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

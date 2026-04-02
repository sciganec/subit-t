const WHO = ["THEY", "YOU", "ME", "WE"];
const WHAT = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"];
const WHEN = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"];

const WHO_LABEL = {
  THEY: "system-directed",
  YOU: "other-directed",
  ME: "self-directed",
  WE: "co-directed",
};

const WHAT_LABEL = {
  PRESERVE: "preserve",
  REDUCE: "reduce",
  EXPAND: "expand",
  TRANSFORM: "transform",
};

const WHEN_LABEL = {
  RELEASE: "release",
  INTEGRATE: "integrate",
  INITIATE: "initiate",
  SUSTAIN: "sustain",
};

const ARCHETYPE_GRID = {
  ME: {
    EXPAND: ["SEED", "DRAFTER", "PRIME", "AUTHOR"],
    TRANSFORM: ["ENGINE", "CLOSER", "LAUNCHER", "DRIVER"],
    REDUCE: ["WATCHER", "REFINER", "PROBE", "AUDITOR"],
    PRESERVE: ["HERMIT", "INDEXER", "LOGGER", "ARCHIVIST"],
  },
  WE: {
    EXPAND: ["POOL", "MERGE", "SPARK", "CHORUS"],
    TRANSFORM: ["STANDBY", "COMMIT", "DEPLOY", "SYNC"],
    REDUCE: ["QUORUM", "VERDICT", "COUNCIL", "TRIBUNAL"],
    PRESERVE: ["ORIGIN", "DIGEST", "LEDGER", "REGISTRY"],
  },
  YOU: {
    EXPAND: ["BUFFER", "ECHO", "RESPONDER", "ADAPTER"],
    TRANSFORM: ["QUEUE", "RESOLVER", "HANDLER", "EXECUTOR"],
    REDUCE: ["LISTENER", "FILTER", "INTAKE", "SCAN"],
    PRESERVE: ["VOID", "SNAPSHOT", "INTAKE_LOG", "CACHE"],
  },
  THEY: {
    EXPAND: ["SHADOW", "SIGNAL", "GHOST", "ORACLE"],
    TRANSFORM: ["DAEMON", "SWEEP", "TRIGGER", "FORCE"],
    REDUCE: ["SENTINEL", "VALIDATOR", "INSPECTOR", "MONITOR"],
    PRESERVE: ["CORE", "FOSSIL", "IMPRINT", "LEDGER_SYS"],
  },
};

const ARCHETYPE_ROLE = {
  PRIME: "Initiator. Generates from scratch. First impulse, maximum creative space.",
  AUTHOR: "Peak generator. Produces complete drafts at full capacity.",
  DRIVER: "Peak autonomous executor. Full speed, no blockers.",
  COUNCIL: "Collective analysis initiator. Opens group review.",
  SCAN: "Peak reactive analyzer. Deep critique of external input.",
  ADAPTER: "Peak reactive generator. Adapts at full capacity.",
  ORACLE: "Peak meta-generator. System-level insight production.",
  MONITOR: "Peak meta-analyzer. Full system observability active.",
  SYNC: "Peak collective executor. Full team in flow state.",
  FORCE: "Peak meta-executor. Full systemic action.",
};

const ASSISTANTS = {
  general: {
    label: "General",
    extra:
      "Assistant profile: General Assistant\nStyle: practical, concise, engineering-oriented. State assumptions when needed and avoid bluffing.",
  },
  review: {
    label: "Review",
    extra:
      "Assistant profile: Review Assistant\nPrioritize bugs, regressions, edge cases, unsafe assumptions, and missing validation. Lead with concrete findings.",
  },
  research: {
    label: "Research",
    extra:
      "Assistant profile: Research Assistant\nSeparate facts, assumptions, and recommendations. Prefer sourced, current information when possible.",
  },
  incident: {
    label: "Incident",
    extra:
      "Assistant profile: Incident Assistant\nPrioritize stabilization, rollback safety, containment, and short ordered next steps.",
  },
  planner: {
    label: "Planner",
    extra:
      "Assistant profile: Planning Assistant\nTurn requests into concrete plans with sequence, risk, and validation criteria.",
  },
  coding: {
    label: "Coding",
    extra:
      "Assistant profile: Coding Assistant\nPrefer implementation-oriented answers, minimal correct fixes, and explicit verification steps.",
  },
};

const EXAMPLES = [
  {
    id: "review-rollout",
    title: "Review rollout",
    category: "Review",
    assistant: "review",
    text: "Review this rollout plan and tell me what to change first before we merge.",
  },
  {
    id: "review-auth",
    title: "Auth audit",
    category: "Review",
    assistant: "review",
    text: "Audit this authentication flow and tell me the highest-risk security mistakes.",
  },
  {
    id: "incident-recover",
    title: "Recovery plan",
    category: "Incident",
    assistant: "incident",
    text: "Pause the rollout and recover after the failed deployment. What should we do first?",
  },
  {
    id: "incident-logs",
    title: "Root cause",
    category: "Incident",
    assistant: "incident",
    text: "The API is failing in production. Investigate logs and propose the safest next steps.",
  },
  {
    id: "research-python",
    title: "Latest Python",
    category: "Research",
    assistant: "research",
    text: "What is the latest Python release and what changed?",
  },
  {
    id: "research-llama",
    title: "Llama comparison",
    category: "Research",
    assistant: "research",
    text: "Compare local Llama deployment options for a small engineering team.",
  },
  {
    id: "plan-feature",
    title: "Feature plan",
    category: "Planning",
    assistant: "planner",
    text: "Turn this feature idea into a concrete implementation plan with risks and validation steps.",
  },
  {
    id: "plan-migration",
    title: "Migration plan",
    category: "Planning",
    assistant: "planner",
    text: "Plan a zero-downtime migration for a busy Postgres database.",
  },
  {
    id: "coding-refresh",
    title: "Token refresh",
    category: "Coding",
    assistant: "coding",
    text: "Explain token refresh in a web app and list the most common security mistakes.",
  },
  {
    id: "coding-react",
    title: "React architecture",
    category: "Coding",
    assistant: "coding",
    text: "Design a React architecture for a multi-panel AI assistant UI with local settings and chat history.",
  },
  {
    id: "team-sync",
    title: "Team alignment",
    category: "Coordination",
    assistant: "planner",
    text: "Let's coordinate the team around the Q2 launch plan and decide what to do this week.",
  },
  {
    id: "demo-subit",
    title: "What is SUBIT-T",
    category: "Demo",
    assistant: "general",
    text: "Explain what SUBIT-T does and why routed state transitions are better than generic prompting.",
  },
];

const PROVIDER_PRESETS = [
  {
    key: "studio-demo",
    label: "Studio Demo",
    description: "Fully autonomous local demo mode with built-in responses and route visualisation.",
    settings: {
      providerMode: "demo",
      endpoint: "",
      apiKey: "",
      model: "subit-t-demo-engine",
    },
  },
  {
    key: "ollama-llama32",
    label: "Ollama Llama 3.2",
    description: "Local Llama via Ollama. No API key required.",
    settings: {
      providerMode: "ollama",
      endpoint: "http://localhost:11434/v1/chat/completions",
      apiKey: "",
      model: "llama3.2",
    },
  },
  {
    key: "ollama-llama31",
    label: "Ollama Llama 3.1",
    description: "Alternative local Llama preset for larger offline runs.",
    settings: {
      providerMode: "ollama",
      endpoint: "http://localhost:11434/v1/chat/completions",
      apiKey: "",
      model: "llama3.1",
    },
  },
  {
    key: "openai-compatible",
    label: "OpenAI compatible",
    description: "Cloud endpoint if you want to swap in an external provider later.",
    settings: {
      providerMode: "cloud",
      endpoint: "https://api.openai.com/v1/chat/completions",
      model: "gpt-4o-mini",
    },
  },
];

const REVIEW_TERMS = ["review", "analyze", "audit", "debug", "check", "bug", "issue", "fix"];
const FACTUAL_TERMS = [
  "latest",
  "current",
  "today",
  "recent",
  "news",
  "weather",
  "price",
  "version",
  "who is",
  "what is",
  "when is",
  "compare",
];
const EXECUTION_TERMS = ["deploy", "run", "execute", "ship", "launch", "apply", "perform", "build"];
const TEAM_TERMS = ["we ", "let's", "team", "together", "coordinate", "align"];
const START_TERMS = ["start", "begin", "kick off", "new", "from scratch"];
const INCIDENT_TERMS = ["incident", "outage", "rollback", "revert", "recover", "failure", "mitigate"];

function containsAny(text, phrases) {
  return phrases.some((phrase) => text.includes(phrase));
}

function shift(order, value, delta) {
  const index = order.indexOf(value);
  return order[(index + delta + order.length) % order.length];
}

function stateFromDims(who, what, when) {
  return {
    who,
    what,
    when,
    name: ARCHETYPE_GRID[who][what][WHEN.indexOf(when)],
  };
}

export function applyOperator(state, operator) {
  if (operator === "WHO_SHIFT") {
    return stateFromDims(shift(WHO, state.who, 1), state.what, state.when);
  }
  if (operator === "WHAT_SHIFT") {
    return stateFromDims(state.who, shift(WHAT, state.what, 1), state.when);
  }
  if (operator === "WHEN_SHIFT") {
    return stateFromDims(state.who, state.what, shift(WHEN, state.when, 1));
  }
  return stateFromDims(
    shift(WHO, state.who, -1),
    shift(WHAT, state.what, -1),
    shift(WHEN, state.when, -1),
  );
}

export function encodeText(text) {
  const lowered = text.toLowerCase();
  const factualLookup = containsAny(lowered, FACTUAL_TERMS);
  const reviewRequest = containsAny(lowered, REVIEW_TERMS);
  const executionRequest = containsAny(lowered, EXECUTION_TERMS);
  const teamRequest = containsAny(lowered, TEAM_TERMS);
  const startRequest = containsAny(lowered, START_TERMS);
  const incidentRequest = containsAny(lowered, INCIDENT_TERMS);

  let who = "ME";
  let what = "EXPAND";
  let when = "SUSTAIN";

  if (factualLookup) {
    who = "THEY";
    what = "EXPAND";
  } else if (reviewRequest) {
    who = "YOU";
    what = "REDUCE";
  } else if (executionRequest) {
    who = "ME";
    what = "TRANSFORM";
  }

  if (teamRequest) {
    who = "WE";
  }
  if (startRequest) {
    when = "INITIATE";
  }
  if (incidentRequest) {
    who = teamRequest ? "WE" : "THEY";
    what = executionRequest ? "TRANSFORM" : "REDUCE";
  }

  const currentState = stateFromDims(who, what, when);

  let operator = "WHAT_SHIFT";
  let axisDiff = "WHAT";
  let routingReason = "default_expand";

  if (factualLookup || lowered.includes("rollback") || lowered.includes("revert")) {
    operator = "INV";
    axisDiff = "ALL";
    routingReason = factualLookup
      ? "factual_lookup_requires_external_grounding"
      : "explicit_rollback_signal";
  } else if (reviewRequest) {
    operator = "WHAT_SHIFT";
    axisDiff = "WHAT";
    routingReason = "review_request_prefers_what_shift";
  } else if (executionRequest && startRequest) {
    operator = "WHEN_SHIFT";
    axisDiff = "WHEN";
    routingReason = "execution_start_prefers_when_shift";
  } else if (executionRequest) {
    operator = "WHEN_SHIFT";
    axisDiff = "WHEN";
    routingReason = "execution_prefers_when_shift";
  } else if (teamRequest) {
    operator = "WHO_SHIFT";
    axisDiff = "WHO";
    routingReason = "team_request_prefers_who_shift";
  }

  const nextState = applyOperator(currentState, operator);

  return {
    currentState,
    nextState,
    operator,
    axisDiff,
    routingReason,
    signalSummary: {
      factualLookup,
      reviewRequest,
      executionRequest,
      teamRequest,
      startRequest,
      incidentRequest,
    },
  };
}

export function buildPrompt({ state, operator, input, assistantKey = "general" }) {
  const assistant = ASSISTANTS[assistantKey] ?? ASSISTANTS.general;
  const role = ARCHETYPE_ROLE[state.name] ?? `${state.name}. Routed archetype response mode.`;
  const opDescriptions = {
    WHO_SHIFT: "cyclic forward shift on WHO",
    WHAT_SHIFT: "cyclic forward shift on WHAT",
    WHEN_SHIFT: "cyclic forward shift on WHEN",
    INV: "global rollback by one step on all axes",
  };

  return [
    `[ARCHETYPE: ${state.name}]`,
    `WHO: ${state.who} -> ${WHO_LABEL[state.who]}`,
    `WHAT: ${state.what} -> ${WHAT_LABEL[state.what]}`,
    `WHEN: ${state.when} -> ${WHEN_LABEL[state.when]}`,
    `OPERATOR: ${operator} -> ${opDescriptions[operator]}`,
    "",
    `Role: ${role}`,
    assistant.extra,
    "",
    "Respond from this routed position. Be concise, concrete, and technically useful.",
    "",
    `User input: ${input}`,
  ].join("\n");
}

export function generateDemoResponse({ text, route, assistantKey }) {
  const intro = [
    `Routed through ${route.currentState.name} into ${route.nextState.name}.`,
    `The chosen move is ${route.operator}, which keeps the response deliberate instead of generic.`,
  ];

  if (assistantKey === "review") {
    return [
      ...intro,
      "The first thing to tighten is the highest-risk edge case: define the rollback condition, add a verification checkpoint before rollout, and make the stop criteria explicit.",
      "If this were a real review pass, I would next list the top regressions, missing tests, and the exact place where the plan is underspecified.",
    ].join(" ");
  }

  if (assistantKey === "incident") {
    return [
      ...intro,
      "Stabilize first: stop further rollout, capture the failing version and timestamps, and confirm whether rollback is safe before touching data.",
      "Then separate observations, hypotheses, and actions so the team is not debugging and changing the system at the same time.",
    ].join(" ");
  }

  if (assistantKey === "research") {
    return [
      ...intro,
      "For live factual topics, SUBIT-T prefers a grounded lane: note what is known, what may have changed, and what should be verified against external sources.",
      "That keeps the answer honest instead of letting the assistant bluff current information.",
    ].join(" ");
  }

  if (assistantKey === "planner") {
    return [
      ...intro,
      "A strong next move is to convert the request into phases: scope, dependencies, implementation sequence, risk controls, and validation criteria.",
      "That gives you a plan an engineer can execute, not just a paragraph of strategy talk.",
    ].join(" ");
  }

  if (assistantKey === "coding") {
    return [
      ...intro,
      "The practical answer should focus on a minimal correct implementation, the sharp edge cases, and how to verify the change in a real codebase.",
      "That is usually more useful than a long conceptual explanation with no operating details.",
    ].join(" ");
  }

  return [
    ...intro,
    `This autonomous demo mode is answering locally, so you can still showcase the routing system even without a live model endpoint.`,
    `Prompt received: "${text}"`,
  ].join(" ");
}

export function listAssistants() {
  return Object.entries(ASSISTANTS).map(([key, value]) => ({ key, label: value.label }));
}

export function listProviderPresets() {
  return PROVIDER_PRESETS;
}

export function listExamples() {
  return EXAMPLES;
}

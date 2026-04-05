const WHO = ["THEY", "YOU", "ME", "WE"];
const WHAT = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"];
const WHEN = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"];

const WHO_LOGIC = {
  THEY: "Objective/System level. Abstract laws and cosmos.",
  YOU: "Relational/Reactive level. Dialogue and empathy.",
  ME: "Subjective/Autonomous level. Individual will and action.",
  WE: "Collective/Synergetic level. Unity and synchronization.",
};

const WHAT_LOGIC = {
  PRESERVE: "Memory/Storage. Storing information for later.",
  REDUCE: "Analysis/Critique. Filtering out noise from signal.",
  EXPAND: "Creation/Ideation. Opening the space of possibilities.",
  TRANSFORM: "Execution/Transformation. Converting intent into result.",
};

const WHEN_LOGIC = {
  RELEASE: "Pause/Dormancy. Potentiation of the next cycle.",
  INTEGRATE: "Synthesis/Closing. Gathering results and experience.",
  INITIATE: "Impulse/Opening. The first spark of a new movement.",
  SUSTAIN: "Flow/Throughput. Active maintenance of process.",
};

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

const CURRENT_KW = {
  WHO: {
    ME: ["i ", "my ", "i'll", "let me", "i will", "i'm", "i've", "as for me", "myself"],
    WE: ["we ", "our ", "team", "together", "let's", "everyone", "we're", "squad", "group", "collective"],
    YOU: ["you ", "your ", "your code", "the issue", "the bug", "review this", "the function", "examine this", "check this"],
    THEY: ["system", "the model", "data shows", "historically", "evidence", "the pattern", "it shows"],
  },
  WHAT: {
    EXPAND: ["idea", "design", "draft", "brainstorm", "architecture", "document", "new approach", "proposal", "ideate", "generate"],
    TRANSFORM: ["running", "executing", "deploying", "building", "implementing", "pipeline", "in progress", "perform", "apply"],
    REDUCE: ["review", "analyze", "bug", "issue", "problem", "memory leak", "error", "debug", "logs", "outage", "vulnerabilit", "critique", "check", "audit", "glitch", "flaw", "defect", "examine", "inspect", "scrutinize"],
    PRESERVE: ["log", "store", "archive", "record", "save", "remember", "document", "note", "keep"],
  },
  WHEN: {
    INITIATE: ["start", "begin", "first", "scratch", "initial", "kick off", "new project", "today", "opening", "commence", "launch", "trigger"],
    SUSTAIN: ["now", "currently", "active", "working", "processing", "right now", "in progress", "asap", "presently", "forthwith"],
    INTEGRATE: ["finish", "complete", "wrap", "close", "done", "final", "commit", "conclude", "merge", "before the release", "end", "terminate", "finalize"],
    RELEASE: ["wait", "pause", "ready", "idle", "standby", "later", "hold", "queue", "pending"],
  },
};

const TARGET_KW = {
  WHO: {
    ME: ["i will", "let me", "i'll do", "on my own", "autonomously", "i can handle", "myself will"],
    WE: ["coordinate", "align", "team effort", "collaborate", "all of us", "share", "together we", "collective effort", "squad effort"],
    YOU: ["please review", "can you", "analyze this", "evaluate", "give feedback", "check this", "examine this", "inspect this"],
    THEY: ["observe", "monitor", "track", "watch", "report on", "the system should", "it should"],
  },
  WHAT: {
    EXPAND: ["generate", "create", "draft", "propose", "design", "come up with", "write", "document", "ideate"],
    TRANSFORM: ["run", "execute", "deploy", "ship", "implement", "apply", "perform", "launch", "build"],
    REDUCE: ["review", "analyze", "critique", "evaluate", "check", "test", "audit", "debug", "assess", "identify", "investigate", "examine", "inspect", "scrutinize"],
    PRESERVE: ["save", "document", "log", "store", "archive", "keep", "record", "note down"],
  },
  WHEN: {
    INITIATE: ["start", "begin", "fresh", "restart", "from scratch", "new", "reset", "kick off", "opening", "commence", "initiate", "trigger"],
    SUSTAIN: ["now", "immediately", "right away", "asap", "proceed", "continue", "keep going", "right now", "presently", "forthwith"],
    INTEGRATE: ["finish", "complete", "close", "wrap up", "finalize", "commit", "conclude", "deliver", "before the release", "end", "terminate"],
    RELEASE: ["later", "wait", "pause", "when ready", "no rush", "hold", "queue", "standby"],
  },
  ROLLBACK: {
    YES: ["rollback", "revert", "undo", "go back", "reverse", "undo that", "cancel last"]
  }
};

const SIGNAL_TERMS = {
  REVIEW: ["review", "critique", "feedback", "evaluate", "check this"],
  DESIGN_COLLAB: ["ideate", "brainstorm", "design together", "architecture", "proposal"],
  BUILD_START: ["let's build", "start implementing", "kick off", "ready to develop"],
  INCIDENT: ["outage", "broken", "critical bug", "fixed", "incident"],
  AUDIT: ["security audit", "risk assessment", "vulnerabilit"],
  CREATION: ["create", "generate", "new project", "fresh start"],
  EXECUTION: ["run this", "execute", "perform", "deploy now"],
  IMMEDIATE: ["asap", "immediately", "right now", "now"],
  FACTUAL_LOOKUP: ["what is", "tell me about", "historically", "data shows"],
  LOOKUP_VERBS: ["find", "search", "lookup", "explore"],
  TEAM: ["team", "we", "our", "all of us", "collective"],
};

function score(text, kwMap) {
  const lowered = text.toLowerCase();
  const scores = {};
  for (const [key, words] of Object.entries(kwMap)) {
    let count = 0;
    for (const word of words) {
      const pattern = new RegExp(`\\b${word.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
      if (pattern.test(lowered)) {
        const wordCount = word.split(/\s+/).length;
        count += wordCount > 1 ? (wordCount * wordCount) * 2 : 1;
      }
    }
    scores[key] = count;
  }
  return scores;
}

function pick(scores, fallback, priorityOrder = null) {
  const entries = Object.entries(scores);
  if (entries.length === 0 || entries.every(([, v]) => v === 0)) {
    return { value: fallback, score: 0 };
  }
  const maxVal = Math.max(...Object.values(scores));
  const candidates = entries.filter(([, v]) => v === maxVal).map(([k]) => k);
  
  if (candidates.length === 1) return { value: candidates[0], score: maxVal };
  if (priorityOrder) {
    for (const p of priorityOrder) {
      if (candidates.includes(p)) return { value: p, score: maxVal };
    }
  }
  return { value: candidates[0], score: maxVal };
}

function boost(scores, key, amount) {
  scores[key] = (scores[key] || 0) + amount;
}

function forwardSteps(order, current, target) {
  const curIdx = order.indexOf(current);
  const tarIdx = order.indexOf(target);
  return (tarIdx - curIdx + order.length) % order.length;
}

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

function shift(order, value, delta) {
  const index = order.indexOf(value);
  return order[(index + delta + order.length) % order.length];
}

export function stateFromDims(who, what, when) {
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

function containsAny(text, phrases) {
  const lowered = text.toLowerCase();
  return phrases.some((phrase) => {
    const pattern = new RegExp(`\\b${phrase.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
    return pattern.test(lowered);
  });
}

export function encodeText(text) {
  const lowered = text.toLowerCase();
  
  // 1. Detect Intents
  const intents = {
    review_request: containsAny(lowered, SIGNAL_TERMS.REVIEW),
    design_collab_request: containsAny(lowered, SIGNAL_TERMS.DESIGN_COLLAB),
    build_start_request: containsAny(lowered, SIGNAL_TERMS.BUILD_START),
    incident_request: containsAny(lowered, SIGNAL_TERMS.INCIDENT),
    audit_request: containsAny(lowered, SIGNAL_TERMS.AUDIT),
    creation_request: containsAny(lowered, SIGNAL_TERMS.CREATION),
    execution_request: containsAny(lowered, SIGNAL_TERMS.EXECUTION),
    immediate_request: containsAny(lowered, SIGNAL_TERMS.IMMEDIATE),
    factual_lookup: containsAny(lowered, SIGNAL_TERMS.FACTUAL_LOOKUP) && containsAny(lowered, SIGNAL_TERMS.LOOKUP_VERBS),
    team_request: containsAny(lowered, SIGNAL_TERMS.TEAM),
    rollback_score: TARGET_KW.ROLLBACK.YES.filter(w => lowered.includes(w)).length,
  };
  intents.rollback_detected = intents.rollback_score > 0;

  // 2. Score Dimensions
  const whoCur = score(lowered, CURRENT_KW.WHO);
  const whatCur = score(lowered, CURRENT_KW.WHAT);
  const whenCur = score(lowered, CURRENT_KW.WHEN);
  
  const whoTar = score(lowered, TARGET_KW.WHO);
  const whatTar = score(lowered, TARGET_KW.WHAT);
  const whenTar = score(lowered, TARGET_KW.WHEN);

  // 3. Apply Boosts
  if (intents.review_request || intents.incident_request) boost(whatCur, "REDUCE", 3);
  if (intents.design_collab_request) boost(whatCur, "EXPAND", 3);
  if (intents.creation_request) boost(whatCur, "EXPAND", 4);
  if (intents.execution_request) boost(whatCur, "TRANSFORM", 4);
  if (intents.team_request) boost(whoCur, "WE", 2);
  if (intents.rollback_detected) boost(whatCur, "EXPAND", 3);
  if (intents.review_request && intents.team_request) {
    boost(whoCur, "WE", 4);
    boost(whatCur, "REDUCE", 4);
  }

  // 4. Penalty overrides
  if ((whoCur.YOU || 0) > 2) whoCur.ME = Math.max(0, (whoCur.ME || 0) - 4);
  if ((whoCur.WE || 0) > 2) {
    whoCur.ME = Math.max(0, (whoCur.ME || 0) - 4);
    whoCur.YOU = Math.max(0, (whoCur.YOU || 0) - 2);
  }
  if ((whatCur.TRANSFORM || 0) > 2) whatCur.EXPAND = Math.max(0, (whatCur.EXPAND || 0) - 4);
  if ((whatCur.REDUCE || 0) > 2) whatCur.EXPAND = Math.max(0, (whatCur.EXPAND || 0) - 4);

  // 5. Final Dimension Picks
  const bestWho = pick(whoCur, "ME", ["YOU", "WE", "THEY"]);
  const bestWhat = pick(whatCur, "EXPAND", ["REDUCE", "TRANSFORM", "PRESERVE"]);
  const bestWhen = pick(whenCur, "SUSTAIN", ["INITIATE", "INTEGRATE", "RELEASE"]);

  const currentState = stateFromDims(bestWho.value, bestWhat.value, bestWhen.value);

  const bestWhoTar = pick(whoTar, null);
  const bestWhatTar = pick(whatTar, null);
  const bestWhenTar = pick(whenTar, null);

  // 6. Operator Calculation (Closest Axis)
  const diffs = [];
  if (bestWhoTar.value && bestWhoTar.value !== bestWho.value) {
    diffs.push({ axis: "WHO", op: "WHO_SHIFT", steps: forwardSteps(WHO, bestWho.value, bestWhoTar.value) });
  }
  if (bestWhatTar.value && bestWhatTar.value !== bestWhat.value) {
    diffs.push({ axis: "WHAT", op: "WHAT_SHIFT", steps: forwardSteps(WHAT, bestWhat.value, bestWhatTar.value) });
  }
  if (bestWhenTar.value && bestWhenTar.value !== bestWhen.value) {
    diffs.push({ axis: "WHEN", op: "WHEN_SHIFT", steps: forwardSteps(WHEN, bestWhen.value, bestWhenTar.value) });
  }

  let operator = "WHAT_SHIFT";
  let axisDiff = "WHAT";
  let routingReason = "default_expand";

  if (intents.factual_lookup && intents.rollback_score > 0) {
    operator = "INV";
    axisDiff = "ALL";
    routingReason = "factual_lookup_grounding";
  } else if (intents.rollback_score > 0) {
    operator = "INV";
    axisDiff = "ALL";
    routingReason = "explicit_rollback";
  } else if (diffs.length > 0) {
    const axisOrder = { WHO: 0, WHAT: 1, WHEN: 2 };
    diffs.sort((a, b) => a.steps - b.steps || axisOrder[a.axis] - axisOrder[b.axis]);
    
    let chosen = diffs[0];
    routingReason = `closest_axis_${chosen.axis.toLowerCase()}`;

    if (intents.execution_request && intents.immediate_request && diffs.some(d => d.axis === "WHEN")) {
      chosen = diffs.find(d => d.axis === "WHEN");
      routingReason = "immediate_prefers_when";
    } else if (intents.review_request && diffs.some(d => d.axis === "WHAT")) {
      chosen = diffs.find(d => d.axis === "WHAT");
      routingReason = "review_prefers_what";
    } else if (intents.build_start_request && diffs.some(d => d.axis === "WHEN")) {
      chosen = diffs.find(d => d.axis === "WHEN");
      routingReason = "build_start_prefers_when";
    } else if (intents.creation_request && diffs.some(d => d.axis === "WHAT")) {
      chosen = diffs.find(d => d.axis === "WHAT");
      routingReason = "creation_prefers_what";
    } else if (intents.design_collab_request && diffs.some(d => d.axis === "WHAT")) {
      chosen = diffs.find(d => d.axis === "WHAT");
      routingReason = "design_prefers_what";
    }

    operator = chosen.op;
    axisDiff = chosen.axis;
  } else {
    // Cycle priority
    const signals = {
      WHO_SHIFT: Object.values(whoTar).reduce((a, b) => a + b, 0),
      WHAT_SHIFT: Object.values(whatTar).reduce((a, b) => a + b, 0) + Object.values(whatCur).reduce((a, b) => a + b, 0),
      WHEN_SHIFT: Object.values(whenTar).reduce((a, b) => a + b, 0) + Object.values(whenCur).reduce((a, b) => a + b, 0),
    };
    if (intents.review_request) signals.WHAT_SHIFT += 8;
    if (intents.build_start_request) signals.WHEN_SHIFT += 8;
    if (intents.audit_request) signals.WHAT_SHIFT += 10;

    const cyclePriority = ["WHAT_SHIFT", "WHEN_SHIFT", "WHO_SHIFT"];
    operator = cyclePriority.sort((a, b) => signals[b] - signals[a] || cyclePriority.indexOf(a) - cyclePriority.indexOf(b))[0];
    axisDiff = operator.split("_")[0];
    routingReason = "signal_fallback";
  }

  const nextState = applyOperator(currentState, operator);

  return {
    currentState,
    nextState,
    operator,
    axisDiff,
    routingReason,
    signalSummary: intents,
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

export function getAxisLogic() {
  return { WHO: WHO_LOGIC, WHAT: WHAT_LOGIC, WHEN: WHEN_LOGIC };
}

export function listAllArchetypes() {
  const all = [];
  for (const w of WHO) {
    for (const x of WHAT) {
      for (const y of WHEN) {
        const state = stateFromDims(w, x, y);
        const { row, col } = getLatticeCoords(w, x, y);
        all.push({
          ...state,
          row,
          col,
          logic: {
            who: WHO_LOGIC[w],
            what: WHAT_LOGIC[x],
            when: WHEN_LOGIC[y],
            role: ARCHETYPE_ROLE[state.name] || `${state.name} archetype.`,
          },
        });
      }
    }
  }
  return all;
}

export function getLatticeCoords(who, what, when) {
  const w = WHO.indexOf(who);
  const x = WHAT.indexOf(what);
  const y = WHEN.indexOf(when);
  
  // Mapping 4x4x4 to 8x8 Lattice
  // Row = WHO (4) x WHAT_high (2)
  // Col = WHEN (4) x WHAT_low (2)
  const row = w * 2 + Math.floor(x / 2);
  const col = y * 2 + (x % 2);
  
  return { row, col };
}

export function getNeighbors(state) {
  const neighbors = [];
  const ops = ["WHO_SHIFT", "WHAT_SHIFT", "WHEN_SHIFT", "INV"];
  for (const op of ops) {
    const next = applyOperator(state, op);
    neighbors.push({ op, name: next.name, state: next });
  }
  return neighbors;
}

export function getTorusCoords(state, R = 3, r = 1) {
  const { row, col } = getLatticeCoords(state.who, state.what, state.when);
  
  // Map 8x8 to [0, 2π]
  const theta = (row / 8) * Math.PI * 2;
  const phi = (col / 8) * Math.PI * 2;
  
  const x = (R + r * Math.cos(phi)) * Math.cos(theta);
  const y = (R + r * Math.cos(phi)) * Math.sin(theta);
  const z = r * Math.sin(phi);
  
  return [x, y, z];
}

import { useDeferredValue, useEffect, useRef, useState, useTransition } from "react";
import {
  buildPrompt,
  encodeText,
  generateDemoResponse,
  listAssistants,
  listExamples,
  listProviderPresets,
  stateFromDims,
} from "./lib/subit";
import UnifiedObservatory from "./components/UnifiedObservatory";
import TopologicalView from "./components/TopologicalView";
import logoMark from "./assets/subit-mark.svg";
import wordmark from "./assets/subit-wordmark.svg";
import splashArt from "./assets/subit-splash.svg";

const STORAGE_KEY = "subit-t-ai-settings";
const generateId = () => Date.now().toString(36) + Math.random().toString(36).substring(2);
const ASSISTANTS = listAssistants();
const PRESETS = listProviderPresets();
const EXAMPLES = listExamples();

const DEFAULT_SETTINGS = {
  providerMode: "demo",
  endpoint: "",
  apiKey: "",
  model: "subit-t-demo-engine",
  assistant: "general",
  temperature: "0.4",
};

const STARTER = [
  {
    id: "welcome",
    role: "assistant",
    content:
      "Welcome to SUBIT-T AI Studio. This build can run in fully autonomous demo mode or connect to local Llama through Ollama. Pick a preset, choose an example, and watch the route trace update live.",
    route: {
      currentState: { name: "SCAN", who: "YOU", what: "REDUCE", when: "SUSTAIN" },
      operator: "WHAT_SHIFT",
      nextState: { name: "ADAPTER", who: "YOU", what: "EXPAND", when: "SUSTAIN" },
      axisDiff: "WHAT",
      routingReason: "studio_welcome",
      signalSummary: {},
    },
  },
];

const DOCTRINE = [
  {
    title: "Routing over prompting",
    text: "SUBIT-T treats every answer as a deliberate next move in a bounded state space, not as a generic blob of language.",
  },
  {
    title: "Closed cyclic algebra",
    text: "The system lives in a 64-state lattice with four operators. No dead ends, no accidental idempotence, no hand-wavy state transitions.",
  },
  {
    title: "Visible cognitive posture",
    text: "Every reply is explainable through WHO, WHAT, and WHEN. The route is part of the product, not hidden behind the model.",
  },
  {
    title: "Rollback is first-class",
    text: "INV is not a hack. Recovery and external grounding are formal operators in the system, which makes error handling legible.",
  },
];

const TUTORIAL_STEPS = [
  {
    step: "1. Choose your runtime",
    detail:
      "Use Studio Demo for fully autonomous presentations, or switch to Ollama Llama for real local responses with no cloud dependency.",
  },
  {
    step: "2. Start from scenarios",
    detail:
      "Pick a scenario card first. SUBIT-T becomes much easier to understand when you feel how review, incident, planning, and research routes differ.",
  },
  {
    step: "3. Watch the route trace",
    detail:
      "Every prompt produces a current state, an operator, and a next state. That trace is the product's core teaching surface.",
  },
  {
    step: "4. Read the prompt layer",
    detail:
      "Open the rendered system prompt to see how state, operator, and assistant mode combine into a deliberate instruction set.",
  },
  {
    step: "5. Think in trajectories",
    detail:
      "One move is useful. A planned sequence is where the algebra starts to feel powerful. Ask what the next move should be after this one.",
  },
];

const THEORY_CARDS = [
  {
    title: "WHO",
    subtitle: "Orientation of attention",
    body: "THEY, YOU, ME, WE define whether the assistant is system-level, reactive, autonomous, or collective.",
  },
  {
    title: "WHAT",
    subtitle: "Operation on information",
    body: "PRESERVE, REDUCE, EXPAND, TRANSFORM let you see whether the next move is memory, critique, ideation, or execution.",
  },
  {
    title: "WHEN",
    subtitle: "Phase of the cycle",
    body: "RELEASE, INTEGRATE, INITIATE, SUSTAIN describe temporal posture: dormant, closing, opening, or active throughput.",
  },
  {
    title: "INV",
    subtitle: "Global rollback",
    body: "A first-class reverse move across all axes. Use it for recovery, reset, and external grounding instead of pretending the model always knows enough.",
  },
];

const RITUALS = [
  "For reviews, start in SCAN and ask what the next safe shift is before you ask for a verdict.",
  "For incidents, separate stabilization, hypotheses, and actions before you ask the model to produce fixes.",
  "For planning, make the route visible to the team. People trust structured transitions more than raw AI confidence.",
  "For research, let factual queries trigger grounded or rollback-like behavior instead of bluff-heavy chat responses.",
];

const PRESENTATION_TIPS = [
  "Open with Studio Demo to explain the theory without any infra friction.",
  "Switch to Ollama Llama live so the audience sees the same UX working with a real local model.",
  "Use one prompt from Review, one from Incident, and one from Research. Those three make the routing difference obvious fast.",
];

const LANDING_PILLARS = [
  "A bounded 64-state intelligence lattice",
  "A local-first path through Ollama and Llama",
  "A visible route trace for every answer",
  "A theory layer strong enough to teach, not just demo",
];

const LANDING_PATHS = [
  {
    title: "Enter Studio",
    body: "Go straight into the routed assistant, try scenarios, and switch between autonomous mode and local Llama.",
  },
  {
    title: "Learn the Doctrine",
    body: "Understand WHO, WHAT, WHEN, and INV before you ever ask the model a question.",
  },
  {
    title: "Present the Movement",
    body: "Use the built-in rituals and scenario library to make SUBIT-T feel like a real operating system for thought.",
  },
];

const PHILOSOPHY_CARDS = [
  {
    title: "Structural Monism",
    subtitle: "Posture is State",
    body: "SUBIT-T eliminates the dualism of data and instruction. The 64-state lattice is not a menu of commands; it is a space of unified cognitive postures where being in a state is identical to performing its associated action.",
  },
  {
    title: "Monadology",
    subtitle: "The Simple Substance",
    body: "Inspired by Leibniz, every 6-bit state is a 'monad'—a simple, indivisible unit that reflects the entire system's intent. There are no parts, only transitions. Each state perceives the user's goal from its own unique mathematical coordinate.",
  },
  {
    title: "Calculus Ratiocinator",
    subtitle: "Reason as Computation",
    body: "The project is a spiritual successor to Leibniz's Step Reckoner. By formalizing transitions as Z4 cyclic ops (WHO_SHIFT, WHAT_SHIFT, WHEN_SHIFT, INV), we turn reasoning into a deterministic algebra where errors are solvable via rollback.",
  },
];

function loadSettings() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

function groupExamples() {
  const grouped = new Map();
  for (const example of EXAMPLES) {
    const current = grouped.get(example.category) ?? [];
    current.push(example);
    grouped.set(example.category, current);
  }
  return [...grouped.entries()];
}

function MessageCard({ item }) {
  return (
    <article className={`message-card message-${item.role}`}>
      <div className="message-head">
        <span className="speaker">{item.role === "user" ? "You" : "SUBIT-T AI"}</span>
        {item.route ? (
          <span className="route-chip">
            {item.route.currentState.name}
            {" -> "}
            {item.route.operator}
            {" -> "}
            {item.route.nextState.name}
          </span>
        ) : null}
      </div>
      <p>{item.content}</p>
    </article>
  );
}

function RouteInspector({ route, prompt }) {
  if (!route) {
    return (
      <section className="panel inspector-panel">
        <div className="panel-header">
          <h3>Route Inspector</h3>
        </div>
        <p>Pick an example or send a message to inspect `current_state`, `operator`, and `next_state`.</p>
      </section>
    );
  }

  const activeSignals = Object.entries(route.signalSummary).filter(([, value]) => value);

  return (
    <section className="panel inspector-panel">
      <div className="panel-header">
        <h3>Route Inspector</h3>
        <span className="muted-chip">{route.routingReason}</span>
      </div>
      <div className="inspector-grid">
        <MetricCard label="Current" primary={route.currentState.name} secondary={`${route.currentState.who} / ${route.currentState.what} / ${route.currentState.when}`} />
        <MetricCard label="Operator" primary={route.operator} secondary={route.axisDiff} />
        <MetricCard label="Next" primary={route.nextState.name} secondary={`${route.nextState.who} / ${route.nextState.what} / ${route.nextState.when}`} />
      </div>
      <div className="signal-strip">
        {activeSignals.length ? activeSignals.map(([key]) => (
          <span className="signal-chip" key={key}>
            {key}
          </span>
        )) : <span className="signal-chip muted">no dominant signal flags</span>}
      </div>
      <RouteTimeline route={route} />
      <details className="prompt-details">
        <summary>Rendered system prompt</summary>
        <pre>{prompt}</pre>
      </details>
    </section>
  );
}

function RouteTimeline({ route }) {
  const steps = [
    {
      title: "Current posture",
      name: route.currentState.name,
      meta: `${route.currentState.who} / ${route.currentState.what} / ${route.currentState.when}`,
    },
    {
      title: "Operator",
      name: route.operator,
      meta: route.routingReason,
    },
    {
      title: "Next move",
      name: route.nextState.name,
      meta: `${route.nextState.who} / ${route.nextState.what} / ${route.nextState.when}`,
    },
  ];

  return (
    <div className="timeline-block">
      <div className="timeline-head">
        <span className="metric-label">Route timeline</span>
        <span className="muted-chip">deliberate transition</span>
      </div>
      <div className="timeline">
        {steps.map((step, index) => (
          <div className="timeline-step" key={step.title}>
            <div className="timeline-node">{index + 1}</div>
            <div className="timeline-copy">
              <strong>{step.title}</strong>
              <span className="timeline-primary">{step.name}</span>
              <span>{step.meta}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricCard({ label, primary, secondary }) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <strong>{primary}</strong>
      <span>{secondary}</span>
    </div>
  );
}

function PresetCard({ preset, active, onApply }) {
  return (
    <button
      type="button"
      className={`preset-card ${active ? "is-active" : ""}`}
      onClick={() => onApply(preset)}
    >
      <strong>{preset.label}</strong>
      <span>{preset.description}</span>
      <small>{preset.settings.model}</small>
    </button>
  );
}

function ExampleCard({ example, onUse }) {
  return (
    <button type="button" className="example-card" onClick={() => onUse(example)}>
      <span className="example-tag">{example.category}</span>
      <strong>{example.title}</strong>
      <span>{example.text}</span>
    </button>
  );
}

function DoctrineCard({ item }) {
  return (
    <article className="doctrine-card">
      <strong>{item.title}</strong>
      <p>{item.text}</p>
    </article>
  );
}

function TheoryCard({ item }) {
  return (
    <article className="theory-card">
      <span className="example-tag">{item.title}</span>
      <strong>{item.subtitle}</strong>
      <p>{item.body}</p>
    </article>
  );
}

function PhilosophyCard({ item }) {
  return (
    <article className="philosophy-card">
      <span className="brand-topline">{item.title}</span>
      <h3>{item.subtitle}</h3>
      <p>{item.body}</p>
    </article>
  );
}

function Landing({ onEnterStudio, activeState, onSelect }) {
  return (
    <div className="landing-shell">
      <header className="landing-nav">
        <img className="landing-mark" src={logoMark} alt="SUBIT-T mark" />
        <img className="landing-wordmark" src={wordmark} alt="SUBIT-T AI wordmark" />
        <button type="button" className="primary-button" onClick={onEnterStudio}>
          Enter Studio
        </button>
      </header>

      <section className="landing-hero">
        <div className="landing-copy">
          <span className="section-tag">Deliberate intelligence</span>
          <h1>SUBIT-T AI is what happens when routing becomes a worldview.</h1>
          <p>
            Not just another chat wrapper. Not just another prompt library. A system that
            treats every answer as a visible transition in a closed cognitive algebra.
          </p>
          <div className="landing-actions">
            <button type="button" className="primary-button" onClick={onEnterStudio}>
              Launch the studio
            </button>
            <a className="secondary-link" href="#doctrine">
              Read the doctrine
            </a>
          </div>
          <div className="brand-badges">
            {LANDING_PILLARS.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>
        <div className="landing-visual-full">
          <UnifiedObservatory 
            activeState={activeState} 
            onSelect={onSelect} 
          />
        </div>
      </section>

      <section className="landing-story">
        <div className="story-grid">
          {LANDING_PATHS.map((item) => (
            <article className="story-card" key={item.title}>
              <strong>{item.title}</strong>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="doctrine" className="landing-doctrine">
        <div className="landing-section-head">
          <span className="section-tag">The doctrine</span>
          <h2>Why people remember SUBIT-T after they see it once</h2>
        </div>
        <div className="doctrine-grid">
          {DOCTRINE.map((item) => (
            <DoctrineCard key={item.title} item={item} />
          ))}
        </div>
      </section>

      <section className="landing-theory">
        <div className="landing-section-head">
          <span className="section-tag">Core theory</span>
          <h2>The four pieces people need to internalize</h2>
        </div>
        <div className="theory-grid">
          {THEORY_CARDS.map((item) => (
            <TheoryCard key={item.title} item={item} />
          ))}
        </div>
      </section>

      <section className="landing-philosophy">
        <div className="landing-section-head">
          <span className="section-tag">The Leibniz Milestone</span>
          <h2>Structural Monism & Monadology</h2>
          <p>
            SUBIT-T v0.4.0 is more than a technical update. It is a deep-dive into the 
            historical and philosophical debt we owe to Gottfried Wilhelm Leibniz.
            Explore the three pillars of our structural monism approach.
          </p>
        </div>
        <div className="philosophy-grid">
          {PHILOSOPHY_CARDS.map((item, index) => (
            <PhilosophyCard key={index} item={item} />
          ))}
        </div>
      </section>

      <section className="landing-footer">
        <img className="footer-wordmark" src={wordmark} alt="SUBIT-T AI wordmark" />
        <p>
          A routing discipline for AI systems that want composability, observability, and
          recovery to be part of their identity.
        </p>
      </section>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState("home");
  const [viewPhase, setViewPhase] = useState("idle");
  const [landingFocus, setLandingFocus] = useState(STARTER[0].route.currentState);
  const [settings, setSettings] = useState(loadSettings);
  const [messages, setMessages] = useState(STARTER);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [statusText, setStatusText] = useState("Studio demo mode is ready.");
  const [lastRoute, setLastRoute] = useState(null);
  const [lastPrompt, setLastPrompt] = useState("");
  const [routeFlashKey, setRouteFlashKey] = useState(0);
  const [studioTab, setStudioTab] = useState("chat"); // ["chat", "observatory"]
  const [isPending, startTransition] = useTransition();
  const bottomRef = useRef(null);

  const deferredInput = useDeferredValue(input);
  const previewRoute = deferredInput.trim() ? encodeText(deferredInput.trim()) : null;
  const exampleGroups = groupExamples();

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const needsEndpoint = settings.providerMode !== "demo";
  const canSend =
    input.trim().length > 0 &&
    settings.model.trim().length > 0 &&
    (!needsEndpoint || settings.endpoint.trim().length > 0);

  function patchSettings(key, value) {
    setSettings((current) => ({ ...current, [key]: value }));
  }

  function applyPreset(preset) {
    setSettings((current) => ({
      ...current,
      ...preset.settings,
    }));
    setError("");
    if (preset.settings.providerMode === "demo") {
      setStatusText("Autonomous studio mode selected. No endpoint or key needed.");
    } else if (preset.settings.providerMode === "ollama") {
      setStatusText("Local Llama mode selected. Start Ollama and keep the browser on this machine.");
    } else {
      setStatusText("Cloud mode selected. You may need an API key and a CORS-friendly endpoint.");
    }
  }

  function applyExample(example) {
    setInput(example.text);
    setSettings((current) => ({ ...current, assistant: example.assistant }));
    setError("");
  }

  function resetChat() {
    setMessages(STARTER);
    setLastRoute(null);
    setLastPrompt("");
    setError("");
    setStatusText("Conversation reset.");
  }

  function enterStudio() {
    setViewPhase("to-studio");
    window.setTimeout(() => {
      setView("studio");
      setViewPhase("studio-enter");
      window.setTimeout(() => setViewPhase("idle"), 420);
    }, 260);
  }

  function goHome() {
    setViewPhase("to-home");
    window.setTimeout(() => {
      setView("home");
      setViewPhase("home-enter");
      window.setTimeout(() => setViewPhase("idle"), 420);
    }, 260);
  }

  async function onSubmit(event) {
    event.preventDefault();
    if (!canSend || isPending) {
      return;
    }

    const text = input.trim();
    const route = encodeText(text);
    const prompt = buildPrompt({
      state: route.nextState,
      operator: route.operator,
      input: text,
      assistantKey: settings.assistant,
    });
    const userMessage = { id: generateId(), role: "user", content: text, route };

    setInput("");
    setError("");
    setStatusText("Routing and generating response...");
    setLastRoute(route);
    setLastPrompt(prompt);
    setRouteFlashKey((value) => value + 1);
    setMessages((current) => [...current, userMessage]);

    startTransition(async () => {
      try {
        const content =
          settings.providerMode === "demo"
            ? generateDemoResponse({ text, route, assistantKey: settings.assistant })
            : await fetchCompletion({
                endpoint: settings.endpoint,
                apiKey: settings.apiKey,
                model: settings.model,
                temperature: settings.temperature,
                prompt,
                text,
                messages,
              });

        setMessages((current) => [
          ...current,
          { id: generateId(), role: "assistant", content, route },
        ]);
        setStatusText(
          settings.providerMode === "demo"
            ? "Autonomous response generated locally."
            : "Model response received.",
        );
      } catch (requestError) {
        setError(describeRequestError(requestError, settings.endpoint));
        setStatusText("Request failed.");
      }
    });
  }

  async function handleManualFocus(monad) {
    const route = {
      currentState: lastRoute?.nextState || messages[messages.length - 1]?.route?.nextState,
      nextState: monad,
      operator: "MANUAL_FOCUS",
      routingReason: "Manual atlas selection",
      signalSummary: {}
    };
    const nextPrompt = buildPrompt({
      state: monad,
      operator: "MANUAL_FOCUS",
      input: "Exploring the grid.",
      assistantKey: settings.assistant
    });
    
    setLastRoute(route);
    setLastPrompt(nextPrompt);
    setStudioTab("chat"); 
  }

  if (view === "home") {
    return (
      <div className={`app-stage ${viewPhase}`}>
        <Landing 
          onEnterStudio={enterStudio} 
          activeState={landingFocus}
          onSelect={setLandingFocus}
        />
      </div>
    );
  }

  return (
    <div className={`app-stage ${viewPhase}`}>
      <div className="studio-shell">
        <aside className="studio-sidebar">
          <header className="brand-panel">
            <div className="brand-lockup" onClick={goHome} style={{ cursor: "pointer" }}>
              <img src={logoMark} alt="" className="brand-mark" />
              <div className="brand-copy">
                <span className="brand-topline">SUBIT-T // v0.4.0</span>
                <h1>Studio</h1>
              </div>
            </div>
            <div className="brand-badges">
              <span className="route-chip">Leibniz Milestone</span>
              <span className="muted-chip">64 States</span>
            </div>
          </header>

          <nav className="panel studio-nav">
            <button 
              className={`preset-card ${studioTab === "chat" ? "is-active" : ""}`}
              onClick={() => setStudioTab("chat")}
              style={{ width: "100%", marginBottom: "8px" }}
            >
              <strong>Studio Chat</strong>
              <span>Interactive dialogue & routing</span>
            </button>
            <button 
              className={`preset-card ${studioTab === "observatory" ? "is-active" : ""}`}
              onClick={() => setStudioTab("observatory")}
              style={{ width: "100%" }}
            >
              <strong>Monadology Grid</strong>
              <span>64-state topology map</span>
            </button>
          </nav>

          <section className="panel settings-panel">
            <div className="panel-header">
              <h2>Runtime</h2>
              <button className="soft-button" type="button" onClick={resetChat}>Reset</button>
              <button className="soft-button" type="button" onClick={goHome}>Home</button>
            </div>
            <div className="preset-grid">
              {PRESETS.map((p) => (
                <PresetCard 
                  key={p.key} 
                  preset={p} 
                  active={settings.providerMode === p.settings.providerMode && settings.model === p.settings.model} 
                  onApply={applyPreset} 
                />
              ))}
            </div>
            <div className="field-grid">
              <label>Provider mode<input value={settings.providerMode} readOnly /></label>
              <label>Model 
                <input 
                  value={settings.model} 
                  onChange={(e) => patchSettings("model", e.target.value)} 
                />
              </label>
            </div>
            <label>Endpoint 
              <input 
                value={settings.endpoint} 
                onChange={(e) => patchSettings("endpoint", e.target.value)} 
              />
            </label>
            <div className="field-grid">
              <label>Assistant
                <select value={settings.assistant} onChange={(e) => patchSettings("assistant", e.target.value)}>
                  {ASSISTANTS.map(a => <option key={a.key} value={a.key}>{a.label}</option>)}
                </select>
              </label>
              <label>Temperature
                <input value={settings.temperature} onChange={(e) => patchSettings("temperature", e.target.value)} />
              </label>
            </div>
          </section>

          {studioTab === "chat" && (lastRoute || previewRoute) && (
            <div key={routeFlashKey} className="route-inspector-shell">
              <RouteInspector 
                route={lastRoute ?? previewRoute} 
                prompt={lastPrompt || (previewRoute ? buildPrompt({
                  state: previewRoute.nextState,
                  operator: previewRoute.operator,
                  input: deferredInput.trim(),
                  assistantKey: settings.assistant,
                }) : "")} 
              />
            </div>
          )}
        </aside>

        <main className="studio-main">
          {studioTab === "chat" ? (
            <>
              <header className="hero-panel">
                <div className="hero-copy">
                  <span className="section-tag">Interactive Analysis</span>
                  <h2>Calculus Ratiocinator</h2>
                  <p>Every response is a state transition. The system prompt is rebuilt live based on the current monad.</p>
                </div>
                <div className="hero-stats">
                  <MetricCard label="PARITY" primary="99.7%" secondary="stable" />
                  <MetricCard label="AXES" primary="3 (Z4)" secondary="WHO/WHAT/WHEN" />
                  <MetricCard label="SPACE" primary="64" secondary="states" />
                </div>
              </header>

              <section className="panel chat-panel">
                <div className="panel-header">
                  <h2>Studio Chat</h2>
                  <div className="tab-switcher">
                    <button className="soft-button" onClick={() => setStudioTab("observatory")}>
                      Open Observatory
                    </button>
                  </div>
                </div>
                <div className="chat-log">
                  {messages.map((m) => (
                    <MessageCard key={m.id} item={m} />
                  ))}
                  {statusText && <div className="status-bar">{statusText}</div>}
                  {error && <div className="error-bar">{error}</div>}
                  <div ref={bottomRef} />
                </div>
                <form className="composer" onSubmit={onSubmit}>
                  <textarea
                    placeholder="Enter prompt to trigger route..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        onSubmit(e);
                      }
                    }}
                  />
                  <div className="composer-actions">
                    <button type="submit" className="primary-button" disabled={!canSend || isPending}>
                      {isPending ? "Routing..." : "Send Prompt"}
                    </button>
                  </div>
                </form>
              </section>

              <section className="panel route-panel">
                <RouteInspector 
                  route={lastRoute || messages[messages.length - 1]?.route} 
                  prompt={lastPrompt} 
                />
              </section>

              <section className="panel examples-section">
                <div className="panel-header">
                  <h2>Scenarios</h2>
                </div>
                <div className="example-groups" style={{ padding: '0 24px 24px' }}>
                  {exampleGroups.map(([cat, items]) => (
                    <div key={cat} className="example-group">
                      <h3>{cat}</h3>
                      <div className="example-grid">
                        {items.map(ex => <ExampleCard key={ex.id} example={ex} onUse={applyExample} />)}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </>
          ) : (
            <div className="studio-main-observatory">
              <UnifiedObservatory
                activeState={lastRoute?.nextState || messages[messages.length - 1]?.route?.nextState}
                onSelect={handleManualFocus}
              />
            </div>
          )}

          <section className="panel doctrine-panel">
            <div className="panel-header">
              <h2>Doctrine</h2>
            </div>
            <div className="doctrine-grid">
              {DOCTRINE.map(d => <DoctrineCard key={d.title} item={d} />)}
            </div>
          </section>

          <section className="panel tutorial-panel">
             <div className="panel-header"><h2>Tutorial</h2></div>
             <div className="tutorial-grid">
                <div className="tutorial-column">
                  {TUTORIAL_STEPS.map(s => <article className="tutorial-step" key={s.step}><strong>{s.step}</strong><p>{s.detail}</p></article>)}
                </div>
                <div className="tutorial-column">
                  <div className="mini-manifesto">
                    <h3>Theory</h3>
                    <div className="theory-grid">
                      {THEORY_CARDS.map(t => <TheoryCard key={t.title} item={t} />)}
                    </div>
                  </div>
                </div>
             </div>
          </section>
        </main>
      </div>
    </div>
  );
}

async function fetchCompletion({ endpoint, apiKey, model, temperature, prompt, text, messages }) {
  const headers = { "Content-Type": "application/json" };
  if (apiKey.trim()) {
    headers.Authorization = `Bearer ${apiKey.trim()}`;
  }

  const history = messages
    .filter((message) => message.id !== "welcome")
    .slice(-6)
    .map((message) => ({ role: message.role, content: message.content }));

  const response = await fetch(endpoint, {
    method: "POST",
    headers,
    body: JSON.stringify({
      model,
      temperature: Number.parseFloat(temperature) || 0.4,
      messages: [{ role: "system", content: prompt }, ...history, { role: "user", content: text }],
    }),
  });

  if (!response.ok) {
    const details = await response.text();
    throw new Error(`API request failed (${response.status}): ${details.slice(0, 240)}`);
  }

  const payload = await response.json();
  const content = payload?.choices?.[0]?.message?.content;
  if (typeof content !== "string" || !content.trim()) {
    throw new Error("The model response did not contain chat text.");
  }
  return content.trim();
}

function describeRequestError(error, endpoint) {
  if (!(error instanceof Error)) {
    return "API request failed. Check the endpoint, API key, and browser console.";
  }

  const message = error.message || "API request failed.";

  if (message.includes("Failed to fetch")) {
    const endpointLower = endpoint.toLowerCase();
    if (endpointLower.includes("localhost") || endpointLower.includes("127.0.0.1")) {
      return "Could not reach the local model endpoint. Make sure Ollama is running and that the endpoint is http://localhost:11434/v1/chat/completions.";
    }
    return "The browser could not reach the API endpoint. This is usually CORS, a blocked network request, or an incorrect URL.";
  }

  if (message.includes("401")) {
    return "The API rejected the credentials. Check that the key matches this provider and endpoint.";
  }

  if (message.includes("403")) {
    return "The provider denied access. Check permissions, model access, and endpoint settings.";
  }

  if (message.includes("404")) {
    return "The endpoint or model was not found. Verify the URL and exact model name.";
  }

  if (message.includes("429")) {
    return "The provider accepted the key but refused the request because of rate limits or exhausted quota.";
  }

  if (message.includes("did not contain chat text")) {
    return "The provider responded, but not in the expected OpenAI-compatible chat format.";
  }

  return message;
}

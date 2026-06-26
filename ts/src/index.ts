/**
 * groundedwork — retrieval that knows when it doesn't know.
 *
 * A tiny, dependency-free retrieval layer for giving an LLM a knowledge base
 * bigger than its context window. Keyword (BM25) retrieval into a relevance-
 * floored "working set", with grounding and abstention built in as defaults.
 *
 * This is the TypeScript mirror of the Python reference implementation. Both
 * run the SAME shared fixture (fixtures/nimbus.json), so their behavior is
 * provably identical — same tokenizer, same BM25, same floor, same grounding.
 *
 * Lineage: groundedwork is a from-scratch reimplementation inspired by
 * ContextForge (github.com/Betanu701/ContextForge) by Derek Thomas. The design
 * choices here come from empirically testing that SDK and shipping the lessons
 * as defaults. See README for the evidence.
 */

export const VERSION = "0.1.0";

const STOP = new Set(
  ("a an the is are was were be been do does did of to in on at for and or but with " +
    "from by as this that these those your you we our it its i my me can how what when " +
    "where which will would should could about get got").split(" "),
);

/** Lowercase, split on non-alphanumerics, drop stopwords and 1-char tokens. */
export function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 1 && !STOP.has(w));
}

export interface Doc {
  id: string;
  title: string;
  body: string;
  answer?: string;
  meta?: Record<string, unknown>;
}

export interface Hit {
  doc: Doc;
  score: number;
  matched: string[];
}

export interface Retrieval {
  query: string;
  hits: Hit[];
  terms: string[];
  /** true iff at least one doc cleared the relevance floor. */
  grounded: boolean;
}

export interface PromptPayload {
  system: string;
  knowledge: string;
  user: string;
  grounded: boolean;
  sources: string[];
}

export interface Answer {
  grounded: boolean;
  answer: string;
  source: string | null;
}

/**
 * The grounding instruction that shipped 0/72 hallucinations in our testing,
 * vs 5/72 for a permissive prompt. This is the DEFAULT, not opt-in.
 */
export const GROUNDING_PROMPT =
  "You are a helpful assistant. Answer using ONLY the information in the " +
  "knowledge provided below. If the answer is not contained in it, say you " +
  "do not have that information — do not guess or use outside knowledge.";

export interface Options {
  /** Relevance floor: a query whose best match scores below this returns an
   *  empty, ungrounded result instead of distractors. Default 2.0. */
  minScore?: number;
  /** Max docs in a working set. Default 3. */
  topK?: number;
  k1?: number;
  b?: number;
  systemPrompt?: string;
  /** Stable per-user/persona text, pinned into the cached prefix. Default "". */
  prefs?: string;
}

export class GroundedWork {
  readonly minScore: number;
  readonly topK: number;
  readonly k1: number;
  readonly b: number;
  readonly systemPrompt: string;
  readonly prefs: string;

  private docs: Doc[] = [];
  private tf: Map<string, number>[] = [];
  private len: number[] = [];
  private df = new Map<string, number>();
  private avgdl = 0;

  constructor(opts: Options = {}) {
    this.minScore = opts.minScore ?? 2.0;
    this.topK = opts.topK ?? 3;
    this.k1 = opts.k1 ?? 1.5;
    this.b = opts.b ?? 0.75;
    this.systemPrompt = opts.systemPrompt ?? GROUNDING_PROMPT;
    this.prefs = opts.prefs ?? "";
  }

  /** Add one document. Title is weighted 2x (matches the reference). Chainable. */
  add(doc: Doc): this {
    const toks = tokenize(doc.title + " " + doc.title + " " + doc.body);
    const tf = new Map<string, number>();
    for (const t of toks) tf.set(t, (tf.get(t) ?? 0) + 1);
    this.docs.push(doc);
    this.tf.push(tf);
    this.len.push(toks.length);
    for (const term of tf.keys()) this.df.set(term, (this.df.get(term) ?? 0) + 1);
    this.avgdl = this.len.reduce((a, b) => a + b, 0) / this.len.length;
    return this;
  }

  addMany(docs: Doc[]): this {
    for (const d of docs) this.add(d);
    return this;
  }

  get size(): number {
    return this.docs.length;
  }

  /** Return the relevance-floored working set for a query. */
  retrieve(query: string, topK?: number): Retrieval {
    const k = topK ?? this.topK;
    const terms = tokenize(query);
    const n = this.docs.length;
    if (terms.length === 0 || n === 0) {
      return { query, hits: [], terms, grounded: false };
    }

    const scored: { i: number; score: number; matched: string[] }[] = [];
    for (let i = 0; i < n; i++) {
      const tf = this.tf[i];
      const dl = this.len[i];
      let s = 0;
      const matched: string[] = [];
      for (const t of terms) {
        const f = tf.get(t);
        if (!f) continue;
        const df = this.df.get(t) ?? 0;
        const idf = Math.log(1 + (n - df + 0.5) / (df + 0.5));
        s += (idf * (f * (this.k1 + 1))) / (f + this.k1 * (1 - this.b + (this.b * dl) / (this.avgdl || 1)));
        matched.push(t);
      }
      if (s > 0) scored.push({ i, score: s, matched });
    }

    scored.sort((a, b) => b.score - a.score);
    const hits: Hit[] = scored
      .slice(0, k)
      .filter((x) => x.score >= this.minScore) // the floor
      .map((x) => ({ doc: this.docs[x.i], score: x.score, matched: x.matched }));

    return { query, hits, terms, grounded: hits.length > 0 };
  }

  /** Build the message payload an LLM would receive for this query. */
  prompt(query: string): PromptPayload {
    const r = this.retrieve(query);
    const knowledge = r.hits.map((h) => `### ${h.doc.title}\n${h.doc.body}`).join("\n\n");
    return {
      system: this.systemPrompt,
      knowledge,
      user: query,
      grounded: r.grounded,
      sources: r.hits.map((h) => h.doc.id),
    };
  }

  /** The cache-stable prefix: [system + prefs], assembled identically every call.
   *  Pin this at the front of every request and a prompt-caching endpoint reuses
   *  it across calls. Contains nothing query-dependent, so it never changes. */
  stablePrefix(): string {
    return this.prefs ? `${this.systemPrompt}\n\n${this.prefs}` : this.systemPrompt;
  }

  /** Cache-optimal message assembly: stable prefix first (system), volatile
   *  retrieved knowledge LAST before the user turn — so everything before the
   *  knowledge is byte-identical every call and the prefix cache hits. The
   *  library structures this; measure your hit-rate from the endpoint's usage
   *  metadata (e.g. cache_read_input_tokens), not from here. */
  messages(query: string): {
    messages: { role: "system" | "user"; content: string }[];
    grounded: boolean;
    sources: string[];
    stablePrefix: string;
  } {
    const r = this.retrieve(query);
    const knowledge = r.hits.map((h) => `### ${h.doc.title}\n${h.doc.body}`).join("\n\n");
    const messages: { role: "system" | "user"; content: string }[] = [
      { role: "system", content: this.stablePrefix() },
    ];
    if (knowledge) messages.push({ role: "user", content: `Knowledge:\n${knowledge}` });
    messages.push({ role: "user", content: query });
    return {
      messages,
      grounded: r.grounded,
      sources: r.hits.map((h) => h.doc.id),
      stablePrefix: this.stablePrefix(),
    };
  }

  /** Demo-grade answerer with NO LLM call: canonical answer of the top grounded
   *  hit, or an honest abstention. Real apps pass prompt(query) to their model. */
  ask(query: string): Answer {
    const r = this.retrieve(query);
    if (!r.grounded) {
      return {
        grounded: false,
        answer: "I don't have that in my knowledge base, so I won't guess.",
        source: null,
      };
    }
    const top = r.hits[0].doc;
    return { grounded: true, answer: top.answer || top.body, source: top.id };
  }
}

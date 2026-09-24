# VIRA V2 Root-Cause Analysis — Sam Chatbot (Haiku 4.5)

Scope reviewed: `VIRA.json` (n8n V2 workflow), the AI Agent system prompt, memory + retrieval config, the four "after implementing v2" failure chats, `UAT Cost Claude.xlsx`, and Sam's original (V1) reference replies. This is a targeted root-cause pass, not a full audit.

## Headline

The degradation is **mostly architectural, not the model**. V1 (Sonnet 4.6) was masking three concrete wiring bugs that V2 (Haiku 4.5) exposes. The prompt content is actually well-written; the problem is that it is mis-wired to the tools, the memory key is broken, and the bot runs an agentic tool-call loop that Haiku handles poorly. Swapping back to Sonnet would hide the symptoms again without fixing the causes — and at higher cost.

## Root causes

### RC1 — Prompt instructs tools that aren't wired (the "boros" engine)
**Severity: High · Confidence: 90%**
The agent has only **three** tools attached: `PROGRAM`, `LINKS`, `ABOUT_SAM`. But the system prompt explicitly orders the model to "panggil tool BATCH untuk jadwal, HARGA untuk biaya." Those tools **do not exist** on the agent. So on any price/batch/schedule question the model tries a tool that isn't there, retries, and burns iterations.
Evidence: `UAT Cost Claude.xlsx` rows 7–15 are a running fight with this — "AI belum dpt jawaban dan stop karena max iterations," then bumping max iterations 3 → 6 → 8, still "kena maks iterasi." When the loop fails, the model falls back to memory and invents facts (see RC4). This single defect drives **hallucination, looping, latency, and cost** at once.

### RC2 — Memory key resets every clock hour + 5-message window
**Severity: High · Confidence: 95% (deterministic)**
`Simple Memory` session key = `user_wa + '_' + new Date().getHours()`, with `contextWindowLength` left at the default (5). Two failure modes: the conversation buffer only holds the last 5 turns, **and** it is wiped whenever the server clock crosses an hour boundary. The bot then forgets what was already established.
Evidence: chat **+62 877-8433-6814** ("muter2, kirim link 2x") — grade 9 / Intermediate is established and a GForm link is sent, then the bot re-asks "anaknya sekarang kelas berapa?" and offers to send the registration link **again**. Classic mid-conversation context loss.

### RC3 — Haiku under-follows a 7.5k-char, ~30-negative-constraint prompt
**Severity: High (persona) · Confidence: 80%**
The prompt is dense and almost entirely prohibitions ("DILARANG…", "JANGAN…", hard 1–3 sentence limit, no honorifics, parent vs. student "kamu" rule). Sonnet juggles this; Haiku drops constraints under load.
Evidence: long stiff paragraphs flagged as "kaku" (+62 812-2008-9875); formal non-Sam voice "Saya memahami ketertarikannya terhadap universitas di Hong Kong" (UAT row 29); **internal instructions leaked into the reply** "Ambil data dulu dari FAQ yang sudah ada…" (UAT row 33); and the parent/student referent bug — a parent who said "anak saya" / "orang tua murid" is repeatedly addressed as the student: "kelas kamu berapa," "kamu cocok program Junior" (+62 812-8799-6856).

### RC4 — Hallucination from lexical-only retrieval + no grounded fallback
**Severity: High · Confidence: 80%**
FAQ retrieval is keyword/lexical (stemming + synonym groups), no semantic matching. On a miss, the prompt says output `[UNKNOWN]` — but with the broken tool loop (RC1) the model instead answers from memory.
Evidence: "ada juga yang **partial** atau tidak dapet beasiswa" (+62 812-2008-9875) — there is no partial scholarship; this is invented. The folder names themselves ("salah kasih info," "salah jawabannya," "salah refer") are three independent accuracy failures.

### RC5 — temperature 0.7 on a factual bot
**Severity: Medium · Confidence: 70%**
0.7 is tuned for variety, not for a grounded FAQ/registration bot. It widens output variance, which amplifies RC3 (persona drift) and RC4 (hallucination), and makes Haiku's behavior less repeatable across identical questions (visible in UAT rows 33 vs 35, same question, divergent replies).

## Top 5, ranked by impact
1. **RC1 — mis-wired BATCH/HARGA tools → agent loop** (fixes hallucination + cost + latency)
2. **RC2 — hourly memory reset + tiny window** (fixes "muter-muter," duplicate links, re-asking)
3. **RC4 — lexical retrieval, no grounded fallback** (fixes wrong/invented answers)
4. **RC3 — prompt too dense for Haiku** (fixes persona + length + leakage)
5. **RC5 — temperature 0.7** (cheap multiplier on 3 and 4)

## Direct answers
1. **Is the model the primary problem?** No. Haiku *amplifies* the failures but the same prompt on Sonnet simply hid wiring bugs that are still there.
2. **Is it the architecture?** Yes — largest single share. Tool wiring (RC1) + memory key (RC2) are deterministic defects.
3. **Is it the prompt design?** Partly. The *content* is good; the defect is the prompt referencing tools that don't exist and being too constraint-dense for a small model.
4. **Is it retrieval/context?** Contributing, medium. Lexical-only with no semantic fallback creates the gaps the model then hallucinates into.
5. **Single highest-impact fix:** Stop making the agent decide which tool to call. **Pre-fetch** the relevant PROGRAM/BATCH/HARGA/LINKS/FAQ rows deterministically (the way `faq_context` is already injected) and pass them in the prompt, with tool-calling disabled. This kills the loop, the cost, and most hallucination in one change — and is model-agnostic.

## Diagnosis: combination, weighted
Architecture (agent loop + memory) ≈ 55% · Retrieval ≈ 20% · Model instruction-following ≈ 15% · Prompt/temperature config ≈ 10%. Not primarily a model-capacity problem.

## QUICK WINS (< 1 day)
- **Fix the memory key** to `user_wa` only (drop `getHours()`); raise `contextWindowLength` to ~15. (RC2)
- **Lower temperature to 0.2–0.3.** (RC5)
- **Either wire the missing `BATCH` and `HARGA` tools, or remove those instructions** from the prompt so the model stops calling phantom tools. (RC1)
- **Harden the fallback:** if retrieval/tools return nothing, force `[UNKNOWN]` rather than letting the model free-write. (RC4)
- **Raise output cap** (`maxTokensToSample` 512) only if truncation appears; current short-answer goal makes this low priority.

## MEDIUM (1–3 days)
- **Replace the agentic tool loop with deterministic pre-retrieval** — assemble PROGRAM/BATCH/HARGA/LINKS/FAQ context before the LLM call; disable in-agent tool calls. (RC1, RC4)
- **Split the mega-prompt:** a short always-on persona core, plus only the rule block relevant to the detected intent (price / batch / status). Easier for Haiku to obey. (RC3)
- **Add the missing FAQ rows** flagged in the chats (partial-scholarship clarification, kelas-10 path, MTL requirement) — several failures were genuine content gaps. (RC4)

## LONG-TERM
- **Semantic retrieval** (embeddings) over the FAQ/knowledge base to replace lexical keyword matching. (RC4)
- **Confidence-based model routing:** Haiku by default, escalate to Sonnet only on `[UNKNOWN]`, multi-intent, or low-confidence turns. (cost vs. quality)
- **Regression eval set** built from these failure chats, run on every prompt/model change to prevent re-introducing the same bugs.

## Decision matrix
| Option | Est. cost impact | Est. quality impact | Risk |
|---|---|---|---|
| Keep V2 as-is | Baseline (but loops inflate it) | Poor — persona, accuracy, UX failures persist | High (reputational) |
| Improve V2 architecture | **↓ 30–50%** (loop removed) | **↑ High** — fixes RC1/2/4/5 | Low–Med |
| Switch back to Sonnet 4.6 | ↑ 4–6× per chat | ↑ Medium (hides, not fixes, bugs) | Med (cost + bugs remain) |
| Hybrid Haiku + Sonnet routing | ↑ 10–25% over fixed-Haiku | ↑ High | Med (routing complexity) |

## FINAL VERDICT
**Most likely root cause:** an agentic architecture that asks Haiku to call tools that don't exist (RC1) on top of a memory key that wipes context hourly (RC2). These are wiring defects, not model limitations.

**Is Haiku 4.5 viable here?** Yes. Once tool-calling is replaced with deterministic pre-retrieval, temperature is lowered, and the prompt is slimmed, this FAQ/registration use case is well within Haiku's range — at a fraction of Sonnet's cost.

**Is Sonnet 4.6 actually necessary?** No — not as the default. Reserve it as a fallback for low-confidence or multi-intent turns only.

**Architecture I would deploy:** detect intent + status deterministically → pre-fetch the exact PROGRAM/BATCH/HARGA/LINKS/FAQ rows into the prompt (no agent tool loop) → single Haiku call at temp 0.25 with a slimmed, intent-scoped prompt → durable per-user memory (15-turn window, no hourly reset) → hard `[UNKNOWN]` fallback → Sonnet escalation only when confidence is low.

**Single highest quality-per-dollar recommendation:** Replace the agent's tool-calling loop with deterministic context pre-injection. It removes the cost-burning iteration loops *and* eliminates most hallucination and "muter-muter" behavior in one change — keeping Haiku's price while delivering Sonnet-level reliability on this narrow task.

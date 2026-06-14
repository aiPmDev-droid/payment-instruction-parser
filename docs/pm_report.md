# Payment Instruction Parser — AI Product Report

## 1. One-Page Case Study (Portfolio Ready)

### Problem
Finance teams at companies like Visa receive hundreds of payment instructions daily through messy email threads, forwarded invoices, and informal chat messages. Accounts payable staff manually read each email, identify the vendor, amount, due date, and payment method, then enter them into a payment system. This process is slow, error-prone, and scales poorly as transaction volume grows.

### Solution
**Payment Instruction Parser** is an internal finance tool that accepts raw `.txt` and `.eml` email uploads and extracts structured payment instructions using Google Gemini's structured output mode. Each extraction returns vendor, amount, currency, due date, payment method, confidence score, a supporting text excerpt, and reviewer notes. Results are stored in PostgreSQL for audit history and review.

The system uses a **three-layer architecture**:
| Layer | Technology | Role |
|-------|-----------|------|
| Frontend | Next.js + Streamlit | File upload, extraction view, history table |
| API | FastAPI | File handling, orchestration, persistence |
| Extraction | Google Gemini | Unstructured → structured JSON |
| Storage | PostgreSQL (Neon) | Persistent audit trail |

### Product Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| **AI over regex** | Vendor names, dates, and payment methods appear in too many formats for regex to cover reliably. AI handles ambiguity, relative dates ("end of month"), and multiple invoices per email. |
| **Structured Outputs** | Forces the model to return valid JSON matching a strict schema. Eliminates parsing errors from freeform text. |
| **Confidence + Excerpt** | Every extraction includes a confidence score and raw text excerpt. This lets reviewers verify the model's work without re-reading the entire email. |
| **FastAPI (not a monolith)** | Clean API boundary makes it easy to swap the extraction provider or add validation middleware without touching the UI or storage layer. |

### Impact
The tool reduces manual data entry for accounts payable by converting minutes of reading and typing into seconds of review. For emails containing multiple payment requests — a common case in consolidated vendor communications — it catches instructions that might otherwise be missed. The structured history enables querying payment volume, tracking extraction accuracy over time, and flagging suspicious changes.

### Key Metrics (Projected)
- Extraction time per email: **2–5 seconds** (vs 2–5 minutes manually)
- Multi-payment capture: emails with 2+ invoices extracted correctly
- Confidence threshold: configurable, operators review anything below 0.85

---

## 2. Tradeoffs: AI Extraction vs Regex

### Accuracy

| Scenario | AI (Gemini) | Regex |
|----------|-------------|-------|
| `"Please ACH $4,820.75 to Brightline Supply for invoice B-8812 due June 28"` | ✅ Correctly extracts vendor, amount, method, date | ⚠️ Needs patterns for "ACH to X for invoice Y due Z" |
| `"Net 15 from 06/10"` | ✅ Interprets as 15 days from June 10 | ❌ Hard to express relative dates in regex |
| `"Wire transfer to Atlas Freight — no rush date given"` | ✅ Returns date as null with note | ⚠️ Might miss that "no date" is intentional vs missing |
| `"Pay $950 by 7/5 via check"` (currency implied) | ✅ Assumes USD, notes it in notes field | ❌ No currency inference |
| `"Invoice #442 — $3,200 overdue — please pay immediately"` | ✅ Extracts amount, high urgency noted | ⚠️ "Overdue" is hard to interpret as a due date signal |

**Verdict:** AI wins on recall and flexibility. Regex wins only when the email format is known and rigid.

### Maintainability

| Aspect | AI | Regex |
|--------|-----|-------|
| Adding a field | Update the JSON schema + prompt | Add a new pattern for every variation |
| New email format | Handled naturally by the model | Write and test new regex rules |
| Debugging failures | Add examples to the prompt, check model response | Trace which pattern didn't match |
| Non-engineer review | Prompt and schema can be reviewed | Complex patterns are hard to audit |
| Regression risk | Low — model generalizes | High — new patterns can break old matches |

**Verdict:** AI is dramatically cheaper to maintain. Regex complexity grows linearly with the number of email formats.

### Edge Cases

| Edge Case | AI | Regex |
|-----------|-----|-------|
| Multiple invoices per email | Extracts each one as a separate payment object | Needs separate capture groups per invoice |
| Forwarded email chain with mixed content | Models handle conversational text well | Patterns break on forwarded headers |
| Multilingual payment terms (Spanish, French) | Gemini handles common languages | Requires per-language patterns |
| Ambiguous dates ("06/07" = June 7 or July 6?) | Returns the most likely with a note | Returns whatever the pattern matches |
| Omitted currency (implied USD) | Detects and assumes USD with note | Can't infer — returns null or wrong |
| Invoice attachments referenced but not included | Notes the gap in notes field | Can't detect absence |

**Verdict:** AI handles edge cases more gracefully. The cost is that errors are "softer" (wrong but plausible) rather than "hard" (missing/null).

### Cost

| Factor | AI (Gemini 2.5 Flash) | Regex |
|--------|----------------------|-------|
| Per-email cost | ~$0.001–0.005 (token-based) | ~$0.000001 (compute only) |
| Latency | 1–3 seconds per email | <100ms |
| Development time | Hours (schema + prompt) | Days to weeks (pattern engineering) |
| Maintenance cost | Low (model improves) | High (new patterns for every edge case) |

**Verdict:** AI has higher per-transaction cost but lower total cost for messy inputs. For a finance team processing 500 emails/month, the AI cost is ~$1–2.50/month — negligible compared to the time saved.

### Recommendation: Hybrid Pipeline

>The practical answer is **not "AI or regex" — it's "AI with regex guardrails."**

| Stage | Approach | Why |
|-------|----------|-----|
| Pre-validation | Regex | Validate file type, check for obvious format errors before calling the API |
| Primary extraction | Gemini | Handle messy text, multiple invoices, implied fields |
| Post-processing | Regex | Normalize dates to ISO format, validate confidence, remove duplicates |
| Reviewer queue | Human | Confidence < 0.85 or missing "due_date" → flagged for manual review |

This hybrid approach gives the best of both: AI's flexibility for extraction, regex's determinism for validation, and human judgment for edge cases.

---

## 3. PM Signal: When Does AI Fail vs Regex? (Interview Answer)

### The PM Interview Question
> *"You're building a financial extraction tool. When would you choose AI over regex, and what are the risks?"*

### The Short Answer
Choose AI when the input is **unstructured, variable, or ambiguous**, and you can tolerate **soft errors** (wrong but plausible outputs). Choose regex when the input is **rigidly formatted** and errors must be **deterministic** (null or correct — nothing in between).

### When AI Fails (And Why It Matters in Finance)

**1. Hallucinated vendors or amounts**  
If the email mentions "please pay the usual amount to the usual vendor," a model might guess the vendor and amount from context. This is **dangerous in finance** — a hallucinated payment of $48,000 to a wrong vendor could be costly.  
**Mitigation in this app:** The `confidence` field, `raw_text_excerpt` (showing exactly what the model based its answer on), and reviewer notes all flag this.

**2. Over-inference from weak signals**  
An email saying "Invoice 101 is late, please expedite" might cause the model to infer a due date of "today" even when none was explicitly stated.  
**Mitigation:** The prompt instructs the model to use `null` for missing fields. The post-processing layer also strips any inferred dates that don't match explicit patterns.

**3. Currency ambiguity in global finance**  
A dollar amount could be USD, CAD, AUD, or HKD. The model assumes USD by default in US contexts, but for a global payment workflow, this could cause underpayment.  
**Mitigation:** The schema includes a `currency` field. For production, the prompt should be region-aware, or a second pass should validate currency against vendor location.

**4. Multi-invoice splitting errors**  
An email listing 5 invoices on one line ("Invoices 101-105 total $12,400") could be interpreted as one payment or five. The model might split them correctly or merge them incorrectly.  
**Mitigation:** Each extraction is an independent object. Reviewers can see the source excerpt and decide.

### When Regex Fails (And Why That Can Be Worse)

**1. Brittleness under real-world conditions**  
A regex that works on a clean invoice email breaks when the email is forwarded three times, has "FW:" in the subject, includes a signature block with phone numbers that look like dollar amounts, or has HTML formatting.

**2. Silent misses**  
A regex pattern that doesn't match yields a null value — but the operator doesn't know if the value is genuinely missing or the regex just failed. This creates **false negatives** that are invisible.

**3. Impossible variation**  
Expressions like "end of month following invoice date," "net 30 from receipt," or "due upon receipt" would each require a separate regex rule. The complexity grows exponentially.

### The PM Decision Framework

| Input characteristic | Choose | Risk to manage |
|---------------------|--------|----------------|
| Fixed format, known template | **Regex** | Brittle to format changes |
| Freeform email, conversational | **AI** | Hallucination, over-inference |
| Mixed (some structured, some not) | **Hybrid** | Integration complexity |
| High volume, low value per item | **Regex** | Cost per extraction |
| Low volume, high value per item | **AI with human review** | Manual review bottleneck |

### Finance-Specific Recommendation

> *For a production payment extraction system at scale, the safest architecture is: **AI for extraction → regex for validation → human for exceptions**.*

This maps to three tiers of trust:

| Trust Tier | Approach | Action |
|------------|----------|--------|
| High confidence (≥0.9, all fields populated) | Auto-approve | No review needed |
| Medium confidence (0.7–0.9 or missing optional field) | Flag for quick review | Operator confirms |
| Low confidence (<0.7 or missing required field) | Manual entry | Operator keys in data |
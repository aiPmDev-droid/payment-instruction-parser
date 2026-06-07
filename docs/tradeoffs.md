# ChatGPT vs Regex Tradeoffs

## Accuracy

ChatGPT with Structured Outputs is better for messy payment emails because vendors, dates, amounts, and payment methods appear in inconsistent forms. It can interpret phrases like "Net 15 from 06/10/2026" or "end of month" more naturally than regex.

Regex is accurate when formats are predictable, such as `Amount due: $1,200.00` or `Due: 2026-07-01`. It degrades quickly when emails are forwarded, informal, multilingual, or contain several invoices.

## Maintainability

The model approach centralizes complexity in a schema and prompt. Adding fields like `currency` or `confidence` is mostly a schema change.

Regex requires separate patterns for every wording variation. Each new edge case can add brittle logic that is difficult for non-engineers to review.

## Edge Cases

ChatGPT handles ambiguity better, but it can still infer too much if the prompt is loose. This project reduces that risk by requiring strict JSON, source excerpts, confidence, and reviewer notes.

Regex is transparent and cheap, but struggles with relative dates, multiple payments, implied currencies, and payment methods described indirectly.

## Cost

Regex has near-zero marginal cost and is fast. ChatGPT adds API cost and latency per email. For a finance workflow, the higher cost can be justified when it reduces manual review time and improves coverage of messy inputs.

## Recommendation

Use ChatGPT for primary extraction and reserve regex for pre-validation, obvious normalizations, and post-processing checks. The practical product decision is not "AI or regex"; it is a hybrid pipeline with model extraction plus deterministic validation.

# Manual Retrieval Test Cases

Run these questions through the assistant after copying `docs/` into `src/docs/` and rebuilding the index. Source paths below assume the application is started from `src/`.

The `Primary signal` column describes what the case is designed to exercise, not the only retrieval method that may find the answer.

| ID | Question | Expected source | Expected answer fact | Primary signal |
| --- | --- | --- | --- | --- |
| T01 | How much paid holiday does a permanent employee get? | `docs/vacation-policy.md` | 24 working days per calendar year | Semantic/paraphrase |
| T02 | What is HR-LV-204? | `docs/vacation-policy.md` | Vacation and personal leave policy | Exact term/BM25 |
| T03 | Can I work from Spain for a month? | `docs/remote-work.md` | No more than 20 calendar days per year, subject to three approvals | Semantic retrieval |
| T04 | Which day must everyone come to the office? | `docs/remote-work.md` | Tuesday, unless an exception is approved | Semantic retrieval |
| T05 | What is the recovery deadline under RTO-17? | `docs/incident-response.md` | Core transaction processing within 45 minutes | Exact acronym/BM25 |
| T06 | How do I open the most severe production incident? | `docs/incident-response.md` | `opsctl incident declare --severity p1` | Query expansion + hybrid |
| T07 | How do I undo a broken production release? | `docs/deployment-guide.md` | Use `deployctl rollback --service <service-name> --to <release-id>` | Query expansion (`undo` → `rollback`) |
| T08 | Where is the Payments API deployment manifest? | `docs/deployment-guide.md` | `services/payments/config.py` | Filename/path/BM25 |
| T09 | How can I renew my ZETA device credential? | `docs/security-policy.md` | `vpnctl rotate-key --device <device-id>` | Query expansion + exact command |
| T10 | Can secrets be stored in config.py? | `docs/security-policy.md` | No; secrets belong in Blackbox Vault | Hybrid and cross-document discrimination |
| T11 | How long are login security records kept? | `docs/data-retention.md` | Authentication audit logs: 400 days | Paraphrase + precise fact |
| T12 | Is business class allowed on a five-hour flight? | `docs/expense-policy.md` | Only with vice-president approval; normal rule is economy under six hours | Semantic retrieval |
| T13 | What is the maximum hotel rate in Paris? | `docs/expense-policy.md` | EUR 190 per night, excluding local taxes | Exact fact |
| T14 | What is the office Wi-Fi password? | None | The knowledge base does not contain this information | Missing-information behavior |
| T15 | Who founded Northstar Labs? | None | The knowledge base does not contain this information | Missing-information behavior |

## Suggested comparison

For each question, record whether the expected source appears in the returned Top-K contexts. If the implementation exposes branch diagnostics, also record whether the source was found by vector search, BM25, or both.

Use the same documents, `TOP_K`, embedding model, and questions when comparing vector-only retrieval with hybrid retrieval. Do not infer an improvement from one or two selected examples; report the number of successful cases out of all answerable cases (T01–T13).


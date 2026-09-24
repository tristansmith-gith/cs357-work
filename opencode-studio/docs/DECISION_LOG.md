# Decision Log

<!-- The running record of decisions actually taken (RFCs are for proposals; this log
     is for outcomes). Append-only. Future contributors should understand why the
     project evolved as it did. -->

## 2026-09-24: Canvas To-Do section is authoritative; activity-stream fallback rejected

- **Decision:** Use the Canvas To-Do section as the authoritative source for assignment data rather than using Canvas activity-stream entries as a fallback.
- **Rationale:** The activity-stream entries can indicate that an assignment's due date changed, but they do not reliably provide the actual new due date or points value. Using them as a fallback could therefore produce false additions/removals or other incorrect change reports. This decision follows the charter value of correctness over speed.
- **Alternatives considered:** Use Canvas activity-stream entries as a fallback when an assignment is not found in the To-Do section. Rejected because a stream row records the change event (the change timestamp), not the assignment's resolved due date or points, so a stream-derived record can never produce a correct positive change — only a no-op, a false "assignment removed" (the stream is a rolling window), or a mislabeled "assignment added".
- **Long-term implications:** The parser is committed to the To-Do sidebar as its only record source (decision D9); activity-stream rows must never be parsed into records. Extending the parser beyond To-Do scope requires a new decision entry here.

<!-- For projects inheriting prior work (human or AI), also keep a forensics table
     treat inherited work as archaeology to re-verify, never as authority:

| Finding | Evidence | Confidence | Action |
|---|---|---|---|
| <claim about the prior work> | <artifact/log/commit> | high/med/low | <re-verify / use / discard> |
-->

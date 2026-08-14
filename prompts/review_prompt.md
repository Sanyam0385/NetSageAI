# Human Review Prompt

Review the AI diagnosis before any lab fix is accepted.

Return one of:

- `Accepted`: root cause and fix are supported by evidence.
- `Edited`: diagnosis is partly useful but needs correction.
- `Rejected`: diagnosis is not supported by the evidence or could cause harm.

Checklist:

- Does the AI cite actual symptom or show-command evidence?
- Does the OSI layer match the failure?
- Is the next command useful and safe?
- Are fix steps specific enough for Packet Tracer or Cisco IOS?
- Is there a safer explanation with stronger evidence?

Log any correction in `outputs/responsible_ai_log.csv`.

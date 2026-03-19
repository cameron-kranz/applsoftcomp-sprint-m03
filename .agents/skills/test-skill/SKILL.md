---
name: test-skill
description: Test-drive a skill by spawning one sub-agent per test case in PRD.md. Each sub-agent executes the skill for its assigned input and judges the output against the expected result.
---

Invocation: `Test skill [SKILL-NAME]` — reads `PRD.md` in the current working dir.

Shared files: `test_results.txt` (one entry per case), `test_log.txt` (actual outputs + failure notes).

## Lead Agent (loop controller)

1. Read `PRD.md` → extract every test case. For each, append to `test_results.txt`:
   `[ ] Task <N> / Case <M>: <one-line description> | input: <input> | expected: <expected>`
2. Spawn one Tester Sub-Agent per test case in parallel via Task tool. Pass each sub-agent: skill name, skill path, task N, case M, the exact input, and the expected output.
3. Wait for all. Read `test_results.txt`. Print summary: `N passed, M failed`.
4. If any failures: spawn Advisor Sub-Agent once. Wait. Then stop.

## Sub-Agents (spawned via Task tool, `general` / `mode: subagent`)

**Tester** (parallelizable, once per test case — do NOT use Task tool):
1. Read `SKILL.md` of the target skill. Understand its inputs, outputs, and steps.
2. Execute the skill for the assigned input: follow the skill's steps directly, run any tools it requires. Do not skip steps.
3. Compare actual output to expected output. Judge: PASS if output satisfies the spec; FAIL otherwise.
4. Mark result in `test_results.txt` (replace `[ ]` with `[PASS]` or `[FAIL] <reason>`).
5. Append to `test_log.txt`: `--- Task <N> / Case <M> ---\nActual: <output>\nVerdict: PASS|FAIL\nNotes: <notes>`.
6. Stop.

**Advisor** (once, only if failures exist):
1. Read `PRD.md`, `test_results.txt`, `test_log.txt`.
2. For each FAIL: identify root cause (wrong output format, missing step, bad tool usage, etc.).
3. Append `## Fix Recommendations` to `test_log.txt` with one concrete suggestion per failure.
4. Stop.

## Stop Conditions
- All test cases evaluated + summary printed (+ advisor done if needed)
- Sub-agent fails 3× on same case → mark `[ERROR]`, continue to next
- User cancels

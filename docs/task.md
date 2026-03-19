# Your Task: Build a Personalized Assistant

Design and build an AI assistant that makes *your* life or work easier. The assistant must learn your preferences over time and improve through your feedback.

## What to Build

Pick an assistant that solves a real problem for you. Some ideas:

| Idea | What it does |
|---|---|
| **Literature Assistant** | Given a research question, searches and summarizes relevant papers using the [OpenAlex CLI](https://github.com/alejandroschuler/openalex) |
| **Personalized News Briefing** | Fetches today's news and delivers a briefing in the tone, style, and focus areas you specify |
| **Research Idea Generator** | Reads your notes/papers and proposes new research directions aligned with your interests |
| **Meeting Prep Assistant** | Given a meeting agenda and context, drafts talking points and questions in your voice |
| **Anything else** | It just has to be useful to *you* |

The assistant should improve the more you use it: when you give feedback ("be more concise", "focus on methods, not results"), the assistant remembers and applies it next time.

---

## Requirements

Your `SKILL.md` must implement all three context engineering primitives:

### 1. Write — persist state
The assistant must save data to files. Examples:
- A preferences file (`preferences.md`) that stores your feedback and style instructions
- A history file that logs past queries and responses
- A memory file that accumulates domain knowledge across sessions

### 2. Select — retrieve relevant context
The assistant must selectively pull in context rather than dumping everything into every prompt. Examples:
- Retrieve relevant past notes or papers before answering
- Query an external API or dataset (e.g., OpenAlex for papers, a news API for headlines)
- Search the web for current information

### 3. Isolate — use sub-agents
The assistant must delegate subtasks to isolated sub-agents via the Task tool. Examples:
- One sub-agent fetches/searches; another synthesizes
- One sub-agent reads your preferences and plans; another executes
- Parallel sub-agents handle independent pieces of a request

---

## Steps

### Step 1: Vibe

Build a rough prototype with no planning. Goal: get a feel for what is hard. The output will be messy. That is intentional.

> [!TIP]
> Instruct agents to make an atomic commit with a clear message after each task. The git log becomes a second-brain of the agent, recording what was done, when, and why. It also lets you roll back easily if something goes wrong.

### Step 2: Plan

Create a clear, unambiguous specification. Every ambiguity becomes a silent decision the agent makes during implementation—usually wrong.

Discard the prototype. Open a fresh session (`/new`).

Paste this prompt (replace `[ASSISTANT]` and `[ASSISTANT-NAME]`):

```
I want to build a personalized AI assistant called [ASSISTANT] under .agents/skills/[ASSISTANT-NAME].
Interview me RELENTLESSLY until nothing is ambiguous.
Ask one question at a time. Cover: what the assistant does, how it learns my preferences,
how users give feedback, inputs, outputs, edge cases, tools, and output format.
Then write PRD.md with overview and each task as a subsection:

## Task <N>: <name>
- Goal:
- Inputs:
- Outputs:
- Specification 1:
- Specification 2:
```

**Output:** `PRD.md`

git commit `PRD.md`.

---

### Step 3: Test Design

Build tests before implementing. Tests create a feedback loop so agents can learn from their mistakes without human intervention.

Open a fresh session.

Paste this prompt:

```
Read PRD.md.

For each task, propose test cases covering: happy path, edge cases, bad inputs,
and failure modes. Each test case must include an explicit input and expected output.

Show me the tests for one task at a time and ask for my approval before moving on.
Refine any test I reject before proceeding.

Once all tests are approved, add them to each task's subsection in PRD.md.
```

**Output:** `PRD.md` (updated with test cases)

git commit the updated `PRD.md`.

---

### Step 4: Implement (Ralph Wiggum Pattern)

Write a prompt to implement the plan using the Ralph Wiggum loop. Your `SKILL.md` must:

1. Spawn a fresh sub-agent for each task via the Task tool (no memory of previous agents)
2. Specify shared files for inter-agent communication (e.g., `preferences.md`, `progress.txt`, `learning.txt`)
3. Define the Lead Agent loop: when to spawn, when to wait, when to stop
4. Define Sub-Agent steps: how it reads preferences, how it fetches/retrieves context, what it produces, how it verifies against `PRD.md` tests, what it writes back, and how it stops after one task
5. Define stop conditions and what happens on repeated failure

See [`.agents/skills/literature-review/SKILL.md`](../.agents/skills/literature-review/SKILL.md) for an example of the full pattern.

> [!NOTE]
> **Ralph Wiggum Pattern:**
> - **Lead Agent:** a loop controller. Initializes shared files on first run, spawns one sub-agent per task via the Task tool, waits, then repeats until done.
> - **Sub-Agent:** spawned fresh each time. No memory of previous agents. Its prompt must be fully self-contained.
> - **Shared files:** the only memory between agents. Typically `progress.txt` (what is done), `learning.txt` (lessons learned), and `preferences.md` (user preferences).

---

### Step 5: Teach It Your Preferences

Run your assistant on at least three different inputs. After each run, give it feedback:

```
I didn't like [X]. Next time, [Y].
Tell me what you've learned about my preferences.
```

Verify that the assistant:
- Saves your feedback to `preferences.md` (or equivalent)
- Applies it on the next run without you repeating yourself

---

## Validation

Run your skill on the tests you designed. Fix the skill until you are satisfied.

> [!TIP]
> Shorter instructions are better—for the agent and for you. If `SKILL.md` exceeds ~150 lines, create templates or tools to offload parts of the process.
>
> Allowing `Sacrifice grammar` in writing instructions is effective for conciseness. Agents follow grammar rules too strictly, leading to unnecessary verbosity. Explicitly permitting grammar sacrifices encourages tighter, more task-oriented output.

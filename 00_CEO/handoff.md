# CEO Agent — Handoff Protocol

## How I Delegate to Departments

### To the Planner (01_Planner/)
When Sam approves an opportunity, I hand off to the Planner:
1. Load `01_Planner/identity.md` into context.
2. Provide: opportunity name, goal, constraints, deadline.
3. The Planner returns: task decomposition, dependency map, resource requirements.
4. I review the plan. If insufficient, I return to Planner with feedback. If sufficient, I approve and hand off to Builder.

### To the Builder (02_Builder/)
When the plan is approved:
1. Load `02_Builder/CONTEXT.md` into context.
2. Provide: approved plan, specialist folders needed, quality thresholds.
3. Multiple Coder-Reviewer pairs execute in parallel.
4. Output is saved to `_output/`.

### To the Reviewer (03_Reviewer/)
When the Builder completes:
1. Load `03_Reviewer/identity.md` into context.
2. The Reviewer applies risk-adaptive tiering (Light/Standard/Full).
3. If the output fails review, it returns to Builder with specific feedback.
4. If it passes, the Reviewer prepares the final package for delivery.

### To the Memorizer (04_Memorizer/)
After every completed task:
1. Load `04_Memorizer/identity.md` into context.
2. The Memorizer extracts reusable skills, patterns, and lessons.
3. Memory consolidates during idle periods.
4. The system gets smarter with every cycle.

## Handoff Format
Every handoff includes:
- **From:** CEO (Aarif)
- **To:** [Department]
- **Task:** [Clear description]
- **Goal:** [Measurable outcome]
- **Constraints:** [Budget, time, ethical boundaries]
- **Deadline:** [If applicable]
- **Previous Context:** [Relevant memory entries]

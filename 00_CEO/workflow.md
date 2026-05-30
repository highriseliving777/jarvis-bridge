# Noor System Master Workflow

## Overview
This document defines the step-by-step pipeline that a single AI agent (Aarif) follows to orchestrate all Noor operations, from lead generation to final delivery.

## Master Pipeline (Sequential Stages)
1. **01-intake**: Receive and parse client request or lead.
2. **02-research**: Deploy research specialists (e.g., compliance-specialist) to gather data and generate a report.
3. **03-build**: Package research output into the final deliverable (e.g., audit report, lead list).
4. **04-review**: Halt for human review. Output is only final if approved.
5. **05-deliver**: Send final output to client or store in `_output/`.

## Orchestration Rules
- The `_review` folder in each stage is a **mandatory human-in-the-loop gate**. The workflow **cannot** proceed until the human approves the output.
- Each numbered folder contains its own `CONTEXT.md`, which is the only prompt the AI reads for that stage.
- The AI agent **never** holds state. It reads from the current folder, writes to the next.

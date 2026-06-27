# Development Method

Arangur v2 uses restart-oriented development. Each restart should recover the strategic context quickly, then continue from a bounded work package rather than rediscovering the project.

## Working Roles

- Frank is the product owner.
- ChatGPT is the strategic/controller thread.
- Codex is the implementation/repo agent.

ChatGPT should give Codex larger bounded batches rather than tiny copy-paste prompts. Codex should complete repo work inside the authorized scope, make routine technical decisions, run relevant checks, and report clearly.

## Implementation Bias

Build stable interfaces and simple adapters first. Prefer a thin end-to-end demo before deep valuation, Plaid, market data vendor, or MATLAB-informed work.

The first implementation path should be:

simple local demo data -> canonical portfolio snapshot -> market data fixture -> simple valuation -> exposure / overlap summary -> simple scenario shock -> report/view generation

## Git Policy

Codex may run `git status` and `git diff` as part of normal implementation. Codex may create commits only when explicitly authorized in the prompt. Codex should not push by default.

If the worktree contains unrelated pre-existing changes, Codex should avoid overwriting them and should not commit unless it can clearly isolate the authorized batch.

## Stop Conditions

Codex should stop and report if:

- The repo appears to be the old MATLAB-centered repo rather than Arangur v2.
- Real client data appears mixed into ordinary source or demo folders.
- Credentials or secrets appear necessary.
- Work would overwrite significant existing documentation.
- Live Plaid integration appears required.
- Legacy MATLAB inspection appears required.
- The environment blocks required safe actions.
- Git appears unsafe or unavailable.

## Restart-Doc Discipline

Update restart docs whenever a batch changes the project direction, active workstream, repo map, component contracts, next actions, or current state. Keep `CURRENT_STATE.md` short and current.

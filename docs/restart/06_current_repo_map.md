# Current Repo Map

Observed on 2026-06-27.

## Top-Level Folders

- `.codex_work/`: Local Codex scratch space. Ignored by git. Active only for temporary implementation notes or generated scratch output.
- `.dispatcher_tmp/`: Temporary dispatcher output. Ignored by git. Do not rely on it for project state.
- `.git/`: Git metadata.
- `.test_work_root/`: Temporary test work root. Ignored by git.
- `data/`: Project data area. Currently contains `data/demo/` for synthetic demo fixtures.
- `docs/`: Project documentation. Currently the main active area.
- `reports/`: Generated report output. Currently contains `reports/demo/` for demo report packages.
- `src/`: Future source code. Placeholder until the system skeleton batch.
- `tests/`: Future test code. Placeholder until implementation begins.

## Top-Level Files

- `.gitignore`: Ignore rules for temp output, secrets, client data, Python cache files, and OS metadata.
- `README.md`: Short repo identity and restart-doc pointer.

## Active Areas

- `docs/restart/`: Active restart documentation and current-state files.

## Placeholder Areas

- `docs/architecture/`: Future architecture notes that are not part of the ordered restart set.
- `docs/contracts/`: Future detailed schemas and interface contracts.
- `docs/decisions/`: Future durable decision records if the decision log outgrows restart docs.
- `docs/demo/`: Future demo walkthroughs, acceptance examples, and sample outputs.
- `data/demo/`: Future synthetic demo input fixtures.
- `reports/demo/`: Future generated advisor-readable demo reports.
- `src/`: Future application/package code.
- `tests/`: Future automated tests.

## Output Locations

- Demo data should go under `data/demo/`.
- Generated demo reports should go under `reports/demo/`.
- Tests should go under `tests/`.
- Temporary Codex work should go under `.codex_work/`.
- Dispatcher and test scratch output should go under `.dispatcher_tmp/` and `.test_work_root/`.

## Restricted Or Sensitive Areas

Do not inspect or modify `client_data/`, `confidential/`, `secrets/`, `credentials/`, `.env`, `.env.*`, private keys, auth tokens, or real client files without explicit authorization.

Do not inspect, port, or modify legacy MATLAB content unless a specific MATLAB audit batch is authorized.

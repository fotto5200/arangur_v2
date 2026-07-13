# Private Demo Deployment Readiness v1

Audit date: 2026-07-12
Audited commit: `3f9c40b7c66b636bc9db3dbeb24668fa900e9536`
Branch: `master`

## 1. Executive readiness verdict

**Verdict: ready with prerequisites.** The repository builds and runs as a self-contained Docker Compose private demo, packages the accepted advisor UI and all four built-in briefing templates, and passes container, API, browser, and restart checks. It is not ready to expose to colleagues until a private-access mechanism is selected and enforced. The current `DEMO_ADMIN_TOKEN` setting is not authorization: it is parsed and reported as configured, but no route checks it.

The deployment tranche must also make explicit choices about Developer/QA exposure, browser-local persistence, the hostname/TLS path, secret provisioning, and Postgres backup/retention. This audit does not deploy or mutate any external system.

## 2. Current accepted UI model

The advisor entry experience is **Briefing Templates** plus **Generated Reports**. There is no separate conversation object.

- Built-in and custom templates coexist in one list.
- The built-ins are Principal Briefing, Engaged Client Review, Advisor Oversight, and External Manager Story Translation.
- Built-ins can be opened as working copies, duplicated, and saved under new names, but cannot be overwritten or deleted.
- Generated Reports are browser-saved populated artifacts. They open directly to rendered content, support Previous/Next and `Report N of M`, and reopen from a separate list.
- Builder, narrative elements, named workflows, print/export, report storage, and Developer/QA controls remain present.

## 3. Current private-demo architecture

- `docker-compose.yml` defines `app` and `postgres` services plus the named volume `arangur_postgres_data`.
- `Dockerfile` builds from `python:3.12-slim`, installs `requirements.txt`, copies the repository build context to `/app`, and starts Uvicorn for `arangur.app.main:app` on `0.0.0.0:8000` inside the container.
- Compose now publishes the app only on host loopback at `127.0.0.1:8000`; Postgres has no published host port.
- FastAPI serves the advisor HTML from `src/arangur/app/static/index.html`, mounts `reports/demo` at `/reports/demo`, and mounts `data/simulation` at `/simulation`.
- Postgres stores workflow-run metadata, artifact metadata, events, briefing spec sets, and briefing spec items. It does not store the accepted Generated Reports shelf or named browser templates.
- The app has no WebSocket dependency and makes no external API calls in this flow.

## 4. Deployable entry path

The canonical advisor entry path is `/app/`. `/` and `/app/index.html` currently serve the same HTML. The deployment should proxy the application at the origin root, not under an additional path prefix, unless root-path support is separately implemented and tested.

## 5. Built-in template packaging findings

All four built-in workflow JSON files are tracked under `data/simulation/report_workflows/demo_workflows_v1/`. `src/arangur/app/advisor_workflows.py` loads them from the project root, normalizes them to `arangur.local_briefing_spec_set.v1`, and resolves preview content only from:

- `docs/product/report_mockups`
- `data/simulation/external_story_translation`

The Docker build context includes those directories, `data/simulation/report_element_views`, and the advisor static HTML. `.dockerignore` does not exclude `data/`, `docs/`, `reports/`, or `src/`; it excludes local environments, caches, Git metadata, and `.env.*` except the sanitized example.

Container inspection confirmed all four workflow files, report mockups, external-story artifacts, report-element views, and static UI exist below `/app`. No repository mount is used. Paths are repository-relative and resolve correctly in Linux. No absolute Windows path or case mismatch was found in the built-in generation path. Browser generation succeeded for all four built-ins from the container.

The generator allowlists built-in source files by resolved parent directory and permits only `.md` and `.json`. Missing or invalid catalog content degrades to unavailable templates rather than exposing a filesystem path.

## 6. Generated-report packaging and persistence findings

`POST /api/generated-reports/demo-populate` validates a browser workflow payload and returns one `generated_report_artifact.v1` object. Report IDs include report type, workflow identity, data date, and a per-request identifier, so repeated generation creates distinct records. The server does not save these artifacts.

The browser wraps returned artifacts in `arangur.local_generated_reports.v1` and stores the shelf in browser `localStorage`. Opening and navigation are entirely from that browser artifact. Invalid stored records without a supported schema, report ID, or ordered sections are ignored. The API returns bounded structured errors for malformed requests. The generation path reads only known analytic views or catalog sources resolved through the built-in allowlist; it does not accept an arbitrary file path.

Observed persistence:

| Event | Accepted Generated Reports |
| --- | --- |
| Browser refresh | Persists in the same browser profile and origin |
| App process/container restart | Persists in the same browser profile and origin |
| Compose down/up | Persists in the same browser profile and origin |
| Container rebuild | Persists in the same browser profile and origin |
| Host restart | Expected to persist if the browser profile and origin are unchanged; not server-backed |
| New browser/device/profile | Does not appear |
| Browser storage clearing/private-session end | Does not persist |
| Hostname/origin change | Does not appear under the new origin |
| Redeployment | Persists only for a returning browser at the same origin with intact local storage |

There is user-driven per-report deletion and a clear-all control; no automatic retention or cleanup policy exists.

Separately, `/api/runs` can generate file-backed workflow artifacts below `/app/reports/demo`. Those files live in the app container and are lost when the container is recreated because no artifact volume is mounted. Postgres metadata can outlive the corresponding files. This Developer/QA workflow-run path is not the accepted Generated Reports shelf, but it must be disabled/protected or given an explicit artifact-volume decision before external use.

## 7. Custom-template persistence findings

Named custom templates and duplicates use `localStorage` schema `arangur.local_named_briefing_workflows.v1`. The browser-local template survives refresh, Compose down/up, and a rebuilt app container when the same browser profile and origin are retained. It is not stored in Postgres, synchronized across colleagues, or recoverable from another browser. Local JSON copy/download/restore is the manual transfer path.

The optional `/api/briefing-spec-sets` controls persist draft spec sets in Postgres, but they are secondary Developer/QA controls and do not populate the ordinary named Briefing Templates shelf. Postgres records survived Compose down/up and rebuild through `arangur_postgres_data`.

## 8. Authentication and private-access findings

No authentication or authorization is enforced. This applies to:

- `/`, `/app/`, and `/app/index.html`
- briefing-template and generated-report APIs
- briefing-spec-set create/list/read/delete APIs
- workflow-run create/list/detail APIs
- report-element APIs
- `/simulation` and `/reports/demo` static content
- Developer/QA controls
- `/docs` and `/openapi.json`

`DEMO_ADMIN_TOKEN` is read in `settings.py`; `/api/health` reports only whether it is configured. Supplying it does not protect a route. CORS is an origin policy for browsers, not access control. Missing credentials therefore do not prevent startup or access.

`/api/health` is intentionally reachable for Docker health checks and currently discloses app environment, runtime mode, database engine, and configuration booleans, but not values. Decide whether an edge proxy may expose a reduced health path or restrict it to localhost/monitoring.

**Blocking prerequisite:** select and enforce a colleague-facing private-access mechanism before any public-IP exposure. Acceptable mechanisms must be chosen by Frank/ops and may include an authenticated edge proxy, VPN/private network, identity-aware proxy, or a bounded application-auth tranche. Do not treat an unimplemented token variable, CORS, an unlisted hostname, or Cloudflare DNS alone as authentication.

## 9. Developer/QA exposure findings

Developer/QA is visible as a collapsed advisor-home disclosure and a builder section. It provides:

- QA preview links into `/simulation`;
- local workflow JSON copy, download, and restore;
- backend draft save/load controls;
- Generated Reports clear-all;
- access to the full builder and synthetic diagnostics.

The backing APIs also expose run metadata with repository-relative artifact paths and allow workflow creation and draft deletion. OpenAPI documentation exposes all API shapes. There is no environment flag that hides or disables these features.

Recommendation for `Private Demo Colleague Deployment v1`: hide Developer/QA from colleague navigation and deny or separately protect its mutation, artifact, documentation, and broad static routes. Preserve the code for internal use. Frank must decide whether named internal testers receive a separately protected Developer/QA path; hiding navigation alone is insufficient.

## 10. Sanitized environment-variable inventory

| Variable | Purpose and reader | Required/current default | Secret | AWS/Lightsail requirement and absence behavior |
| --- | --- | --- | --- | --- |
| `APP_ENV` | Runtime label; `settings.py` | Optional; `local` | No | Set `private_demo`. Absence starts local mode. It does not enforce security. |
| `PUBLIC_ORIGIN` | Canonical-origin setting; `settings.py` | Optional; unset | No | Supply the final HTTPS origin. Currently read but not used to construct URLs or enforce host/proxy behavior. |
| `ALLOWED_ORIGINS` | CORS allowlist; `settings.py`, `main.py` | Optional; empty | No | Set the exact final HTTPS origin. Absence omits CORS middleware; same-origin UI still works. |
| `DEMO_ADMIN_TOKEN` | Reserved demo-token setting; `settings.py` | Optional; unset | Yes | Do not rely on it until enforcement exists. Absence and presence currently leave all routes open. |
| `DB_ENGINE` | Persistence selector; `settings.py`, `persistence.py` | Optional; `none` | No | Set `postgres` for Compose persistence. `none` makes backend draft persistence unavailable and workflow runs file-scanned. |
| `DATABASE_URL` | Psycopg connection string; `settings.py`, `persistence.py` | Required when `DB_ENGINE=postgres` | Yes | Supply through host secret provisioning. Missing in Postgres mode causes startup schema initialization to fail. |
| `POSTGRES_DB` | Compose Postgres database name | Optional demo default | No | Supply an approved private-demo value. |
| `POSTGRES_USER` | Compose Postgres user | Optional demo default | No | Supply an approved least-privilege demo value. |
| `POSTGRES_PASSWORD` | Compose Postgres password and URL component | Optional unsafe demo default | Yes | Must be replaced and supplied without committing it. Compose defaults are not deployment credentials. |
| `BASE_URL` | Local smoke-script target; `private_demo_smoke.cmd` | Optional; `http://127.0.0.1:8000` | No | Set only when running smoke against another approved origin. |
| `CSRF_SECRET` | Mentioned in the old stack plan only | Not read by code | Yes | Do not provision as if effective. Required only if a chosen cookie/session design implements and reads it. |

Dockerfile-fixed non-secret process settings are `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, and `PYTHONPATH=/app/src`. There is no implemented environment variable for host binding, container port, root path, trusted hosts, proxy trust, logging policy, Developer/QA visibility, generated-report storage, named-template storage, or file-artifact storage.

Do not print or commit supplied values. `.env.private-demo` is Git-ignored and Docker-ignored; `.env.private-demo.example` contains demo-only placeholders.

## 11. Network, port, proxy, hostname, and HTTPS assumptions

- Uvicorn binds `0.0.0.0:8000` inside the app container; Compose publishes only `127.0.0.1:8000` on the host.
- Postgres is internal to the Compose network on port 5432 and is not host-published.
- The browser UI uses root-relative URLs and works behind an origin-root reverse proxy.
- No application root-path/subpath support is configured.
- No `TrustedHostMiddleware` is configured.
- No explicit forwarded-header trust, proxy allowlist, or canonical redirect is configured. Validate the chosen proxy's `Host` and `X-Forwarded-*` behavior.
- HTTPS must terminate at the approved reverse proxy or private-access edge. The app container itself serves HTTP.
- CORS permits only configured exact origins and credentials; an unlisted Origin receives no `Access-Control-Allow-Origin` header.
- No WebSockets are used.
- The current local defaults assume `127.0.0.1`, `localhost`, port 8000, direct HTTP, and root-path hosting. Replace browser origins with the approved HTTPS origin for deployment.

## 12. Synthetic-data and content-safety review

Tracked workflow inputs and generated artifacts are marked synthetic. No live market source, external API, account connection, or real client input is used. A tracked-secret pattern scan found no credential material; the local environment file remains ignored and was absent from the image.

Generated-report requests cannot select arbitrary source files. Built-in previews resolve only `.md`/`.json` files under two allowlisted repository directories, and traversal attempts against mounted static roots returned 404. Default FastAPI debug is off; malformed generated-report requests returned structured errors without stack traces.

The two broad static mounts are directory-root boundaries, not per-file deployment allowlists. Any known file under `data/simulation` or `reports/demo` may be requested. All current content is synthetic, but these routes and `/api/runs` should be protected or disabled for colleagues. Run-detail APIs can expose repository-relative paths.

The External Manager Story Translation generated output was corrected during this audit to visibly retain all existing governance caveats: translation rather than endorsement, synthetic, unverified, not a recommendation, candidate proxies require approval, and production-client use requires review.

Advisor policy attribution and manager mandate attribution remain separate. No revaluation, scenario, attribution, or report analytics were changed.

## 13. Containerized validation results

- Clean Compose down/build/up: passed.
- App and Postgres health checks: passed.
- Standard smoke script: 6/6 passed before and after the readiness fix.
- Container package inspection: all four workflow files, report mockups, external-story pack, report-element views, and static UI present; `.env.private-demo` absent.
- All four built-ins generated rendered report 1 from the container. Gated content remained a restrained unavailable section.
- Duplicate, rename, built-in/custom coexistence, direct report opening, Previous/Next, `Report N of M`, generated shelf, and reopening: passed.
- External-story governance caveats: all six required concepts visible after the bounded fix.
- Browser console errors: none.
- Unauthenticated route probe: advisor, run, static preview, docs, and OpenAPI surfaces reachable, confirming the access-control prerequisite.
- Traversal probe outside `/simulation` and `/reports/demo`: 404.

## 14. Restart-persistence test results

A built-in was duplicated and renamed `Deployment Restart Test Template`; generated outputs for the four built-ins were created. Before restart, the UI showed four built-ins, the renamed custom template, and six generated reports. After Compose down/up, the same browser showed the same custom template and six reports. After a clean image rebuild, the same state remained. Postgres-backed briefing spec records also remained in the named volume.

This verifies same-browser/same-origin persistence, not shared server persistence. A new browser or changed hostname will not inherit the named templates or Generated Reports shelf.

## 15. Blocking issues

1. No enforced authentication or authorization exists for any route.
2. Frank/ops must authorize the Lightsail, private-access, reverse-proxy, DNS/TLS, and firewall/security-group scope before external mutation.
3. Real deployment secrets and a safe Postgres password/URL must be provisioned outside Git.
4. Developer/QA, `/api/runs`, broad static mounts, `/docs`, and `/openapi.json` need an explicit exposure decision and enforcement.
5. Frank must accept browser-local, per-origin persistence for named templates and Generated Reports or authorize a separate persistence design tranche. A substantial redesign is not part of deployment.

## 16. Non-blocking risks

- `PUBLIC_ORIGIN` is informational today; trusted-host and proxy behavior are not explicit.
- Container images use mutable tags and the app container runs as its default root user.
- No rate limiting, resource limits, centralized audit log, automated backup, or retention policy is configured.
- Postgres health verifies server readiness, while app health reports configuration rather than a live query.
- Browser-local shelves can be cleared by the user/browser and are not shared.
- `/api/runs` files are not volume-backed; retained Postgres metadata can become stale after recreation.
- Repeated smoke seeds accumulate Postgres demo spec records; there is no automatic cleanup policy.
- Health returns environment/configuration labels; decide the externally visible response.

## 17. Explicit accepted-demo limitations

- Synthetic/demo data only; not investment advice or production-client reporting.
- Browser-local named templates and Generated Reports are per browser/profile/origin.
- No multi-user identity, role model, or shared report library.
- No production compliance, disaster-recovery, backup, or retention claim.
- Gated report sections remain unavailable rather than fabricated.
- Candidate proxies are unapproved and require review.
- File-backed Developer/QA workflow artifacts are ephemeral across app-container recreation.

## 18. Decisions required from Frank

1. Choose the colleague private-access mechanism and who administers access.
2. Decide whether access is edge-only, application-enforced, or both.
3. Decide whether Developer/QA is disabled externally or separately protected for named testers.
4. Accept per-browser template/report persistence for this demo or schedule a separate server-persistence tranche.
5. Choose AWS account/region, Lightsail instance, approved operator, and backup/retention expectations.
6. Choose hostname and whether Cloudflare is in scope; authorize DNS and TLS ownership.
7. Decide whether `/api/health`, `/docs`, `/openapi.json`, `/simulation`, `/reports/demo`, and `/api/runs` are externally reachable.
8. Approve the Postgres secret-provisioning and backup process.
9. Approve rollback retention and maximum acceptable downtime.

## 19. Exact proposed scope: `Private Demo Colleague Deployment v1`

Prerequisites are the decisions above, a clean reviewed commit, named operators, approved AWS/DNS/private-access authorization, and provisioned secrets. The bounded tranche may:

- prepare one approved Lightsail Ubuntu host;
- install the approved Docker/Compose runtime;
- deploy this repository commit or a reviewed successor;
- provision `.env.private-demo` values without committing or logging secrets;
- retain the Postgres named volume and establish the approved backup procedure;
- configure the chosen private-access control;
- hide/deny or separately protect Developer/QA and technical routes as decided;
- configure a reverse proxy to host loopback port 8000, preserve host/proto, and terminate HTTPS;
- create only the specifically approved DNS/TLS records or certificates;
- run health, smoke, browser, colleague acceptance, and restart checks;
- roll back to the prior image/commit and retained volume on trigger.

It must not introduce real client/live data, analytics changes, attribution changes, a persistence redesign, a database service beyond current Postgres, broad UI changes, unrelated cleanup, or unapproved cloud/DNS/TLS mutations.

## 20. Deployment verification checklist

- [ ] Approved commit and image identity recorded.
- [ ] All prerequisites and Frank decisions recorded.
- [ ] Secrets supplied outside Git and redacted from logs.
- [ ] Port 8000 reachable only through the intended local proxy path.
- [ ] Postgres not publicly published.
- [ ] Private access denies an unauthenticated browser.
- [ ] Authorized colleague can open `/app/`.
- [ ] Exactly four built-ins load.
- [ ] Duplicate, rename, and built-in/custom coexistence work.
- [ ] All four built-ins generate rendered outputs or gated disclosures.
- [ ] External-story caveats are visible.
- [ ] Previous/Next, `Report N of M`, shelf, and reopening work.
- [ ] Developer/QA exposure matches the approved decision.
- [ ] Technical/static/API routes match the approved access policy.
- [ ] CORS, hostname, proxy headers, and HTTPS are correct.
- [ ] Restart preserves Postgres and same-browser shelves.
- [ ] No browser console errors or server stack traces.
- [ ] Rollback and shutdown commands are tested.

## 21. Rollback plan

Record the prior Git commit/image and take the approved Postgres-volume backup before deployment. On a rollback trigger, stop the new Compose stack, restore the prior reviewed repository/image and unchanged environment contract, restore the Postgres volume only if a data rollback is explicitly approved, start the prior stack, and rerun health, smoke, advisor browser, and private-access checks. Browser-local shelves are not centrally restorable; changing the origin may make them appear absent even when still present under the old origin.

Do not delete the named volume during ordinary rollback. `scripts\private_demo_down.cmd --reset` is destructive and is not a deployment rollback command.

## 22. Shutdown and recovery plan

Normal local shutdown:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_down.cmd
```

Recovery starts from an approved host/repository state, intact environment values, and the retained Postgres volume. Always shut down before startup:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
docker compose --env-file .env.private-demo down
docker compose --env-file .env.private-demo up --build
```

Then run:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_smoke.cmd
```

If recovery changes hostname/origin, disclose that browser-local templates and reports will not automatically appear. Never use `--reset` unless destructive Postgres-volume deletion is separately approved.

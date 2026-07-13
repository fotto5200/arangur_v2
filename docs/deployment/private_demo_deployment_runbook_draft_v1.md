# Private Demo Deployment Runbook Draft v1

Status: draft plan only. This document is not authorization to deploy or mutate AWS, Lightsail, Cloudflare, DNS, TLS, firewall, or any remote host.

Proposed tranche: `Private Demo Colleague Deployment v1`
Advisor entry path: `/app/`

## 1. Repository preparation

Prerequisites:

- Frank has approved the access, persistence, Developer/QA, hostname, DNS/TLS, backup, and operator decisions listed in `private_demo_deployment_readiness_v1.md`.
- The approved commit is recorded as `<APPROVED_COMMIT>`.
- The worktree is clean and tests pass.
- No real client data or real secret is present in Git or the Docker context.

Local verification uses Windows Command Prompt syntax:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
git status -sb
git rev-parse HEAD
python -m unittest discover -s tests
git diff --check
```

Do not push from this audit. A later authorized deployment tranche must define the approved release-transfer method: `<REPOSITORY_CHECKOUT_OR_RELEASE_ARTIFACT_METHOD>`.

## 2. Remote host preparation

External authorization required: AWS account `<AWS_ACCOUNT>`, region `<AWS_REGION>`, Lightsail instance `<LIGHTSAIL_INSTANCE>`, operator `<OPERATOR>`, and approved network policy `<NETWORK_POLICY>`.

Prepare one approved Ubuntu host with supported Docker Engine and Compose plugin versions. Record OS, Docker, Compose, instance plan, disk size, public/private addressing, time zone, and patch baseline. Do not invent or publish the IP. Do not expose Postgres. Restrict administrative access to the approved operators and method `<ADMIN_ACCESS_METHOD>`.

## 3. Container/runtime preparation

Deploy the approved repository commit to `<REMOTE_APP_DIRECTORY>`. Confirm the Docker build context contains the four workflow JSON files, report mockups, external-story pack, report-element views, and static UI. Confirm `.env.private-demo` is absent from the image.

The app listens on container port 8000. Compose publishes host `127.0.0.1:8000` only. Postgres remains on the internal Compose network. Do not change this to a public host binding.

Record image identity and base-image resolution. If immutable digests are required, schedule a bounded repository hardening change and retest before deployment.

## 4. Environment and secret provisioning

Provision environment values outside Git at `<REMOTE_ENV_PATH>` with owner-only permissions. Never print them into task logs.

Required deployment values:

- `APP_ENV=private_demo`
- `PUBLIC_ORIGIN=https://<APPROVED_HOSTNAME>`
- `ALLOWED_ORIGINS=https://<APPROVED_HOSTNAME>`
- `DB_ENGINE=postgres`
- `POSTGRES_DB=<APPROVED_DATABASE_NAME>`
- `POSTGRES_USER=<APPROVED_DATABASE_USER>`
- `POSTGRES_PASSWORD=<SECRET>`
- `DATABASE_URL=<SECRET_POSTGRES_URL_USING_SERVICE_NAME_POSTGRES>`

`DEMO_ADMIN_TOKEN` is not currently enforced and must not be represented as protection. Provision it only if an approved repository change adds and tests enforcement. `CSRF_SECRET` is not currently read; provision it only if the selected authenticated session design implements it.

Verify secrets are absent from Git status, image layers, browser responses, health output, and logs.

## 5. Persistence setup

Retain the Compose named volume `arangur_postgres_data`. Define `<BACKUP_METHOD>`, `<BACKUP_LOCATION>`, `<RETENTION>`, `<RESTORE_OWNER>`, and `<RESTORE_TEST_DATE>` before colleague use.

Explicitly record the accepted persistence model:

- named custom templates: browser-local, per profile/origin;
- accepted Generated Reports: browser-local, per profile/origin;
- briefing spec drafts and workflow metadata: Postgres;
- `/api/runs` report files: app-container filesystem unless a separately approved artifact-volume change is made.

If Frank requires shared templates/reports or centralized recovery, stop and create a separate persistence-design tranche. Do not add a database or object store during deployment.

## 6. Private-access setup

Decision placeholder: `<APPROVED_PRIVATE_ACCESS_MECHANISM>`.

Acceptance requirements:

- unauthenticated clients cannot reach advisor, API, static preview, report artifact, Developer/QA, OpenAPI, or mutation surfaces;
- authorized colleagues can reach `/app/` without credentials in URLs;
- access logs do not contain secrets;
- logout/revocation behavior is documented;
- health exposure follows `<HEALTH_ACCESS_POLICY>`;
- CORS is not treated as authentication.

If the selected mechanism requires repository authentication changes, implement them in a bounded reviewed change before deployment and test every route group. Do not silently rely on `DEMO_ADMIN_TOKEN`.

## 7. Developer/QA exposure configuration

Decision placeholder: `<DISABLE_EXTERNALLY_OR_SEPARATELY_PROTECT>`.

Recommended default: hide Developer/QA navigation for colleagues and deny its APIs/static routes at the authenticated edge, while preserving internal access for named testers only if approved. Include `/api/runs`, briefing-spec mutation endpoints, `/reports/demo`, broad `/simulation` access, `/docs`, and `/openapi.json` in the route decision. Navigation hiding alone is not enforcement.

If no repository flag exists for the approved policy, make the smallest bounded configuration/route change and add tests before deployment.

## 8. Reverse proxy

Approved proxy: `<REVERSE_PROXY>`.

Configure it to:

- terminate HTTPS;
- proxy the origin root to `127.0.0.1:8000`;
- preserve the approved `Host` and scheme headers;
- apply the selected private-access policy before forwarding;
- prevent direct public access to port 8000;
- set request/time limits appropriate for the synthetic demo;
- avoid exposing Postgres;
- apply the approved technical-route policy.

Validate forwarded-header trust and hostname handling. The app currently has no TrustedHost middleware, explicit proxy trust list, or root-path configuration.

## 9. DNS and TLS

External authorization required: DNS provider `<DNS_PROVIDER>`, zone `<DNS_ZONE>`, hostname `<APPROVED_HOSTNAME>`, record owner `<DNS_OWNER>`, and TLS owner/method `<TLS_METHOD>`.

Create only the approved record and certificate after authorization. Do not invent IPs, hostnames, account identifiers, or credentials. Confirm the final HTTPS origin exactly matches `PUBLIC_ORIGIN` and `ALLOWED_ORIGINS`. Record renewal and revocation ownership.

## 10. Deployment

Preconditions: approved commit, clean tests, secrets provisioned, volume/backup ready, private access active, reverse proxy ready, and rollback artifact recorded.

On the local repository, the validated sequence is always shutdown first:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
docker compose --env-file .env.private-demo down
docker compose --env-file .env.private-demo up --build
```

For the remote host, use the equivalent approved operator procedure at `<REMOTE_APP_DIRECTORY>` without printing secrets. Record deployment timestamp, commit, image identity, database volume identity, operator, and change authorization `<CHANGE_ID>`.

## 11. Smoke verification

Local reference smoke:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_smoke.cmd
```

Remote smoke uses `BASE_URL=https://<APPROVED_HOSTNAME>` only from an authorized client and must verify private-access denial first. Verify health, `/app/`, report elements, exactly four built-ins, briefing-spec persistence if enabled, and no secret-bearing response. Add authenticated headers/cookies according to the selected mechanism without echoing them.

## 12. Colleague acceptance test

With synthetic data only, an authorized colleague must verify:

1. `/app/` opens to Briefing Templates and Generated Reports.
2. Exactly four built-ins appear.
3. A built-in can be duplicated and renamed; the original stays unchanged.
4. Custom and built-in templates coexist.
5. Each built-in generates rendered report content or a clear gated disclosure.
6. External Manager Story Translation shows all governance caveats.
7. Previous/Next and `Report N of M` work.
8. Generated Reports lists the output and reopening opens report 1 directly.
9. Print/export and builder/narrative flows work.
10. Developer/QA exposure matches the approved policy.
11. No material browser-console error occurs.
12. An unauthorized client is denied.

## 13. Restart verification

Before restart, create a uniquely named custom template and generated report and record only their non-sensitive display names. Perform the approved normal Compose stop/start without deleting volumes. From the same browser and origin, confirm both browser-local records remain and Postgres-backed draft metadata remains. From a second clean browser, confirm browser-local records are absent by design.

Repeat after the approved image update/rebuild. If the hostname changes, treat missing local shelves as an origin-migration limitation, not proof of server data loss.

## 14. Rollback

Rollback triggers:

- private-access bypass;
- secret exposure;
- health or smoke failure;
- missing built-ins or packaged artifacts;
- broken generation/reopening/navigation;
- unexpected loss/corruption of Postgres data;
- material browser/server errors;
- Developer/QA exposure outside the approved policy.

Stop the new stack, restore `<PRIOR_APPROVED_COMMIT_OR_IMAGE>`, retain the current Postgres volume unless an explicit data restore is authorized, start the prior stack, and rerun access, smoke, browser, and restart checks. Record the incident and state. Do not use `down -v` or the reset helper as rollback.

## 15. Shutdown

Local reference:

```cmd
cd /d C:\Users\fotto\cursor\arangur_v2
scripts\private_demo_down.cmd
```

The remote operator must use the equivalent non-destructive Compose shutdown at `<REMOTE_APP_DIRECTORY>`, verify containers and the proxy route are stopped as intended, retain the Postgres volume, and record the shutdown. DNS removal or instance deletion requires separate authorization.

## 16. Recovery

Recovery prerequisites: approved commit/image, intact environment secret source, retained or restored Postgres volume, proxy/private-access configuration, DNS/TLS state, and named operator.

Restore the host/runtime, deploy the approved image, attach the retained/restored volume, restore environment values without logging them, start behind the private-access proxy, and run smoke plus colleague acceptance. Document that browser-local shelves require the same browser profile and origin and cannot be centrally restored.

If recovery requires a different hostname, communicate the browser-origin limitation before cutover. Do not copy browser storage, invent a migration, or redesign persistence in the recovery event.

## 17. What remains forbidden

This runbook does not authorize real client data, live market or account data, external APIs, analytics/attribution/revaluation changes, a new database, persistence redesign, broad Docker restructuring, broad UI redesign, unapproved AWS/Lightsail/Cloudflare/DNS/TLS/firewall changes, credential creation or rotation outside the approved process, unrelated cleanup, or Git push.

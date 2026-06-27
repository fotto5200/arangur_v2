# Plaid-Shaped Mock Ingestion Contract

## Purpose

The Plaid-shaped mock ingestion contract defines a local synthetic fixture that resembles Plaid Investments data at a high level and normalizes into the existing `CanonicalPortfolioSnapshot` contract.

This is not live Plaid integration. It does not use Plaid APIs, Plaid Link, OAuth, access tokens, item IDs, credentials, real account data, or real client data.

## Mock Fixture

Current fixture:

- `data/demo/plaid_mock_investments.json`

The fixture is intentionally synthetic and local. It exists to prove that Arangur v2 can support more than one ingestion shape without changing downstream valuation, exposure, scenario, or report components.

## Represented Mock Fields

The fixture includes:

- `metadata`: dataset ID, valuation date, reporting currency, synthetic-data flag, advisor labels, and caveats.
- `item`: mock institution/import metadata.
- `accounts`: Plaid-like account records with balances and Arangur demo mapping hints.
- `securities`: Plaid-like security records plus canonical identifiers and classification tags.
- `holdings`: account/security/quantity rows similar to investment holdings.
- `cash_balances`: explicit synthetic cash balances.
- `investment_transactions`: optional mock investment transaction examples.

## Canonical Mapping

The mock adapter maps:

- Plaid-like accounts -> canonical accounts.
- Arangur account mapping hints -> canonical managers and account types.
- Plaid-like securities -> canonical securities.
- Plaid-like holdings -> canonical holdings.
- Cash balances -> canonical cash balances.
- Investment transactions -> optional canonical transactions.

The adapter sets canonical source metadata to `adapter: plaid_mock` and preserves Plaid-shaped source identifiers in `source_ref` objects.

## Deliberately Not Represented Yet

The mock fixture does not represent:

- Plaid Link.
- OAuth.
- Access tokens.
- Real item IDs.
- Real account numbers.
- Live Plaid API payloads.
- Multi-currency.
- Options, shorts, derivatives, margin, corporate actions, fees, taxes, or full accounting.
- Production-grade reconciliation or data cleansing.

## Future Plaid Sandbox Adapter

A future Plaid Sandbox adapter would need to add:

- Secure secret handling outside committed files.
- Plaid Sandbox account connection flow.
- Real Plaid API request/response handling.
- Mapping from Plaid-provided identifiers and security metadata into the canonical model.
- Error handling for missing/partial Plaid fields.
- Reconciliation between Plaid balances, holdings, cash, prices, and Arangur market data.
- Tests that do not require committed credentials or real client data.

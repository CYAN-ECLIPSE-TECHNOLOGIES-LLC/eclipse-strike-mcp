# Eclipse Strike MCP

**Powered by Cyan Eclipse Technologies** — https://cetech.ai

**Eclipse Strike — the Coinbase exchange adapter: the price at which a trade executes, normalized into the suite's one book.**

## Wrap posture — read this before expecting account tools

Coinbase ships **three official MCPs** of its own (spec §10.1): a remote **Coinbase MCP** for account trading, a **Wallet MCP** (self-custody — the DeFi suite's concern, not this one's), and a **CDP MCP** for builders. Strike does not re-implement any of them.

- **Strike at M0 is the public-DATA adapter**: a thin client over Coinbase's public market-data shapes — products and level-2 books — deterministic, cacheable, and requiring **no account session**. Suite T0 should never need the owner's credentials.
- **Account paths are M1+, and they are a governed WRAP of the vendor's account MCP** — subsetting, drift-halt, receipts (the Orbit precedent) — fronted by the Book core's placement gate. They are not in this build.
- **One chapter, one upstream**: Strike's capability record names exactly the public data surface. Tools arriving from the vendor's account/wallet/CDP surfaces are out-of-scope here and refused; `venue_status` states `account_surface: ABSENT — M1+ governed wrap` on every call.

So: **no account tools exist in this build** — no balances, no orders, no transfers, no key management. The denylist (`account_get`, `accounts_list`, `balance_get`, `place_order`, `withdraw`, `create_api_key`, …) is stated in code and refused by name (`-32602`).

## Status — honest labels

v0.1.0, phase **M0 (public-data adapter)**. Local stdio transport, Python stdlib only. Reads run against **fixtures shaped like the real Coinbase public product/book responses**, behind a transport seam (`load_fixtures()`); live public reads are a later verification step, labeled `not_tested` in the manifest. **No accounts, no keys, no network calls, and no certification claimed — bench pending.** Own suites: 8/8 tests + stdio smoke passing.

## What it does

- **Products → canonical Instruments**: Coinbase product ids become Book-core SPOT instruments. A native status the core vocabulary doesn't map (the fixture's `pending_review`) surfaces as **`UNMAPPED`** with the native string preserved — never coerced (spec §5.2).
- **Level-2 books → canonical Books**: the `[price, size, orders]` arrays translate through the **same core builder** Forecast's CLOB parser uses. Cross-adapter parity — same logical book in, same canonical book and quote math out, modulo venue fields — is a tested property of the suite, not an aspiration.
- **Quotes with fee truth**: all-in buy/sell cost from Coinbase's dated fee schedule (account-specific tiers supersede the public schedule at M1 and will be labeled as such). A stale schedule degrades the quote to `FEE_UNVERIFIED` (§5.3).

## Tools (6)

`product_list` · `product_get` · `book_get` · `quote_get` · `venue_status` · `receipt_list`

Spec: `~/workspace/cyan-eclipse/eclipse-markets-suite-spec-20261025.md` (§10.1). Suite core: Eclipse Book. Derivatives and Coinbase's equities surface are out of the v1 scope (§8.1; equities live in the Tape chapter). This is data and tooling, **not financial advice**.

A Cyan Eclipse Technologies product. The "Powered by Cyan Eclipse Technologies" attribution travels with it.

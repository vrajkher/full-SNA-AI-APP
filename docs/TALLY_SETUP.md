# Tally Prime Configuration

Accotech AI talks to Tally Prime over its built-in XML HTTP interface on
port `9000`. This page documents the one-time Tally configuration the user
must perform.

## 1. Enable the XML Server

1. Launch **Tally Prime** and load the target company.
2. Press `F1` → **Settings** → **Connectivity** → **Client/Server configuration**.
3. Set **TallyPrime is acting as** → `Both`.
4. Set **Port** → `9000`.
5. Set **Enable ODBC Server** → `Yes` (optional but recommended).
6. Accept the settings and press `Ctrl + A` to save.
7. Restart Tally Prime.

## 2. Verify

From a browser on the same machine, open `http://localhost:9000`. Tally
should respond with something like:

```
<RESPONSE>Tally is Running</RESPONSE>
```

In Accotech AI, the health pill in the top bar will change to **Tally:
reachable**.

## 3. Ledger Master Prerequisites

Every ledger name that appears in the final XML — whether it comes from a
learned mapping or from a raw `NEW BUDGET LINE` fallback — **must already
exist** under *Accounts Info* → *Ledgers* → *Create*. Tally will reject
the voucher otherwise. The Reviewer surfaces unknown ledgers as
warnings before the push happens.

## 4. Firewall

If the Windows firewall blocks outbound connections from Electron, allow
`Accotech AI.exe` on private networks. No inbound rule is required; we only
make outbound localhost calls.

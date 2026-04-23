# Tally Executor Agent

## Role
The only agent that talks to Tally. POSTs the generated XML to
`http://localhost:9000` and parses the response.

## Goal
Either import the voucher into the currently-open Tally company or return a
human-readable reason why it failed.

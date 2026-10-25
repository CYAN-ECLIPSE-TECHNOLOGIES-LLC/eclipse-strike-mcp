#!/usr/bin/env python3
"""End-to-end stdio smoke for Eclipse Strike v0.1 (M0).

Temp shared Book state. Drives initialize -> product_list ->
product_get (DOGE: UNMAPPED native status preserved) ->
quote_get (BTC all-in math) -> venue_status (account ABSENT).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
AS_OF = "2026-10-25T13:00:00Z"


def rpc(proc, rid, method, params=None):
    req = {"jsonrpc": "2.0", "id": rid, "method": method,
           "params": params or {}}
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def call(proc, rid, name, args):
    response = rpc(proc, rid, "tools/call",
                   {"name": name, "arguments": args})
    return json.loads(response["result"]["content"][0]["text"])


def main():
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["ECLIPSE_BOOK_STATE"] = str(Path(tmp) / "state.json")
        proc = subprocess.Popen(
            [sys.executable, str(HERE / "server.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
            cwd=str(HERE), env=env)
        try:
            init = rpc(proc, 1, "initialize",
                       {"protocolVersion": "2025-03-26"})
            assert init["result"]["serverInfo"]["name"] == "eclipse-strike"
            print("initialize OK")

            products = call(proc, 2, "product_list", {})
            assert products["count"] == 3, products
            print("product_list OK; 3 fixture products")

            doge = call(proc, 3, "product_get", {
                "instrument_id": "A:coinbase:DOGE-USD"})["product"]
            assert doge["status"] == "UNMAPPED", doge
            assert doge["native_status"] == "pending_review"
            print("product_get OK; DOGE native status UNMAPPED, preserved")

            q = call(proc, 4, "quote_get", {
                "instrument_id": "A:coinbase:BTC-USD", "size": "0.5",
                "as_of": AS_OF})["quote"]
            assert q["bid"] == "65430" and q["ask"] == "65432.1", q
            assert q["all_in_buy_cost"]["total"] == "32912.3463", q
            print("quote_get OK; BTC all-in buy 32912.3463 for 0.5")

            status = call(proc, 5, "venue_status", {"as_of": AS_OF})
            assert status["account_surface"].startswith("ABSENT")
            print("venue_status OK; account surface ABSENT at M0")
            print("SMOKE PASSED")
        finally:
            proc.stdin.close()
            proc.terminate()


if __name__ == "__main__":
    main()

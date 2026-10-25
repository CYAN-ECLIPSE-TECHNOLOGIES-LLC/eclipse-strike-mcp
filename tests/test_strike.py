"""Eclipse Strike v0.1 tests — Coinbase-shaped fixture
translation, canonical normalization + quote math, UNMAPPED
native status (spec 5.2), fee truth + staleness (5.3),
probability law, and the absent account surface (denylist,
spec 10.1)."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent.parent
CORE = HERE.parent / "eclipse-book-mcp"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(HERE))

import book_engine as eng  # noqa: E402
import server as srv  # noqa: E402

AS_OF = "2026-10-25T13:00:00Z"
BTC = "A:coinbase:BTC-USD"
DOGE = "A:coinbase:DOGE-USD"


def synced_state():
    state = eng.empty_state()
    seed = __import__("json").loads(
        (CORE / "fixtures.json").read_text())
    eng.ensure_seeded(state, seed)
    srv._sync(state)
    return state


class TestProducts(unittest.TestCase):
    def test_products_sync_and_status_mapping(self):
        state = synced_state()
        out = srv.t_product_list(state, {})
        self.assertEqual(out["count"], 3)
        btc = srv.t_product_get(state, {"instrument_id": BTC})
        self.assertEqual(btc["product"]["status"], "OPEN")
        self.assertEqual(btc["product"]["kind"], "SPOT")

    def test_unmapped_native_status_preserved(self):
        state = synced_state()
        doge = srv.t_product_get(state, {"instrument_id": DOGE})
        self.assertEqual(doge["product"]["status"], "UNMAPPED")
        self.assertEqual(doge["product"]["native_status"],
                         "pending_review")


class TestQuotes(unittest.TestCase):
    def test_btc_quote_math_all_in(self):
        state = synced_state()
        q = srv.t_quote_get(state, {"instrument_id": BTC,
                                    "size": "0.5",
                                    "as_of": AS_OF})["quote"]
        self.assertEqual(q["bid"], "65430")
        self.assertEqual(q["ask"], "65432.1")
        self.assertEqual(q["mid_basis"], "computed")
        gross = Decimal("65432.10") * Decimal("0.5")
        fee = gross * Decimal("60") / 10000
        self.assertEqual(q["all_in_buy_cost"]["total"],
                         eng.ds(gross + fee))
        self.assertEqual(q["fee_status"], "FRESH")
        self.assertEqual(q["fee_schedule_ref"], "coinbase@2026-10-25")

    def test_stale_schedule_degrades(self):
        state = synced_state()
        q = srv.t_quote_get(state, {"instrument_id": BTC,
                                    "size": "0.5",
                                    "as_of": "2027-06-01T00:00:00Z"}
                            )["quote"]
        self.assertEqual(q["fee_status"], "STALE")
        self.assertEqual(q["all_in_buy_cost"], "FEE_UNVERIFIED")

    def test_no_probability_fields(self):
        state = synced_state()
        outputs = [srv.t_product_list(state, {}),
                   srv.t_book_get(state, {"instrument_id": BTC}),
                   srv.t_quote_get(state, {"instrument_id": BTC,
                                           "size": "1",
                                           "as_of": AS_OF}),
                   srv.t_venue_status(state, {"as_of": AS_OF})]
        for out in outputs:
            self.assertEqual(eng.probability_scan(out), [])


class TestDenylist(unittest.TestCase):
    def test_tool_surface_exact(self):
        self.assertEqual(set(srv.TOOLS), {
            "product_list", "product_get", "book_get", "quote_get",
            "venue_status", "receipt_list"})

    def test_no_account_tools_exist(self):
        for name in ("account_get", "accounts_list", "balance_get",
                     "place_order", "withdraw", "transfer"):
            self.assertIn(name, srv.FORBIDDEN_TOOL_NAMES)
            self.assertNotIn(name, srv.TOOLS)
            resp = srv.handle({"method": "tools/call", "id": 1,
                               "params": {"name": name,
                                          "arguments": {}}})
            self.assertEqual(resp["error"]["code"], -32602, name)

    def test_venue_status_states_account_absent(self):
        state = synced_state()
        status = srv.t_venue_status(state, {"as_of": AS_OF})
        self.assertTrue(status["account_surface"].startswith("ABSENT"))


if __name__ == "__main__":
    unittest.main()

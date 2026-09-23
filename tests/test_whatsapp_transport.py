"""Tests for whatsapp/transport.py — injectable sender, no network."""

import sqlite3
import unittest

from whatsapp import build_message, record_consent, send_payload
from whatsapp.optout import init_consent_tables


def _db():
    conn = sqlite3.connect(":memory:")
    init_consent_tables(conn)
    return conn


def _consented(conn, to="+447700900100"):
    record_consent(conn, to, "test-opt-in")
    return to


def _stub_sender(calls, message_id="wamid.TEST123"):
    def send(url, token, body):
        calls.append({"url": url, "token": token, "body": body})
        return {"messages": [{"id": message_id}]}
    return send


class TestTransportRefusals(unittest.TestCase):
    def test_unsendable_payload_never_sends(self):
        conn = _db()
        calls = []
        receipt = send_payload(
            conn, {"sendable": False, "reason": "nope", "to": "+447700900100"},
            phone_number_id="123", token="tok",
            sender=_stub_sender(calls))
        self.assertFalse(receipt["sent"])
        self.assertEqual(calls, [])

    def test_no_token_refuses(self):
        conn = _db()
        to = _consented(conn)
        payload = build_message(conn, to=to, template="review_due",
                                variables={"name": "Jo", "link": "https://example.test/book"})
        calls = []
        receipt = send_payload(
            conn, payload, phone_number_id="123", token="",
            sender=_stub_sender(calls))
        # '' token falls back to env; env unset in tests → refusal
        import os
        if not os.environ.get("WHATSAPP_TOKEN"):
            self.assertFalse(receipt["sent"])
            self.assertEqual(calls, [])
        else:
            self.assertTrue(receipt["sent"])


class TestTransportSend(unittest.TestCase):
    def test_template_send_shape(self):
        conn = _db()
        to = _consented(conn)
        payload = build_message(conn, to=to, template="review_due",
                                variables={"name": "Jo", "link": "https://example.test/book"})
        self.assertTrue(payload["sendable"])
        calls = []
        receipt = send_payload(
            conn, payload, phone_number_id="PNID", token="SECRET",
            sender=_stub_sender(calls), idempotency_key="k-1")
        self.assertTrue(receipt["sent"])
        self.assertEqual(receipt["message_id"], "wamid.TEST123")
        self.assertFalse(receipt["replayed"])
        body = calls[0]["body"]
        self.assertEqual(body["type"], "template")
        self.assertEqual(body["to"], to)
        self.assertIn("graph.facebook.com", calls[0]["url"])
        self.assertEqual(calls[0]["token"], "SECRET")

    def test_idempotent_replay_skips_network(self):
        conn = _db()
        to = _consented(conn)
        payload = build_message(conn, to=to, template="review_due",
                                variables={"name": "Jo", "link": "https://example.test/book"})
        calls = []
        first = send_payload(
            conn, payload, phone_number_id="PNID", token="SECRET",
            sender=_stub_sender(calls), idempotency_key="k-replay")
        second = send_payload(
            conn, payload, phone_number_id="PNID", token="SECRET",
            sender=_stub_sender(calls), idempotency_key="k-replay")
        self.assertTrue(first["sent"])
        self.assertTrue(second["replayed"])
        self.assertEqual(second["message_id"], first["message_id"])
        self.assertEqual(len(calls), 1)

    def test_transport_error_returns_receipt(self):
        conn = _db()
        to = _consented(conn)
        payload = build_message(conn, to=to, template="review_due",
                                variables={"name": "Jo", "link": "https://example.test/book"})

        def boom(url, token, body):
            raise TimeoutError("down")

        receipt = send_payload(
            conn, payload, phone_number_id="PNID", token="SECRET",
            sender=boom)
        self.assertFalse(receipt["sent"])
        self.assertIn("TimeoutError", receipt["reason"])

    def test_no_message_id_is_failure(self):
        conn = _db()
        to = _consented(conn)
        payload = build_message(conn, to=to, template="review_due",
                                variables={"name": "Jo", "link": "https://example.test/book"})
        receipt = send_payload(
            conn, payload, phone_number_id="PNID", token="SECRET",
            sender=lambda u, t, b: {"oops": True})
        self.assertFalse(receipt["sent"])

    def test_window_refusal_never_reaches_sender(self):
        conn = _db()
        to = _consented(conn)
        payload = build_message(conn, to=to, body="hello freeform",
                                last_user_message_at="2020-01-01T00:00:00")
        self.assertFalse(payload["sendable"])
        calls = []
        receipt = send_payload(
            conn, payload, phone_number_id="PNID", token="SECRET",
            sender=_stub_sender(calls))
        self.assertFalse(receipt["sent"])
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()

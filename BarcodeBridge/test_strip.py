#!/usr/bin/env python3
"""Test unitari sulla logica di strip (senza hook tastiera)."""

from barcode_bridge import strip_prefix


def test_strip_typical_seven_plus_dash():
    assert strip_prefix("ABC1234-9876543210", strip_through_dash=True, require_dash=True) == "9876543210"


def test_strip_shorter_prefix():
    assert strip_prefix("AB-999", strip_through_dash=True, require_dash=True) == "999"


def test_no_dash_required():
    assert strip_prefix("SOLOCCODICE", strip_through_dash=True, require_dash=True) is None


def test_no_dash_passthrough_when_not_required():
    assert strip_prefix("SOLOCCODICE", strip_through_dash=True, require_dash=False) == "SOLOCCODICE"


def test_fallback_first_seven():
    assert strip_prefix("1234567RESTO", strip_through_dash=False, require_dash=False) == "RESTO"


def test_empty():
    assert strip_prefix("", strip_through_dash=True, require_dash=True) is None


if __name__ == "__main__":
    test_strip_typical_seven_plus_dash()
    test_strip_shorter_prefix()
    test_no_dash_required()
    test_no_dash_passthrough_when_not_required()
    test_fallback_first_seven()
    test_empty()
    print("OK: tutti i test passati")

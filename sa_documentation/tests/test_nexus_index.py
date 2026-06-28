# sa_documentation/tests/test_nexus_index.py
from sa_documentation.nexus_index import store_ok


def test_store_ok_true_on_clean_success():
    assert store_ok(0, "stored key=aip-x ns=ai-kortex") is True


def test_store_ok_false_on_error_marker():
    assert store_ok(0, "[ERROR] boolean (true)") is False


def test_store_ok_false_on_error_word():
    assert store_ok(0, "internal error while storing") is False


def test_store_ok_false_on_nonzero_returncode():
    assert store_ok(1, "stored") is False

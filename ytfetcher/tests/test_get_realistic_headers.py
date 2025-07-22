from scripts.headers import get_realistic_headers

def test_get_realistic_headers_return_type():
    headers = get_realistic_headers()

    print('keys', headers.keys())

    assert isinstance(headers, dict)
    assert headers.get("User-Agent") is not None
    assert headers.get("Referer") is not None
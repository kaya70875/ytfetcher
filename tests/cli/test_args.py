from ytfetcher._cli import create_parser, YTFetcherCLI

def test_initialize_http_and_proxy_config_default():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "fake_api_key",
        "-c", "TheOffice"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.http_timeout == 4.0
    assert cli.args.http_headers == cli.http_config.headers
    
    assert cli.args.http_proxy == ''
    assert cli.args.https_proxy == ''

    assert cli.args.webshare_proxy_username is None
    assert cli.args.webshare_proxy_password is None

def test_initialize_http_and_proxy_config_override():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "fake_api_key",
        "-c", "TheOffice",
        "--http-timeout", "4.2",
        "--http-headers", "{'key': 'value'}",
        "--http-proxy", "testhttp:proxy",
        "--https-proxy", "testhttps:proxy"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.http_timeout == 4.2
    assert cli.args.http_headers == {'key': 'value'}

    assert cli.args.http_proxy == 'testhttp:proxy'
    assert cli.args.https_proxy == 'testhttps:proxy'

def test_webshare_proxy_config():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "fake_api_key",
        "--webshare-proxy-username", "username",
        "--webshare-proxy-password", "password"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.webshare_proxy_username == 'username'
    assert cli.args.webshare_proxy_password == 'password'

def test_export_arguments():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "fake_api_key",
        "-c", "TheOffice",
        "-f", "json",
        "-o", "C:/Users/user1/Desktop"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.format == 'json'
    assert cli.args.output_dir == 'C:/Users/user1/Desktop'
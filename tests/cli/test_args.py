from ytfetcher._cli import create_parser, YTFetcherCLI

def test_initialize_http_and_proxy_config():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
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
        "-c", "TheOffice",
        "-f", "json",
        "-o", "C:/Users/user1/Desktop",
        "--filename", "testing"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.format == 'json'
    assert cli.args.output_dir == 'C:/Users/user1/Desktop'
    assert cli.args.filename == 'testing'

def test_comments_argument():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "TestChannel",
        "-f", "json",
        "--comments", "5"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.comments == 5

def test_comments_only_argument():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "TestChannel",
        "-f", "json",
        "--comments-only", "5"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.comments_only == 5

def test_comments_argument_default():
    parser = create_parser()
    args = parser.parse_args([
        "from_channel",
        "-c", "TestChannel",
        "-f", "json",
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.comments == 0
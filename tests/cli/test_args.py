from ytfetcher._cli import create_parser, YTFetcherCLI
from ytfetcher.config.fetch_config import default_cache_path

def test_initialize_http_and_proxy_config():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "--http-headers", "{'key': 'value'}",
        "--http-proxy", "testhttp:proxy",
        "--https-proxy", "testhttps:proxy"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.http_headers == {'key': 'value'}

    assert cli.args.http_proxy == 'testhttp:proxy'
    assert cli.args.https_proxy == 'testhttps:proxy'

def test_webshare_proxy_config():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "--webshare-proxy-username", "username",
        "--webshare-proxy-password", "password"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.webshare_proxy_username == 'username'
    assert cli.args.webshare_proxy_password == 'password'

def test_export_arguments():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
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
        "channel",
        "TestChannel",
        "-f", "json",
        "--comments", "5"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.comments == 5

def test_comments_only_argument():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "-f", "json",
        "--comments-only", "5"
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.comments_only == 5

def test_comments_argument_default():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "-f", "json",
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.comments == 0

def test_cache_path_argument_default():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.cache_path == default_cache_path()


def test_cache_path_argument_custom():
    parser = create_parser()
    args = parser.parse_args([
        "channel",
        "TestChannel",
        "--cache-path", "/tmp/custom-cache.sqlite3",
    ])

    cli = YTFetcherCLI(args=args)

    assert cli.args.cache_path == "/tmp/custom-cache.sqlite3"

def test_cache_clean_argument():
    parser = create_parser()
    args = parser.parse_args([
        "cache",
        "--clean"
    ])

    assert args.command == "cache"
    assert args.clean is True

import pytest

import mesen_rpc


def test_reports_unavailable_without_a_running_emulator():
    client = mesen_rpc.MesenRPC(url="http://localhost:9101/mcp", timeout=2)  # closed port
    assert client.available() is False


def test_decodes_a_plain_json_body():
    assert mesen_rpc._decode('{"jsonrpc":"2.0","id":1,"result":{"ok":true}}') == {"ok": True}


def test_decodes_an_sse_body():
    body = 'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"ok":true}}\n\n'
    assert mesen_rpc._decode(body) == {"ok": True}


def test_an_error_response_raises():
    with pytest.raises(mesen_rpc.MesenError):
        mesen_rpc._decode('{"jsonrpc":"2.0","id":1,"error":{"code":-1,"message":"nope"}}')

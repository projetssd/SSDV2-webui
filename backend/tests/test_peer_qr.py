import base64

import pytest

from app.adapters.ssdv2_cli import Ssdv2CtlError
from app.deps import get_ssdv2ctl
from app.main import app
from app.services.peer_qr import PeerQrError, read_peer_qr
from tests.conftest import FakeRunner

PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aP1sAAAAASUVORK5CYII="


def test_peer_qr_requires_authentication_and_csrf(client, auth_client):
    client.cookies.clear()
    assert client.post("/api/v1/apps/wireguard/peer-qr").status_code == 401
    # L'authentification seule ne suffit pas.
    from tests.conftest import login_payload

    assert auth_client.post("/api/v1/auth/login", json=login_payload()).status_code == 200
    assert auth_client.post("/api/v1/apps/wireguard/peer-qr").status_code == 403


def test_peer_qr_is_private_non_streaming_and_explicit(auth_client, caplog):
    runner = FakeRunner(payload={"app": "wireguard", "peer": "1", "png_base64": PNG})
    app.dependency_overrides[get_ssdv2ctl] = lambda: runner
    token = auth_client.cookies.get("ssdv2_webui_csrf")
    response = auth_client.post("/api/v1/apps/wireguard/peer-qr", headers={"x-csrf-token": token})
    assert response.status_code == 200
    assert response.json()["png_base64"] == PNG
    assert "no-store" in response.headers["cache-control"]
    assert runner.calls == [["app", "peer-qr", "wireguard"]]
    assert PNG not in caplog.text


@pytest.mark.parametrize(
    "value", ["private-key-secret", "A" * 699053, base64.b64encode(b"bad").decode()]
)
def test_peer_qr_rejects_invalid_or_oversized_output(value, caplog):
    runner = FakeRunner(payload={"png_base64": value})
    with pytest.raises(PeerQrError) as caught:
        read_peer_qr(runner)
    assert caught.value.status_code == 502
    assert value not in caught.value.message
    assert value not in caplog.text


def test_peer_qr_never_returns_subprocess_errors(auth_client, caplog):
    secret = "private-key-in-subprocess-error"
    runner = FakeRunner(error=Ssdv2CtlError("peer_qr_unavailable", secret))
    app.dependency_overrides[get_ssdv2ctl] = lambda: runner
    response = auth_client.post(
        "/api/v1/apps/wireguard/peer-qr",
        headers={"x-csrf-token": auth_client.cookies.get("ssdv2_webui_csrf")},
    )
    assert response.status_code == 409
    assert "no-store" in response.headers["cache-control"]
    assert secret not in response.text + caplog.text

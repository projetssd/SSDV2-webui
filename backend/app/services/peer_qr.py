"""Restitution explicite du QR WireGuard, jamais via un job ou des journaux."""

import base64
import binascii

from app.adapters.ssdv2_cli import Ssdv2CtlError, Ssdv2CtlRunner
from app.schemas.peer_qr import PeerQrOut


class PeerQrError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message


def read_peer_qr(runner: Ssdv2CtlRunner) -> PeerQrOut:
    try:
        payload = runner.run(["app", "peer-qr", "wireguard"], timeout=15)
    except Ssdv2CtlError as exc:
        status = 409 if exc.code == "peer_qr_unavailable" else 503
        raise PeerQrError(
            status, "QR code WireGuard indisponible. Réessayez après le démarrage."
        ) from None
    try:
        result = PeerQrOut.model_validate(payload)
        png = base64.b64decode(result.png_base64, validate=True)
        if (
            len(png) < 45
            or len(png) > 512 * 1024
            or not png.startswith(b"\x89PNG\r\n\x1a\n")
            or png[12:16] != b"IHDR"
            or png[-8:-4] != b"IEND"
        ):
            raise ValueError
    except (ValueError, binascii.Error):
        # Les erreurs Pydantic ou subprocess peuvent contenir le secret : ne
        # jamais transmettre leur message au client ni au logger.
        raise PeerQrError(502, "QR code WireGuard invalide.") from None
    return result

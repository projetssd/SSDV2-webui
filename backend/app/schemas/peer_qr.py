from typing import Literal

from pydantic import BaseModel, Field


class PeerQrOut(BaseModel):
    app: Literal["wireguard"] = "wireguard"
    peer: Literal["1"] = "1"
    png_base64: str = Field(min_length=1, max_length=699052)

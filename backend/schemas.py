from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CreateRoom(StrictModel):
    mode: Literal["normal", "assisted"] = "assisted"


class Authenticate(StrictModel):
    type: Literal["auth"]
    token: str = Field(min_length=20, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")


class MoveIntent(StrictModel):
    type: Literal["move"]
    from_square: str = Field(alias="from", pattern=r"^[a-h][1-8]$")
    to: str = Field(pattern=r"^[a-h][1-8]$")
    promotion: Literal["q", "r", "b", "n"] | None = None


class HintIntent(StrictModel):
    type: Literal["hint"]


class RevealIntent(StrictModel):
    type: Literal["reveal"]
    confirmed: Literal[True]
    ply: int = Field(ge=0)


intent_adapter = TypeAdapter(Annotated[MoveIntent | HintIntent | RevealIntent, Field(discriminator="type")])

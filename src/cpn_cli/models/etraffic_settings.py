from pydantic import BaseModel, ConfigDict, Field


class EtrafficSettings(BaseModel):
    model_config = ConfigDict(
        title="Setting cho API etraffic.gtelict.vn",
        frozen=True,
    )

    citizen_id: str = Field(
        description="Căn cước",
    )
    password: str = Field(
        description="Mật khẩu",
    )

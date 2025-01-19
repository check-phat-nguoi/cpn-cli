from pydantic import BaseModel, ConfigDict, Field

from cpn_cli.models.etraffic_settings import EtrafficSettings


class ApisSettings(BaseModel):
    model_config = ConfigDict(
        title="Setting cho các API",
        frozen=True,
    )

    retry_resolve_captcha: int = Field(
        description="Số lần thử lại captcha. Có tác dụng với csgt.vn",
        default=3,
    )
    etraffic: EtrafficSettings | None = None

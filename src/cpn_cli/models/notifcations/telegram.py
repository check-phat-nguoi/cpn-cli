from cpn_core.notifications.models.telegram import (
    TelegramNotificationEngineConfig,
)
from pydantic import ConfigDict

from cpn_cli.models.notifcations.base import BaseNotificationConfig


class TelegramNotificationConfig(BaseNotificationConfig):
    model_config = ConfigDict(
        title="Telegram config",
        frozen=True,
    )

    telegram: TelegramNotificationEngineConfig

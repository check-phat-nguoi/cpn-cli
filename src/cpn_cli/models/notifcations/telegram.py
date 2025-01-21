from cpn_core.models.notifications.telegram import TelegramConfig
from pydantic import ConfigDict

from cpn_cli.models.notifcations.base import BaseNotificationConfig


class TelegramNotificationConfig(BaseNotificationConfig):
    model_config = ConfigDict(
        title="Telegram config",
        frozen=True,
    )

    telegram: TelegramConfig

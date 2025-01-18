from cpn_core.notifications.models.discord import DiscordNotificationEngineConfig
from pydantic import ConfigDict

from cpn_cli.models.notifcations.base import BaseNotificationConfig


class DiscordNotificationConfig(BaseNotificationConfig):
    model_config = ConfigDict(
        title="Discord config",
        frozen=True,
    )

    discord: DiscordNotificationEngineConfig

import asyncio
from asyncio import gather, get_running_loop
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait as FutureWait
from functools import cache
from logging import getLogger

from cpn_core.models.plate_detail import PlateDetail
from cpn_core.notifications.discord import DiscordEngine
from cpn_core.notifications.telegram import TelegramEngine

from cpn_cli.models.notifcations.base import BaseNotificationConfig
from cpn_cli.models.notifcations.discord import DiscordNotificationConfig
from cpn_cli.models.notifcations.telegram import TelegramNotificationConfig
from cpn_cli.modules.config_reader import config

logger = getLogger(__name__)


class Notify:
    def __init__(self, plate_details: tuple[PlateDetail, ...]) -> None:
        self._plate_details: tuple[PlateDetail, ...] = plate_details
        self._telegram_engine: TelegramEngine
        self._discord_engine: DiscordEngine

    @cache
    def _get_messages_groups(self, markdown: bool) -> tuple[tuple[str, ...], ...]:
        return tuple(
            plate_detail.get_messages(
                show_less_detail=config.show_less_details,
                markdown=markdown,
                time_format=config.time_format,
            )
            for plate_detail in self._plate_details
        )

    async def _send_messages(self, notification_config: BaseNotificationConfig) -> None:
        try:
            if isinstance(notification_config, TelegramNotificationConfig):
                for messages in self._get_messages_groups(
                    notification_config.telegram.markdown
                ):
                    await self._telegram_engine.send(
                        notification_config.telegram, messages
                    )
            elif isinstance(notification_config, DiscordNotificationConfig):
                for messages in self._get_messages_groups(
                    notification_config.discord.markdown
                ):
                    await self._discord_engine.send(
                        notification_config.discord, messages
                    )
            else:
                logger.error("Unknown notification config!")
                return
        except Exception as e:
            logger.error("Failed to sent notification. %s", e)

    def _safe_thread_work(self, notification: BaseNotificationConfig, loop):
        future = asyncio.run_coroutine_threadsafe(
            self._send_messages(notification), loop
        )
        FutureWait([future])

    async def send(self) -> None:
        if not config.notifications:
            logger.debug("No notification was given. Skip notifying")
            return
        async with (
            TelegramEngine(
                timeout=config.request_timeout,
            ) as self._telegram_engine,
            DiscordEngine() as self._discord_engine,
        ):
            loop = get_running_loop()
            with ThreadPoolExecutor(
                max_workers=config.send_notification_per_time
            ) as executor:
                await gather(
                    *(
                        loop.run_in_executor(
                            executor, self._safe_thread_work, notification, loop
                        )
                        for notification in config.notifications
                        if notification.enabled
                    )
                )

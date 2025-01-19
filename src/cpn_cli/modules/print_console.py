from logging import getLogger

from cpn_core.models.plate_detail import PlateDetail

from cpn_cli.modules.config_reader import config

logger = getLogger(__name__)


class PrintConsole:
    def __init__(self, plate_details: tuple[PlateDetail, ...]) -> None:
        self.plate_details: tuple[PlateDetail, ...] = plate_details

    def print_console(self) -> None:
        if not config.print_console:
            return
        if not self.plate_details:
            logger.info("No plate details. Skip printing")
            return
        print(
            "\n\n---\n\n".join(
                plate_detail.get_str(
                    show_less_detail=config.show_less_details, markdown=False
                )
                for plate_detail in self.plate_details
            )
        )

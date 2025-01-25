from asyncio import gather
from logging import getLogger

from cpn_core.get_data.base import BaseGetDataEngine
from cpn_core.get_data.check_phat_nguoi import CheckPhatNguoiEngine
from cpn_core.get_data.csgt import CsgtEngine
from cpn_core.get_data.etraffic import EtrafficEngine
from cpn_core.get_data.phat_nguoi import PhatNguoiEngine
from cpn_core.get_data.zm_io import ZmioEngine
from cpn_core.models.plate_detail import PlateDetail
from cpn_core.models.plate_info import PlateInfo
from cpn_core.models.violation_detail import ViolationDetail
from cpn_core.types.api import ApiEnum

from cpn_cli.modules.config_reader import config

logger = getLogger(__name__)


class GetData:
    def __init__(self) -> None:
        self._checkphatnguoi_engine: CheckPhatNguoiEngine
        self._csgt_engine: CsgtEngine
        self._phatnguoi_engine: PhatNguoiEngine
        self._zmio_engine: ZmioEngine
        self._etraffic_engine: EtrafficEngine
        self._plate_details: set[PlateDetail] = set()

    async def _get_data_for_plate(self, plate_info: PlateInfo) -> None:
        apis: tuple[ApiEnum, ...] = plate_info.apis if plate_info.apis else config.apis
        engine: BaseGetDataEngine
        for api in apis:
            match api:
                case ApiEnum.checkphatnguoi_vn:
                    engine = self._checkphatnguoi_engine
                case ApiEnum.csgt_vn:
                    engine = self._csgt_engine
                case ApiEnum.phatnguoi_vn:
                    engine = self._phatnguoi_engine
                case ApiEnum.zm_io_vn:
                    engine = self._zmio_engine
                case ApiEnum.etraffic_gtelict_vn:
                    engine = self._etraffic_engine

            logger.info(
                "Plate %s: Getting data with API: %s...", plate_info.plate, api.value
            )
            violations: tuple[ViolationDetail, ...] | None = await engine.get_data(
                plate_info
            )

            if violations is None:
                logger.info(
                    "Plate %s: Failed to get data with API: %s",
                    plate_info.plate,
                    api.value,
                )
                continue
            logger.info(
                "Plate %s: Successfully got data with API: %s",
                plate_info.plate,
                api.value,
            )
            plate_detail: PlateDetail = PlateDetail(
                plate_info=plate_info,
                violations=tuple(
                    violation for violation in violations if not violation.status
                )
                if config.pending_fines_only
                else violations,
            )
            # NOTE: Maybe this will never get race condition while inserting to set
            self._plate_details.add(plate_detail)
            return

        logger.error(
            "Plate %s: Failed to get data!!!",
            plate_info.plate,
        )

    async def get_data(self) -> tuple[PlateDetail, ...]:
        async with (
            CheckPhatNguoiEngine(
                timeout=config.request_timeout,
            ) as self._checkphatnguoi_engine,
            CsgtEngine(
                timeout=config.request_timeout,
                retry_captcha=config.apis_settings.retry_resolve_captcha,
            ) as self._csgt_engine,
            PhatNguoiEngine(
                timeout=config.request_timeout,
            ) as self._phatnguoi_engine,
            ZmioEngine(
                timeout=config.request_timeout,
            ) as self._zmio_engine,
        ):
            if config.asynchronous:
                await gather(
                    *(
                        self._get_data_for_plate(plate_info)
                        for plate_info in config.plate_infos
                        if plate_info.enabled
                    )
                )
            else:
                for plate_info in config.plate_infos:
                    if plate_info.enabled:
                        await self._get_data_for_plate(plate_info)
        return tuple(self._plate_details)

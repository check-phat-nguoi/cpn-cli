import asyncio
from asyncio import gather, get_running_loop
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait as FutureWait
from logging import getLogger

from cpn_core.get_data.base import BaseGetDataEngine
from cpn_core.get_data.check_phat_nguoi import CheckPhatNguoiEngine
from cpn_core.get_data.csgt import CsgtEngine
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
        self._checkphatnguoi_engine: CheckPhatNguoiEngine = CheckPhatNguoiEngine(
            timeout=config.request_timeout,
        )
        self._csgt_engine: CsgtEngine = CsgtEngine(
            timeout=config.request_timeout,
            retry_captcha=config.apis_settings.retry_resolve_captcha,
        )
        self._phatnguoi_engine: PhatNguoiEngine = PhatNguoiEngine(
            timeout=config.request_timeout,
        )
        self._zmio_engine: ZmioEngine = ZmioEngine(
            timeout=config.request_timeout,
        )
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

    def _safe_thread_work(self, plate_info: PlateInfo, loop):
        future = asyncio.run_coroutine_threadsafe(
            self._get_data_for_plate(plate_info), loop
        )
        FutureWait([future])

    async def get_data(self) -> tuple[PlateDetail, ...]:
        async with (
            self._checkphatnguoi_engine,
            self._csgt_engine,
            self._phatnguoi_engine,
            self._zmio_engine,
        ):
            loop = get_running_loop()
            with ThreadPoolExecutor(max_workers=config.requests_per_time) as executor:
                await gather(
                    *(
                        loop.run_in_executor(
                            executor, self._safe_thread_work, plate_info, loop
                        )
                        for plate_info in config.plate_infos
                        if plate_info.enabled
                    )
                )

        return tuple(self._plate_details)

from sys import version_info
from types import FrameType
from typing import Protocol


class FrameScrappable(Protocol):
    def scrap_callable_domain_and_name(self, called_frame: FrameType) -> str:
        ...


if version_info.major >= 3 and version_info.minor >= 11:
    from pydoctrace.tracer.framescrapper.post311 import FrameScrapperPostPy311 as FrameScrapper
else:
    from pydoctrace.tracer.framescrapper.pre311 import FrameScrapperPrePy311 as FrameScrapper

FrameScrapper: FrameScrappable = FrameScrapper

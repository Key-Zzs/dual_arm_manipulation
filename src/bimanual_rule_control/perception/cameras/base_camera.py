from __future__ import annotations
"""Camera base class."""

from abc import ABC, abstractmethod

from .frame_types import CameraFrame


class BaseCamera(ABC):
    @abstractmethod
    def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self) -> CameraFrame:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

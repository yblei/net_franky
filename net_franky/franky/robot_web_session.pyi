from __future__ import annotations

from http.client import HTTPSConnection
from types import TracebackType
from typing import Any, Dict, Literal, Optional, Type


class RobotWebSessionError(Exception):
    ...


class FrankaAPIError(RobotWebSessionError):
    target: str
    http_code: int
    headers: Dict[str, str]
    message: str

    def __init__(
        self,
        target: str,
        http_code: int,
        http_reason: str,
        headers: Dict[str, str],
        message: str,
    ) -> None: ...


class TakeControlTimeoutError(RobotWebSessionError):
    ...


class RobotWebSession:
    __hostname: str
    __username: str
    __password: str
    __client: Optional[HTTPSConnection]
    __token: Optional[str]
    __control_token: Optional[str]
    __control_token_id: Optional[str]

    def __init__(self, hostname: str, username: str, password: str) -> None: ...

    @staticmethod
    def __encode_password(user: str, password: str) -> str: ...

    def _send_api_request(
        self,
        target: str,
        headers: Optional[Dict[str, str]] = ...,
        body: Optional[Any] = ...,
        method: Literal["GET", "POST", "DELETE"] = ...,
    ) -> bytes: ...

    def send_api_request(
        self,
        target: str,
        headers: Optional[Dict[str, str]] = ...,
        body: Optional[Any] = ...,
        method: Literal["GET", "POST", "DELETE"] = ...,
    ) -> bytes: ...

    def send_control_api_request(
        self,
        target: str,
        headers: Optional[Dict[str, str]] = ...,
        body: Optional[Any] = ...,
        method: Literal["GET", "POST", "DELETE"] = ...,
    ) -> bytes: ...

    def open(self, timeout: float = ...) -> RobotWebSession: ...

    def close(self) -> None: ...

    def __enter__(self) -> RobotWebSession: ...

    def __exit__(
        self,
    type: Optional[Type[BaseException]],
    value: Optional[BaseException],
    traceback: Optional[TracebackType],
    ) -> None: ...

    def __check_control_token(self) -> None: ...

    def take_control(self, wait_timeout: float = ..., force: bool = ...) -> None: ...

    def release_control(self) -> None: ...

    def enable_fci(self) -> None: ...

    def has_control(self) -> bool: ...

    def start_task(self, task: str) -> None: ...

    def unlock_brakes(self) -> None: ...

    def lock_brakes(self) -> None: ...

    def set_mode_programming(self) -> None: ...

    def set_mode_execution(self) -> None: ...

    def get_system_status(self) -> Dict[str, Any]: ...

    def execute_self_test(self) -> None: ...

    @property
    def client(self) -> Optional[HTTPSConnection]: ...

    @property
    def token(self) -> Optional[str]: ...

    @property
    def is_open(self) -> bool: ...

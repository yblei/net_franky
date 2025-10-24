from ._franky import _RobotInternal

from .robot_web_session import RobotWebSession


class Robot(_RobotInternal):
    def create_web_session(self, username: str, password: str):
        return RobotWebSession(self, username, password)

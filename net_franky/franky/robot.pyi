from ._franky import _RobotInternal
from net_franky.cb_robot import HWState
import franky

from .robot_web_session import RobotWebSession


class Robot(_RobotInternal):
    def create_web_session(self, username: str, password: str):
        return RobotWebSession(self, username, password)

    def get_last_callback_data(self) -> tuple[franky.RobotState, franky.Duration, franky.Duration, franky.Duration, franky.JointPositions]:
        """
        Get the data from the last motion callback. Check Franky Documentation Motion Callbacks section for more information.
        
        Contains a tupel of: 
        - franky.RobotState: The last buffered state of the robot
        - franky.Duration: time_step
        - franky.Duration: rel_time
        - franky.Duration: abs_time
        - franky.JointPositions: control_signal (e.g. control_signal.q for joint positions)
        
        """
        ...

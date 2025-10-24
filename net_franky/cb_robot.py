import time
from franky import Robot
import franky
from dataclasses import dataclass
import threading

state = None
state_mutex = threading.Lock()

@dataclass 
class HWState:
    robot_state: franky.RobotState
    time_step: franky.Duration
    rel_time: franky.Duration
    abs_time: franky.Duration
    control_signal: franky.JointPositions

def hw_state_callback(
    robot_state: franky.RobotState,
    time_step: franky.Duration,
    rel_time: franky.Duration,
    abs_time: franky.Duration,
    control_signal: franky.JointPositions,
):    
    global state
    state_mutex.acquire()
    state = HWState(
        robot_state=robot_state,
        time_step=time_step,
        rel_time=rel_time,
        abs_time=abs_time,
        control_signal=control_signal,
    )
    state_mutex.release()

class CBRobot(Robot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def move(self, motion, asynchronous=False):
        print("CBRobot is moving")
        motion.register_callback(hw_state_callback)
        super(CBRobot, self).move(motion, asynchronous=asynchronous)

    def get_last_callback_data(self) -> tuple:
        global state
        state_mutex.acquire()
        state_tuple = (
            state.robot_state,
            state.time_step,
            state.rel_time,
            state.abs_time,
            state.control_signal
        )
        state_mutex.release()
        return state_tuple

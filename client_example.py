from net_franky import setup_net_franky
setup_net_franky("localhost", 18812)

from net_franky.franky import *
from scipy.spatial.transform import Rotation
import math
import numpy as np

robot = Robot("192.168.100.1")  # Replace this with your robot's IP
robot.recover_from_errors()

# Let's start slow (this lets the robot use a maximum of 5% of its velocity, acceleration, and jerk limits)
robot.relative_dynamics_factor = 0.05
z_translation_1 = Affine(np.array([0.4, 0.0, 0.3]))
z_translation_2 = Affine(np.array([0.3, 0.0, 0.4]))

gripper = Gripper("192.168.100.1")
gripper.move(0.5, 0.5)

quat = Rotation.from_euler("xyz", [0, -math.pi, 0]).as_quat()
z_rotation = Affine(np.array([0.0, 0.0, 0.0]), quat)

while True:
    rpos = z_translation_1 * z_rotation
    motion = CartesianMotion(rpos, ReferenceType.Absolute)
    m = robot.move(motion, asynchronous=True)
    
    # wait for motion to complete
    while not robot.join_motion(timeout=0.1):
        state: tuple = robot.get_last_callback_data()
        print(state[0].q)
        

    rpos = z_translation_2 * z_rotation
    motion = CartesianMotion(rpos, ReferenceType.Absolute)
    robot.move(motion, asynchronous=True)
    robot.join_motion()


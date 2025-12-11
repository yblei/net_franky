"""Tests for CBRobot callback functionality."""
from unittest.mock import Mock
from net_franky.cb_robot import hw_state_callback, HWState
import franky


class TestHWStateCallback:
    """Test cases for hardware state callback."""
    
    def test_hw_state_callback(self):
        """Test that callback properly stores state."""
        # Create mock objects
        mock_robot_state = Mock(spec=franky.RobotState)
        mock_time_step = Mock(spec=franky.Duration)
        mock_rel_time = Mock(spec=franky.Duration)
        mock_abs_time = Mock(spec=franky.Duration)
        mock_control_signal = Mock(spec=franky.JointPositions)
        
        # Call the callback
        hw_state_callback(
            mock_robot_state,
            mock_time_step,
            mock_rel_time,
            mock_abs_time,
            mock_control_signal
        )
        
        # Import state to check it was set
        from net_franky import cb_robot
        assert cb_robot.state is not None
        assert isinstance(cb_robot.state, HWState)
        assert cb_robot.state.robot_state == mock_robot_state
    
    def test_hw_state_stores_all_fields(self):
        """Test that all fields are properly stored."""
        mock_robot_state = Mock(spec=franky.RobotState)
        mock_time_step = Mock(spec=franky.Duration)
        mock_rel_time = Mock(spec=franky.Duration)
        mock_abs_time = Mock(spec=franky.Duration)
        mock_control_signal = Mock(spec=franky.JointPositions)
        
        hw_state_callback(
            mock_robot_state,
            mock_time_step,
            mock_rel_time,
            mock_abs_time,
            mock_control_signal
        )
        
        from net_franky import cb_robot
        assert cb_robot.state.time_step == mock_time_step
        assert cb_robot.state.rel_time == mock_rel_time
        assert cb_robot.state.abs_time == mock_abs_time
        assert cb_robot.state.control_signal == mock_control_signal

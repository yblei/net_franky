"""Tests for net_franky setup functionality."""
import pytest
from net_franky.setup import setup_net_franky, cfg


class TestSetupNetFranky:
    """Test cases for setup_net_franky function."""
    
    def test_setup_basic(self):
        """Test basic setup with IP and port."""
        setup_net_franky("192.168.1.100", 18812)
        
        assert cfg.IS_SETUP is True
        assert cfg.IP == "192.168.1.100"
        assert cfg.PORT == 18812
    
    def test_setup_localhost(self):
        """Test setup with localhost."""
        setup_net_franky("localhost", 18812)
        
        assert cfg.IS_SETUP is True
        assert cfg.IP == "localhost"
        assert cfg.PORT == 18812
    
    def test_setup_different_port(self):
        """Test setup with different port."""
        setup_net_franky("10.0.0.1", 12345)
        
        assert cfg.IS_SETUP is True
        assert cfg.IP == "10.0.0.1"
        assert cfg.PORT == 12345

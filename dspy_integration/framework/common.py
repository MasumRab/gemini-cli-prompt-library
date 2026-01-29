"""
Common utilities and base classes to reduce code duplication.

This module provides common functionality shared across different components
to reduce duplication found in the codebase.
"""

import time
import subprocess
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


class CommonUtils:
    """
    Common utility functions to reduce duplication across the codebase.
    """
    
    @staticmethod
    def is_rate_limited(output: str, custom_indicators: Optional[list] = None) -> bool:
        """
        Common method to detect rate limiting indicators in output.
        
        Args:
            output: Output string to check
            custom_indicators: Additional custom indicators to check
            
        Returns:
            True if rate limited, False otherwise
        """
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "quota exceeded",
            "user rate limit",
            "exceeded",
            "try again later"
        ]
        
        if custom_indicators:
            rate_limit_indicators.extend(custom_indicators)
        
        output_lower = output.lower()
        return any(indicator in output_lower for indicator in rate_limit_indicators)
    
    @staticmethod
    def execute_subprocess_cmd(
        cmd: list,
        timeout: int = 120,
        capture_output: bool = True
    ) -> tuple:
        """
        Common method to execute subprocess commands with error handling.
        
        Args:
            cmd: Command to execute as a list
            timeout: Command timeout in seconds
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            return -1, "", f"Command timed out after {timeout} seconds (elapsed: {elapsed:.2f}s)"
        except Exception as e:
            elapsed = time.time() - start_time
            return -1, "", f"Exception during command execution: {str(e)} (elapsed: {elapsed:.2f}s)"
    
    @staticmethod
    def make_api_request(
        url: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        timeout: int = 60
    ) -> tuple:
        """
        Common method to make API requests with error handling.
        
        Args:
            url: API endpoint URL
            headers: Request headers
            payload: Request payload
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (status_code, response_data, error_message)
        """
        start_time = time.time()
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                return 200, response.json(), None
            elif response.status_code == 401:
                return 401, None, "Unauthorized: Invalid API key"
            elif response.status_code == 429:
                return 429, None, "Rate limit exceeded"
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return response.status_code, None, error_msg
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            return -1, None, f"Request timed out after {timeout} seconds (elapsed: {elapsed:.2f}s)"
        except Exception as e:
            elapsed = time.time() - start_time
            return -1, None, f"Exception during API request: {str(e)} (elapsed: {elapsed:.2f}s)"


class CommonProviderMixin:
    """
    Mixin class providing common functionality for providers.
    
    This addresses code duplication in provider implementations by providing
    common methods for rate limiting detection, subprocess execution, and API requests.
    """
    
    def _is_rate_limited(self, output: str) -> bool:
        """
        Detect rate limiting indicators using common utility.
        
        Args:
            output: Output string to check
            
        Returns:
            True if rate limited, False otherwise
        """
        return CommonUtils.is_rate_limited(output)
    
    def _execute_subprocess_cmd(self, cmd: list, timeout: int = 120) -> tuple:
        """
        Execute subprocess command with common error handling.
        
        Args:
            cmd: Command to execute as a list
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        return CommonUtils.execute_subprocess_cmd(cmd, timeout)
    
    def _make_api_request(
        self, 
        url: str, 
        headers: Dict[str, str], 
        payload: Dict[str, Any], 
        timeout: int = 60
    ) -> tuple:
        """
        Make API request with common error handling.
        
        Args:
            url: API endpoint URL
            headers: Request headers
            payload: Request payload
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (status_code, response_data, error_message)
        """
        return CommonUtils.make_api_request(url, headers, payload, timeout)
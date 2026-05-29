# -*- coding: utf-8 -*-
"""
Unit tests for the AureaTools CommandRunner execution engine.
"""

import unittest
import subprocess
from aurea.core.process import CommandRunner
from aurea.core import platform_info


class TestCommandRunner(unittest.TestCase):

    def test_resolve_command_linux_fallbacks(self):
        # Even on Windows, we can test the mapping utility logic itself in isolation
        resolved_ss = CommandRunner._resolve_command(["ss", "-tuna"])
        if platform_info.is_windows():
            self.assertEqual(resolved_ss, ["ss", "-tuna"])
        else:
            # On Linux, if ss is not installed it falls back to netstat, otherwise remains ss
            import shutil
            if shutil.which("ss"):
                self.assertEqual(resolved_ss, ["ss", "-tuna"])
            else:
                self.assertEqual(resolved_ss, ["netstat", "-tuln"])

    def test_run_command_success(self):
        # Run a simple safe command depending on OS
        if platform_info.is_windows():
            cmd = ["cmd", "/c", "echo hello"]
        else:
            cmd = ["echo", "hello"]
            
        res = CommandRunner.run(cmd)
        self.assertIsNotNone(res)
        self.assertEqual(res.returncode, 0)
        self.assertIn("hello", res.stdout.strip())

    def test_run_command_timeout(self):
        # Run a command designed to sleep and timeout
        if platform_info.is_windows():
            cmd = ["powershell", "-Command", "Start-Sleep -Seconds 5"]
        else:
            cmd = ["sleep", "5"]
            
        res = CommandRunner.run(cmd, timeout=0.1)
        self.assertIsNone(res)  # Timeout returns None and handles it gracefully

    def test_run_stream_real_time(self):
        if platform_info.is_windows():
            cmd = ["cmd", "/c", "echo line1 && echo line2"]
        else:
            cmd = ["sh", "-c", "echo line1; echo line2"]
            
        lines = list(CommandRunner.run_stream(cmd))
        self.assertTrue(any("line1" in line for line in lines))
        self.assertTrue(any("line2" in line for line in lines))


if __name__ == "__main__":
    unittest.main()

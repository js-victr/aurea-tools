"""
Unit tests for tool registry and tool loading.
"""

import unittest
from aurea import tools


class TestToolsRegistry(unittest.TestCase):

    def setUp(self):
        tools._load_all_tools()

    def test_all_tools_loaded(self):
        all_tools = tools.get_all_tools()
        # We expect 31 tools in total after carrier-grade redesign
        self.assertEqual(len(all_tools), 31)

    def test_tool_getting(self):
        tool_1 = tools.get_tool("1")
        self.assertIsNotNone(tool_1)
        self.assertEqual(tool_1.number, "1")
        self.assertEqual(tool_1.category, "diagnostics")
        
        tool_23 = tools.get_tool("23")
        self.assertIsNotNone(tool_23)
        self.assertEqual(tool_23.number, "23")
        self.assertEqual(tool_23.category, "automation")

        tool_31 = tools.get_tool("31")
        self.assertIsNotNone(tool_31)
        self.assertEqual(tool_31.number, "31")
        self.assertEqual(tool_31.category, "automation")

    def test_search_tools(self):
        # Search by number
        self.assertEqual(len(tools.search_tools("1")), 1)
        
        # Search by keyword "ping"
        ping_tools = tools.search_tools("ping")
        self.assertGreaterEqual(len(ping_tools), 2)
        
        # Search by name/i18n key
        self.assertTrue(any("DNS" in t.name for t in tools.search_tools("DNS")))


    def test_tool_execution_wrapper(self):
        called = False
        
        @tools.tool("99", "Mock Test Tool", "diagnostics")
        def mock_tool_func():
            nonlocal called
            called = True
            
        # Retrieve the mock tool and run its func
        t = tools.get_tool("99")
        self.assertIsNotNone(t)
        
        # Invoke the wrapper
        t.func()
        
        self.assertTrue(called)


if __name__ == "__main__":
    unittest.main()

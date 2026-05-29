# -*- coding: utf-8 -*-
"""
Unit tests for the decoupled AureaFlow NetFlow v5 engine and heuristics.
"""

import struct
import queue
import unittest
import ipaddress
import time

from aurea.core.engines.netflow import NetFlowCollector, _is_private_ip


class TestNetFlowCollectorEngine(unittest.TestCase):

    def setUp(self):
        self.collector = NetFlowCollector(port=29999)

    def test_private_ip_heuristic(self):
        # Local subnets
        self.assertTrue(_is_private_ip("192.168.1.1"))
        self.assertTrue(_is_private_ip("10.0.0.254"))
        self.assertTrue(_is_private_ip("172.16.10.15"))
        self.assertTrue(_is_private_ip("127.0.0.1"))
        
        # Public subnets
        self.assertFalse(_is_private_ip("8.8.8.8"))
        self.assertFalse(_is_private_ip("1.1.1.1"))
        self.assertFalse(_is_private_ip("200.17.20.10"))

    def test_netflow_v5_binary_decoding_and_snapshot(self):
        # 1. Construct valid 24-byte NetFlow v5 Header
        # Format: !HHIIIIBBH
        header_bytes = struct.pack(
            "!HHIIIIBBH", 
            5, 1, 1000, 1621234567, 500000, 1, 1, 1, 0
        )
        
        # 2. Construct valid 48-byte NetFlow v5 Record
        # Format: !IIIHHIIIIHHBBBBHHBBH
        src_int = int(ipaddress.IPv4Address("192.168.0.100"))
        dst_int = int(ipaddress.IPv4Address("8.8.8.8"))
        nh_int = int(ipaddress.IPv4Address("192.168.0.1"))
        
        record_bytes = struct.pack(
            "!IIIHHIIIIHHBBBBHHBBH",
            src_int, dst_int, nh_int,
            1, 2, 10, 1500, 100, 200,
            45678, 443, 0, 16, 6, 0,
            0, 15169, 24, 32, 0
        )
        
        payload = header_bytes + record_bytes
        self.assertEqual(len(payload), 72)  # 24 header + 48 record
        
        # Set active manually for worker test without opening UDP socket bind
        self.collector.active = True
        self.collector.packet_queue.put((payload, ("192.168.0.1", 2055)))
        
        # Patch queue.get to turn active off after retrieval so the worker exits after 1 iteration
        orig_get = self.collector.packet_queue.get
        def mock_get(*args, **kwargs):
            item = orig_get(*args, **kwargs)
            self.collector.active = False
            return item
        self.collector.packet_queue.get = mock_get
        
        # Manually run one iteration of the parser worker
        self.collector._parser_worker()
        
        snapshot = self.collector.get_snapshot()
        
        self.assertEqual(snapshot["total_bytes"], 1500)
        self.assertEqual(snapshot["up_bytes"], 1500)
        self.assertEqual(snapshot["down_bytes"], 0)
        self.assertEqual(snapshot["protocols"]["tcp"], 1500)
        self.assertEqual(snapshot["protocols"]["udp"], 0)
        self.assertIn("192.168.0.100", snapshot["talkers"][0][0])
        self.assertEqual(snapshot["talkers"][0][1], 1500)

    def test_port_scan_threat_heuristics(self):
        src_ip = "192.168.0.50"
        self.collector.active = True
        
        header_bytes = struct.pack("!HHIIIIBBH", 5, 20, 1000, 1621234567, 500000, 1, 1, 1, 0)
        payload = header_bytes
        
        src_int = int(ipaddress.IPv4Address(src_ip))
        dst_int = int(ipaddress.IPv4Address("192.168.0.1"))
        
        # Simulate 20 packet records on different ports
        for port in range(1, 21):
            record_bytes = struct.pack(
                "!IIIHHIIIIHHBBBBHHBBH",
                src_int, dst_int, 0,
                1, 2, 1, 64, 100, 200,
                55555, port, 0, 2, 6, 0,
                0, 0, 24, 24, 0
            )
            payload += record_bytes
            
        self.collector.packet_queue.put((payload, (src_ip, 2055)))
        
        # Patch queue.get to turn active off after retrieval so the worker exits after 1 iteration
        orig_get = self.collector.packet_queue.get
        def mock_get(*args, **kwargs):
            item = orig_get(*args, **kwargs)
            self.collector.active = False
            return item
        self.collector.packet_queue.get = mock_get
        
        # Parse all records
        self.collector._parser_worker()
        
        snapshot = self.collector.get_snapshot()
        self.assertEqual(len(snapshot["alerts"]), 1)
        self.assertIn("192.168.0.50", snapshot["alerts"][0]["desc"])


if __name__ == "__main__":
    unittest.main()

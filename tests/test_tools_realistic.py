# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock
import socket
import io
import sys
import ipaddress

from aurea.tools.diagnostics import port_check, isp_latency_matrix, subnet_overlay_planner
from aurea.tools.services import dns_benchmark, cgnat_exhaustion_simulator
from aurea.tools.bgp import traffic_monitor


class TestToolsRealistic(unittest.TestCase):

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("socket.socket")
    def test_nmap_port_scanner_realistic(self, mock_socket_class, mock_pause, mock_input):
        # Mock inputs: host to scan
        mock_input.return_value = "127.0.0.1"
        
        # Setup socket mock
        mock_socket = MagicMock()
        # Mock connect_ex: returns 0 (open) for port 22 and 80, returns 1 for others
        def side_effect_connect(addr):
            port = addr[1]
            if port in (22, 80):
                return 0
            return 1
        mock_socket.connect_ex.side_effect = side_effect_connect
        
        # Mock banner grabbing recv
        def side_effect_recv(bufsize):
            return b"SSH-2.0-OpenSSH_8.2"
        mock_socket.recv.side_effect = side_effect_recv
        
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        # Redirect stdout to check output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            port_check()
        finally:
            sys.stdout = sys.__stdout__

        # Assertions
        output_str = captured_output.getvalue()
        self.assertIn("AUREA NMAP TCP PORT SCANNER", output_str)
        self.assertIn("Porta 22", output_str)
        self.assertIn("ABERTA", output_str)
        self.assertIn("SSH-2.0-OpenSSH_8.2", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.pause")
    @patch("socket.socket")
    def test_isp_latency_matrix_realistic(self, mock_socket_class, mock_pause):
        # Setup socket mock: always open
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            isp_latency_matrix()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("DYNAMIC ISP LATENCY & ROUTING QUALITY MATRIX", output_str)
        self.assertIn("AWS Cloud", output_str)
        self.assertIn("EXCELENTE", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    def test_subnet_overlay_planner_ipv4_realistic(self, mock_pause, mock_input):
        # Set mock inputs for IPv4 scenario
        mock_input.side_effect = [
            "10.0.0.0/24, 10.0.1.0/24",  # Existing subnets
            "10.0.0.0/22",                 # Proposed supernet
            "26"                           # Target prefix
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            subnet_overlay_planner()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("SUBNET OVERLAY PLANNER & CONFLICT DETECTOR", output_str)
        self.assertIn("RELATÓRIO DE AUDITORIA DE OVERLAPS IPAM:", output_str)
        self.assertIn("10.0.2.0/26", output_str)  # Recommended free block
        self.assertIn("10.0.3.0/26", output_str)  # Recommended free block
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    def test_subnet_overlay_planner_ipv6_realistic(self, mock_pause, mock_input):
        # Set mock inputs for IPv6 scenario
        mock_input.side_effect = [
            "2001:db8:1::/48",             # Existing subnets
            "2001:db8::/32",               # Proposed supernet
            "64"                           # Target prefix
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            subnet_overlay_planner()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("SUBNET OVERLAY PLANNER & CONFLICT DETECTOR", output_str)
        self.assertIn("2001:db8::/64", output_str)  # Recommended free block
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("socket.socket")
    def test_cgnat_exhaustion_simulator_realistic(self, mock_socket_class, mock_pause, mock_input):
        # Setup inputs: target and fast thread count (20)
        mock_input.side_effect = ["google.com", "20"]

        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value.__enter__.return_value = mock_socket

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            cgnat_exhaustion_simulator()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("CGNAT PORT EXHAUSTION SIMULATOR", output_str)
        self.assertIn("SIMULAÇÃO DE EXAUSTÃO CONCLUÍDA", output_str)
        self.assertIn("Conexões Bem-Sucedidas: 20", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("socket.socket")
    def test_dns_benchmark_realistic(self, mock_socket_class, mock_pause, mock_input):
        mock_input.return_value = "google.com"

        mock_socket = MagicMock()
        # Mock recvfrom: return dummy data
        mock_socket.recvfrom.return_value = (b"\x00" * 30, ("8.8.8.8", 53))
        mock_socket_class.return_value = mock_socket

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            dns_benchmark()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("LOCAL DNS BENCHMARK", output_str)
        self.assertIn("Google DNS", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("aurea.core.platform_info.is_windows")
    @patch("aurea.core.ui.run_command_safe")
    @patch("aurea.core.network.get_asn_org")
    @patch("time.sleep")
    def test_traffic_flow_monitor_connections_realistic(self, mock_sleep, mock_get_asn_org, mock_run, mock_is_windows, mock_pause, mock_input):
        # 1: Capture Local Active Connections
        mock_input.return_value = "1"
        
        # Simulate Windows environment
        mock_is_windows.return_value = True

        mock_get_asn_org.return_value = "Google LLC"

        # Mock netstat -ano output
        mock_completed_proc = MagicMock()
        mock_completed_proc.returncode = 0
        mock_completed_proc.stdout = (
            "Active Connections\n"
            "  Proto  Local Address          Foreign Address        State           PID\n"
            "  TCP    192.168.0.2:50443      8.8.8.8:443            ESTABLISHED     1234\n"
            "  UDP    192.168.0.2:123        1.1.1.1:123            UDP_FLOW        5678\n"
        )
        mock_run.return_value = mock_completed_proc

        # Stop infinite loop by raising KeyboardInterrupt on time.sleep
        mock_sleep.side_effect = KeyboardInterrupt("Stop loop")

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            traffic_monitor()
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("AUREA NET ACTIVE", output_str)
        self.assertIn("TCP", output_str)
        self.assertIn("192.168.0.2:50443", output_str)
        self.assertIn("8.8.8.8:443", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("socket.create_connection")
    @patch("socket.socket")
    @patch("ssl.create_default_context")
    def test_ssl_inspector_realistic(self, mock_create_default_context, mock_socket_class, mock_create_connection, mock_pause, mock_input):
        mock_input.return_value = "google.com"

        # Mock SSL Context & Connection
        mock_context = MagicMock()
        mock_ssl_socket = MagicMock()
        
        # Cipher mock
        mock_ssl_socket.cipher.return_value = ("ECDHE-RSA-AES128-GCM-SHA256", "TLSv1.3", 128)
        
        # Certificate mock
        mock_ssl_socket.getpeercert.return_value = {
            'subject': ((('commonName', 'google.com'),),),
            'issuer': ((('commonName', 'GTS CA 1C3'),),),
            'notBefore': 'May 28 00:00:00 2026 GMT',
            'notAfter': 'Aug 26 23:59:59 2026 GMT',
            'subjectAltName': (('DNS', 'google.com'), ('DNS', 'www.google.com'))
        }
        
        mock_context.wrap_socket.return_value = mock_ssl_socket
        mock_create_default_context.return_value = mock_context

        # Mock standard socket for creating connection
        mock_sock_inst = MagicMock()
        mock_socket_class.return_value = mock_sock_inst
        mock_create_connection.return_value = mock_sock_inst

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            from aurea.tools.services import ssl_inspector
            ssl_inspector()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("AUREA SSL/TLS CRYPTOGRAPHIC PROTOCOL & CHAIN AUDITOR", output_str)
        self.assertIn("TLSv1.3", output_str)
        self.assertIn("GTS CA 1C3", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("aurea.core.http_client.fetch_json")
    def test_bgp_looking_glass_realistic(self, mock_fetch_json, mock_pause, mock_input):
        mock_input.return_value = "8.8.8.8"

        # Define mocks for fetch_json side effect
        def side_effect_fetch(url, *args, **kwargs):
            if "prefix-overview" in url:
                return {
                    "status": "ok",
                    "data": {
                        "prefix": "8.8.8.0/24",
                        "asns": [{"asn": 15169, "holder": "Google LLC"}]
                    }
                }
            elif "rpki-validation" in url:
                return {
                    "status": "ok",
                    "data": {
                        "status": "VALID",
                        "validating_roas": [{"prefix": "8.8.8.0/24", "max_length": 24, "origin": 15169}]
                    }
                }
            elif "looking-glass" in url:
                return {
                    "status": "ok",
                    "data": {
                        "rrcs": [
                            {
                                "rrc": "RRC00",
                                "peers": [{"asn": 2914, "next_hop": "192.0.2.1", "as_path": "2914 15169"}]
                            }
                        ]
                    }
                }
            return None

        mock_fetch_json.side_effect = side_effect_fetch

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            from aurea.tools.bgp import bgp_looking_glass
            bgp_looking_glass()
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("BGP LOOKING GLASS CONSOLIDADO", output_str)
        self.assertIn("AS15169", output_str)
        self.assertIn("Google LLC", output_str)
        self.assertIn("RPKI Status: VALID", output_str)
        self.assertIn("AS2914", output_str)
        mock_pause.assert_called_once()

    @patch("aurea.core.ui.input_with_default")
    @patch("aurea.core.ui.pause")
    @patch("aurea.tools.bgp.NetFlowCollector")
    @patch("time.sleep")
    def test_netflow_cli_dashboard_realistic(self, mock_sleep, mock_collector_class, mock_pause, mock_input):
        mock_input.side_effect = ["2", "2055", "1"] # Mode [2] NetFlow v5, Port 2055, Filter [1] No Filter
        
        # Setup mock NetFlowCollector
        mock_collector = MagicMock()
        mock_collector.get_snapshot.return_value = {
            "total_bytes": 1048576 * 2.5,
            "down_rate_kbps": 500.0,
            "up_rate_kbps": 300.0,
            "exporters": {
                "192.168.1.1": {
                    "vendor": "Cisco Systems",
                    "rate_kbps": 800.0,
                    "packets": 120
                }
            },
            "talkers": [("192.168.1.100", 1048576 * 2.0)],
            "protocols": {
                "tcp": 1048576 * 1.5,
                "udp": 1048576 * 1.0,
                "icmp": 0,
                "other": 0
            },
            "ports": [("443", 1048576 * 1.5), ("80", 1048576 * 1.0)],
            "interfaces": [
                (1, {"in_bytes": 1048576 * 1.5, "out_bytes": 0}),
                (2, {"in_bytes": 0, "out_bytes": 1048576 * 1.0})
            ],
            "alerts": []
        }
        mock_collector_class.return_value = mock_collector

        # Make time.sleep sleep normally on first call (startup), but raise KeyboardInterrupt on second call (loop)
        calls = []
        def side_effect_sleep(secs):
            calls.append(secs)
            if len(calls) == 2:
                raise KeyboardInterrupt("Exit Loop")
        mock_sleep.side_effect = side_effect_sleep

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            traffic_monitor()
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout = sys.__stdout__

        output_str = captured_output.getvalue()
        self.assertIn("AUREAFLOW", output_str)
        self.assertIn("Cisco Systems", output_str)
        self.assertIn("192.168.1.100", output_str)
        self.assertIn("IfIndex 1", output_str)
        self.assertIn("CONGESTIONADO", output_str)
        mock_pause.assert_called_once()


if __name__ == "__main__":
    unittest.main()

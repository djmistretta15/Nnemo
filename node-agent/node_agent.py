#!/usr/bin/env python3
"""
Mnemo Node Agent
Runs on provider machines to report memory availability

Usage:
    python node_agent.py

Configuration:
    Edit node_config.json before running
"""

import os
import sys
import time
import json
import requests
import psutil
import platform
from datetime import datetime
from pathlib import Path

# Try to import GPU monitoring (optional)
try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
except Exception:
    GPU_AVAILABLE = False
    print("⚠ GPU monitoring not available (pynvml not installed or no GPU detected)")


class MnemoNodeAgent:
    """Node agent for reporting system metrics to Mnemo platform"""

    def __init__(self, config_path='node_config.json'):
        """
        Initialize node agent with configuration

        Args:
            config_path: Path to configuration JSON file
        """
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"❌ Configuration file not found: {config_path}")
            print(f"   Please create {config_path} based on node_config.example.json")
            sys.exit(1)

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.api_url = self.config['api_url']
        self.api_key = self.config['api_key']
        self.node_id = self.config.get('node_id')
        self.heartbeat_interval = self.config.get('heartbeat_interval', 60)

        # Register node if not already registered
        if not self.node_id:
            self.register_node()

    def register_node(self):
        """Register this machine as a node with the Mnemo platform"""
        print("\n🔧 Registering node with Mnemo platform...")

        # Detect system info
        ram_info = psutil.virtual_memory()

        payload = {
            "node_type": self.config['node_type'],
            "name": self.config['name'],
            "region": self.config['region'],
            "latitude": self.config.get('latitude'),
            "longitude": self.config.get('longitude'),
            "total_ram_gb": int(ram_info.total / (1024**3)),
            "total_vram_gb": self.get_total_vram(),
            "bandwidth_mbps": self.config.get('bandwidth_mbps', 1000),
            "base_latency_ms": self.config.get('base_latency_ms', 1.0),
            "price_per_gb_sec": self.config['price_per_gb_sec'],
            "metadata": {
                "os": platform.system(),
                "os_version": platform.version(),
                "cpu": platform.processor(),
                "cpu_cores": psutil.cpu_count(),
                "gpu_model": self.get_gpu_model(),
                "idle_schedule": self.config.get('idle_schedule', 'always')
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}/api/nodes/register",
                headers={"X-API-Key": self.api_key},
                json=payload,
                timeout=30
            )

            if response.status_code == 201:
                data = response.json()
                self.node_id = data['id']

                # Save node_id to config
                self.config['node_id'] = self.node_id
                with open('node_config.json', 'w') as f:
                    json.dump(self.config, f, indent=2)

                print(f"✅ Node registered successfully!")
                print(f"   Node ID: {self.node_id}")
                print(f"   Name: {self.config['name']}")
                print(f"   Type: {self.config['node_type']}")
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                sys.exit(1)

        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            sys.exit(1)

    def get_total_vram(self):
        """
        Get total VRAM in GB

        Returns:
            Total VRAM in GB across all GPUs
        """
        if not GPU_AVAILABLE:
            return 0

        try:
            device_count = pynvml.nvmlDeviceGetCount()
            total_vram = 0
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                total_vram += info.total
            return int(total_vram / (1024**3))
        except Exception:
            return 0

    def get_gpu_model(self):
        """
        Get GPU model name

        Returns:
            GPU model string or "No GPU"
        """
        if not GPU_AVAILABLE:
            return "No GPU"

        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            return name
        except Exception:
            return "Unknown GPU"

    def collect_metrics(self):
        """
        Collect current system metrics

        Returns:
            Dictionary of current metrics
        """
        # RAM
        ram_info = psutil.virtual_memory()
        available_ram_gb = int(ram_info.available / (1024**3))

        # VRAM
        available_vram_gb = self.get_available_vram()

        # CPU
        cpu_usage = psutil.cpu_percent(interval=1)

        # GPU usage
        gpu_usage = self.get_gpu_usage()

        # Temperature
        temp = self.get_gpu_temperature()

        metrics = {
            "available_ram_gb": available_ram_gb,
            "available_vram_gb": available_vram_gb,
            "cpu_usage_pct": round(cpu_usage, 2),
            "gpu_usage_pct": round(gpu_usage, 2) if gpu_usage else None,
            "temperature_c": temp,
            "bandwidth_mbps": self.config.get('bandwidth_mbps'),
            "latitude": self.config.get('latitude'),
            "longitude": self.config.get('longitude')
        }

        return metrics

    def get_available_vram(self):
        """
        Get available VRAM in GB

        Returns:
            Available VRAM in GB across all GPUs
        """
        if not GPU_AVAILABLE:
            return 0

        try:
            device_count = pynvml.nvmlDeviceGetCount()
            available_vram = 0
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                available_vram += info.free
            return int(available_vram / (1024**3))
        except Exception:
            return 0

    def get_gpu_usage(self):
        """
        Get GPU utilization percentage

        Returns:
            GPU utilization percentage or None
        """
        if not GPU_AVAILABLE:
            return None

        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return util.gpu
        except Exception:
            return None

    def get_gpu_temperature(self):
        """
        Get GPU temperature in Celsius

        Returns:
            GPU temperature or None
        """
        if not GPU_AVAILABLE:
            return None

        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            temp = pynvml.nvmlDeviceGetTemperature(
                handle,
                pynvml.NVML_TEMPERATURE_GPU
            )
            return temp
        except Exception:
            return None

    def send_heartbeat(self, metrics):
        """
        Send heartbeat to API

        Args:
            metrics: Dictionary of metrics to send

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/nodes/{self.node_id}/heartbeat",
                headers={"X-API-Key": self.api_key},
                json=metrics,
                timeout=10
            )

            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] ✅ Heartbeat sent | "
                      f"RAM: {metrics['available_ram_gb']}GB | "
                      f"VRAM: {metrics['available_vram_gb']}GB | "
                      f"CPU: {metrics['cpu_usage_pct']}%"
                      f"{f' | GPU: {metrics['gpu_usage_pct']}%' if metrics['gpu_usage_pct'] else ''}")
                return True
            else:
                print(f"❌ Heartbeat failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except requests.exceptions.Timeout:
            print("❌ Heartbeat timeout")
            return False
        except Exception as e:
            print(f"❌ Heartbeat error: {str(e)}")
            return False

    def run(self):
        """Main loop - send heartbeats continuously"""
        print("\n" + "="*60)
        print("🧠 MNEMO Node Agent")
        print("="*60)
        print(f"Node Name:     {self.config['name']}")
        print(f"Node ID:       {self.node_id}")
        print(f"Node Type:     {self.config['node_type']}")
        print(f"Region:        {self.config['region']}")
        print(f"API URL:       {self.api_url}")
        print(f"Heartbeat:     Every {self.heartbeat_interval} seconds")
        print(f"GPU Support:   {'✅ Enabled' if GPU_AVAILABLE else '❌ Disabled'}")
        print("="*60)
        print("\nPress Ctrl+C to stop\n")

        consecutive_failures = 0
        max_failures = 5

        try:
            while True:
                metrics = self.collect_metrics()
                success = self.send_heartbeat(metrics)

                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        print(f"\n❌ Too many consecutive failures ({max_failures})")
                        print("   Please check your API configuration and network connection")
                        break

                time.sleep(self.heartbeat_interval)

        except KeyboardInterrupt:
            print("\n\n⏹ Stopping node agent...")
            if GPU_AVAILABLE:
                pynvml.nvmlShutdown()
            print("✅ Agent stopped cleanly.")
            sys.exit(0)


def main():
    """Main entry point"""
    try:
        agent = MnemoNodeAgent()
        agent.run()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

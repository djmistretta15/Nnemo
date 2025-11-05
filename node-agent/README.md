# MNEMO Node Agent

The Node Agent runs on provider machines (data centers, edge clusters, or mist nodes) to report memory availability to the MNEMO platform.

## Features

- 🔍 Monitors RAM and VRAM availability in real-time
- 📊 Tracks CPU and GPU utilization
- 🌡️ Reports GPU temperature
- 🔄 Sends periodic heartbeats to the platform
- 🔌 Automatic node registration
- ⚡ Lightweight and efficient

## Requirements

- Python 3.7+
- psutil library
- nvidia-ml-py (optional, for GPU monitoring)

## Installation

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **For GPU monitoring (optional):**

If you have an NVIDIA GPU and want to monitor VRAM:

```bash
pip install nvidia-ml-py
```

## Configuration

1. **Copy the example configuration:**

```bash
cp node_config.example.json node_config.json
```

2. **Edit `node_config.json` with your settings:**

```json
{
  "api_url": "http://localhost:8000",
  "api_key": "your_api_key_here",
  "node_type": "mist_node",
  "name": "MyNode_RTX4090",
  "region": "us-east-1",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "price_per_gb_sec": 0.0000008,
  "bandwidth_mbps": 1000,
  "base_latency_ms": 1.0,
  "idle_schedule": "always",
  "heartbeat_interval": 60
}
```

### Configuration Fields

| Field | Description |
|-------|-------------|
| `api_url` | MNEMO API endpoint |
| `api_key` | Your API key (get from MNEMO dashboard) |
| `node_type` | `mist_node`, `edge_cluster`, or `datacenter` |
| `name` | Unique name for your node |
| `region` | Geographic region (e.g., `us-east-1`) |
| `latitude` | Your latitude (for proximity matching) |
| `longitude` | Your longitude (for proximity matching) |
| `price_per_gb_sec` | Price in USD per GB per second |
| `bandwidth_mbps` | Network bandwidth in Mbps |
| `base_latency_ms` | Base network latency in milliseconds |
| `idle_schedule` | When to offer capacity (e.g., "9am-5pm") |
| `heartbeat_interval` | Seconds between heartbeats (default: 60) |

## Usage

### Run the Agent

```bash
python node_agent.py
```

### Run as Background Service (Linux)

Create a systemd service file `/etc/systemd/system/mnemo-agent.service`:

```ini
[Unit]
Description=MNEMO Node Agent
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/node-agent
ExecStart=/usr/bin/python3 /path/to/node-agent/node_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable mnemo-agent
sudo systemctl start mnemo-agent
sudo systemctl status mnemo-agent
```

### Run with Docker

```bash
docker build -t mnemo-agent .
docker run -d --name mnemo-agent \
  -v $(pwd)/node_config.json:/app/node_config.json \
  mnemo-agent
```

## Monitoring

The agent outputs status messages:

```
[2025-01-15 14:30:45] ✅ Heartbeat sent | RAM: 48GB | VRAM: 18GB | CPU: 12.5% | GPU: 8.3%
```

## Troubleshooting

### GPU Not Detected

If you have an NVIDIA GPU but it's not detected:

1. Install nvidia-ml-py: `pip install nvidia-ml-py`
2. Verify NVIDIA drivers are installed: `nvidia-smi`
3. Check CUDA is accessible

### Connection Errors

If heartbeats fail:

1. Verify `api_url` is correct
2. Check your API key is valid
3. Ensure network connectivity to the MNEMO platform
4. Check firewall settings

### High CPU Usage

If the agent uses too much CPU:

1. Increase `heartbeat_interval` in config (e.g., 120 seconds)
2. Reduce monitoring frequency

## Security Notes

- **API Key:** Keep your `node_config.json` secure. Never commit it to version control.
- **Firewall:** The agent only makes outbound connections to the MNEMO API.
- **Permissions:** The agent only reads system metrics, it doesn't modify anything.

## Support

For issues or questions:
- GitHub Issues: [github.com/mnemo/issues](https://github.com/mnemo/issues)
- Documentation: [docs.mnemo.io](https://docs.mnemo.io)
- Discord: [discord.gg/mnemo](https://discord.gg/mnemo)

## License

MIT License - See LICENSE file for details

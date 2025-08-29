# Shopping List Application - Raspberry Pi Setup Guide

This guide will help you install and configure the Shopping List application on your Raspberry Pi to run automatically on boot.

## Prerequisites

- Raspberry Pi running Raspberry Pi OS
- Internet connection
- SSH access or direct terminal access

## Installation Steps

### 1. Update Your Raspberry Pi

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required System Packages

```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### 3. Create Application Directory and Copy Files

```bash
# Create the application directory
sudo mkdir -p /home/pi/shopping-list
sudo chown pi:pi /home/pi/shopping-list

# Copy your application files to the Raspberry Pi
# You can use scp, rsync, or git clone depending on your setup
# Example using scp from your local machine:
# scp -r /path/to/shopping-list/* pi@your-pi-ip:/home/pi/shopping-list/
```

### 4. Set Up the Application

```bash
cd /home/pi/shopping-list

# Make the startup scripts executable
chmod +x start_shopping_list.sh
chmod +x stop_shopping_list.sh

# Test the application manually first
./start_shopping_list.sh
```

### 5. Configure Environment Variables (Recommended)

For security, set up proper credentials:

```bash
# Edit the systemd service file to update credentials
sudo nano shopping-list.service

# Update these lines with secure values:
Environment=SECRET_KEY=your-very-secure-secret-key-here
Environment=ADMIN_USERNAME=your-admin-username
Environment=ADMIN_PASSWORD=your-secure-password-here
```

### 6. Install the Systemd Service

```bash
# Copy the service file to systemd directory
sudo cp shopping-list.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable shopping-list.service

# Start the service now
sudo systemctl start shopping-list.service
```

### 7. Verify Installation

```bash
# Check service status
sudo systemctl status shopping-list.service

# Check if the application is accessible
curl http://localhost:5000

# View application logs
tail -f /home/pi/shopping-list/shopping_list.log
```

## Managing the Service

### Manual Control Commands

```bash
# Start the service
sudo systemctl start shopping-list.service

# Stop the service
sudo systemctl stop shopping-list.service

# Restart the service
sudo systemctl restart shopping-list.service

# Check service status
sudo systemctl status shopping-list.service

# View service logs
sudo journalctl -u shopping-list.service -f
```

### Direct Script Control

```bash
cd /home/pi/shopping-list

# Start manually
./start_shopping_list.sh

# Stop manually
./stop_shopping_list.sh
```

## Accessing the Application

- **Local access**: http://localhost:5000
- **Network access**: http://[pi-ip-address]:5000
- **Default credentials**: admin/admin (change these in production!)

## Troubleshooting

### Service won't start

1. Check service status: `sudo systemctl status shopping-list.service`
2. Check application logs: `tail -f /home/pi/shopping-list/shopping_list.log`
3. Check systemd logs: `sudo journalctl -u shopping-list.service -n 50`

### Permission issues

```bash
# Fix ownership
sudo chown -R pi:pi /home/pi/shopping-list

# Fix script permissions
chmod +x /home/pi/shopping-list/*.sh
```

### Can't access from other devices

1. Check if the Pi's firewall allows port 5000:
```bash
sudo ufw allow 5000
```

2. Modify `app.py` to listen on all interfaces (line 118):
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Database issues

```bash
# Check if database file exists and has correct permissions
ls -la /home/pi/shopping-list/shopping_list.db
sudo chown pi:pi /home/pi/shopping-list/shopping_list.db
```

## Security Recommendations

1. **Change default credentials** in the systemd service file
2. **Generate a secure secret key**:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **Enable HTTPS** for production use by setting `FORCE_HTTPS=true`
4. **Restrict network access** using firewall rules if needed

## Uninstallation

To remove the service:

```bash
# Stop and disable the service
sudo systemctl stop shopping-list.service
sudo systemctl disable shopping-list.service

# Remove the service file
sudo rm /etc/systemd/system/shopping-list.service

# Reload systemd
sudo systemctl daemon-reload

# Remove application directory
rm -rf /home/pi/shopping-list
```

## Files Created

- `start_shopping_list.sh` - Main startup script
- `stop_shopping_list.sh` - Stop script
- `shopping-list.service` - Systemd service configuration
- `shopping_list.log` - Application log file (created at runtime)
- `shopping_list.pid` - Process ID file (created at runtime)
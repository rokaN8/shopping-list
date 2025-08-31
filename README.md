# Shopping List Web App 🛒

A secure, mobile-friendly shopping list web application designed to run on Raspberry Pi with internet access via port forwarding. Features HTTPS encryption, basic authentication, and automatic startup on boot.

## Features

- ✅ **Secure Access**: HTTP Basic Authentication with configurable credentials
- 🔒 **HTTPS Support**: Self-signed SSL certificates for encrypted connections
- 📱 **Mobile Friendly**: Responsive design optimized for mobile devices
- 🔄 **Real-time Updates**: Dynamic list management without page reloads
- ⚡ **Auto-start**: Systemd service for automatic startup on Raspberry Pi boot
- 🌐 **Internet Access**: Designed for port forwarding and remote access
- 💾 **SQLite Database**: Lightweight, file-based data storage

## Quick Start

### Windows 11 Testing

1. **Download and extract** the shopping-list folder
2. **Run setup**: Double-click `setup_windows.bat`
3. **Start app**: Double-click `run_windows.bat`
4. **Access**: Open https://localhost:7666 in your browser

### Raspberry Pi Deployment

1. **Transfer files** to your Raspberry Pi
2. **Make executable**: `chmod +x setup_pi.sh`
3. **Run setup**: `./setup_pi.sh`
4. **Configure router**: Forward port 7666 to your Pi's IP address
5. **Access**: Visit https://YOUR_PI_IP:7666 from any device

## Installation Guide

### Prerequisites

#### Windows 11
- Python 3.7 or later ([Download here](https://python.org))
- Make sure "Add Python to PATH" is checked during installation

#### Raspberry Pi
- Raspberry Pi OS (or similar Debian-based system)
- SSH access (for remote setup)
- Internet connection

### Windows 11 Setup

1. **Download Python**: Install Python 3.7+ from python.org if not already installed
2. **Extract Files**: Download and extract the shopping-list folder to your desired location
3. **Run Setup Script**:
   ```batch
   # Double-click setup_windows.bat or run in Command Prompt
   setup_windows.bat
   ```
4. **Start Application**:
   ```batch
   # Double-click run_windows.bat or run in Command Prompt
   run_windows.bat
   ```

The app will be available at:
- HTTPS: https://localhost:7666 (if certificates generated successfully)
- HTTP: http://localhost:7666 (fallback)

### Raspberry Pi Setup

1. **Transfer Files**: Use SCP, SFTP, or copy files to your Raspberry Pi
   ```bash
   # Example using SCP
   scp -r shopping-list pi@YOUR_PI_IP:~/
   ```

2. **Connect via SSH**:
   ```bash
   ssh pi@YOUR_PI_IP
   cd ~/shopping-list
   ```

3. **Make Setup Script Executable**:
   ```bash
   chmod +x setup_pi.sh
   ```

4. **Run Setup Script**:
   ```bash
   ./setup_pi.sh
   ```

5. **Configure Service** (done automatically by setup script):
   ```bash
   # Check service status
   sudo systemctl status shopping-list
   
   # Start service
   sudo systemctl start shopping-list
   
   # View logs
   sudo journalctl -u shopping-list -f
   ```

## Configuration

### Environment Variables

Create or edit the `.env` file to customize settings:

```bash
# Authentication credentials
SHOPPING_USERNAME=your_username
SHOPPING_PASSWORD=your_secure_password

# Application security key
SECRET_KEY=your-random-secret-key-here
```

### Default Credentials

- **Username**: admin
- **Password**: password123

**⚠️ Important**: Change these default credentials before exposing to the internet!

### Port Configuration

The application runs on **port 7666** by default. To change this:

1. Edit `config.py`
2. Modify the `PORT = 7666` line
3. Update your port forwarding configuration accordingly

## Router Configuration (Port Forwarding)

To access your shopping list from the internet:

1. **Find your Pi's IP address**:
   ```bash
   hostname -I
   ```

2. **Access your router's admin panel** (usually 192.168.1.1 or 192.168.0.1)

3. **Set up port forwarding**:
   - External Port: 7666
   - Internal Port: 7666
   - Internal IP: Your Pi's IP address
   - Protocol: TCP

4. **Find your public IP**: Visit whatismyipaddress.com

5. **Access from internet**: https://YOUR_PUBLIC_IP:7666

## SSL Certificates

### Automatic Generation

SSL certificates are automatically generated during setup. If you need to regenerate them:

```bash
# Windows
python generate_certs.py

# Raspberry Pi
python3 generate_certs.py
```

### Browser Security Warnings

Since we use self-signed certificates, browsers will show security warnings. This is normal and safe for personal use. Click "Advanced" → "Proceed to localhost (unsafe)" or similar.

### Production SSL (Optional)

For a production setup without browser warnings:

1. **Use Let's Encrypt** with a domain name
2. **Use Cloudflare Tunnel** for secure access without port forwarding
3. **Purchase a SSL certificate** from a trusted CA

## Usage

### Adding Items
- Type in the input field and press Enter or click "Add"
- Items are saved automatically

### Managing Items
- **Complete**: Click the checkbox next to an item
- **Edit**: Click on the item text to edit inline
- **Delete**: Click the ✕ button
- **Clear Completed**: Use the "Clear Completed" button to remove all finished items

### Mobile Access
The interface is optimized for mobile devices with:
- Large touch targets
- Responsive layout
- Mobile-friendly forms

## System Management

### Raspberry Pi Service Commands

```bash
# Start the service
sudo systemctl start shopping-list

# Stop the service
sudo systemctl stop shopping-list

# Restart the service
sudo systemctl restart shopping-list

# Check service status
sudo systemctl status shopping-list

# View real-time logs
sudo journalctl -u shopping-list -f

# Disable auto-start
sudo systemctl disable shopping-list

# Enable auto-start
sudo systemctl enable shopping-list
```

### Updating Configuration

After changing `.env` file:
```bash
sudo systemctl restart shopping-list
```

## File Structure

```
shopping-list/
├── app.py                    # Main Flask application
├── database.py              # Database operations
├── config.py                # Configuration settings
├── generate_certs.py        # SSL certificate generation
├── requirements.txt         # Python dependencies
├── setup_windows.bat        # Windows setup script
├── setup_pi.sh             # Raspberry Pi setup script
├── run_windows.bat          # Windows run script
├── shopping-list.service    # Systemd service template
├── .env                     # Environment variables (created during setup)
├── static/
│   ├── style.css           # Responsive CSS
│   └── script.js           # Frontend JavaScript
├── templates/
│   └── index.html          # Main HTML template
├── certs/                  # SSL certificates (generated)
│   ├── cert.pem
│   └── key.pem
├── venv/                   # Python virtual environment
└── shopping_list.db        # SQLite database (created automatically)
```

## Troubleshooting

### Common Issues

**Python not found (Windows)**:
- Install Python from python.org
- Make sure "Add Python to PATH" was checked
- Restart Command Prompt after installation

**Permission denied (Raspberry Pi)**:
```bash
chmod +x setup_pi.sh
```

**Service won't start**:
```bash
# Check logs for errors
sudo journalctl -u shopping-list -f

# Common fixes:
sudo systemctl daemon-reload
sudo systemctl restart shopping-list
```

**Can't access from internet**:
- Check port forwarding configuration
- Verify firewall settings
- Confirm Pi's local IP hasn't changed
- Test local access first: https://PI_LOCAL_IP:7666

**SSL certificate issues**:
```bash
# Regenerate certificates
python3 generate_certs.py
sudo systemctl restart shopping-list
```

### Logs and Debugging

**View application logs**:
```bash
# Raspberry Pi
sudo journalctl -u shopping-list -f

# Windows (run from Command Prompt in shopping-list folder)
python app.py
```

**Database issues**:
- Database file: `shopping_list.db`
- Delete to reset: `rm shopping_list.db` (will recreate automatically)

## Security Considerations

### For Personal Use
- Change default credentials
- Use HTTPS when possible
- Keep your Pi updated: `sudo apt update && sudo apt upgrade`

### For Public Access
- Use strong passwords
- Consider additional authentication layers
- Monitor access logs regularly
- Keep software updated

### Network Security
- Use WPA3 WiFi security
- Consider VPN access instead of port forwarding
- Regular router firmware updates

## License

This project is provided as-is for personal use. Feel free to modify and customize for your needs.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify your setup matches the requirements
3. Check system logs for error messages
4. Try regenerating SSL certificates
5. Test on local network before internet access

---

**Happy Shopping!** 🛒
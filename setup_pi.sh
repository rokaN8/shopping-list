#!/bin/bash

echo "Setting up Shopping List App for Raspberry Pi..."
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}WARNING: Running as root is not recommended.${NC}"
    echo "Consider running as a regular user and using sudo only when needed."
fi

# Update system packages
echo -e "${BLUE}Updating system packages...${NC}"
sudo apt update

# Install Python 3 and pip if not already installed
echo -e "${BLUE}Installing Python 3 and pip...${NC}"
sudo apt install -y python3 python3-pip python3-venv

# Check Python version
echo -e "${BLUE}Python version:${NC}"
python3 --version

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to create virtual environment.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python packages
echo -e "${BLUE}Installing Python packages...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install requirements.${NC}"
    exit 1
fi

# Generate SSL certificates
echo -e "${BLUE}Generating SSL certificates...${NC}"
python3 generate_certs.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}WARNING: Failed to generate SSL certificates. HTTPS will not be available.${NC}"
fi

# Set up environment variables
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${BLUE}Creating environment configuration...${NC}"
    cat > "$ENV_FILE" << 'EOL'
# Shopping List App Configuration
SHOPPING_USERNAME=admin
SHOPPING_PASSWORD=password123
SECRET_KEY=change-this-secret-key-in-production
EOL
    echo -e "${YELLOW}Default credentials created in .env file${NC}"
    echo "Username: admin"
    echo "Password: password123"
    echo -e "${YELLOW}Please edit .env file to change these credentials!${NC}"
else
    echo -e "${GREEN}Environment file already exists.${NC}"
fi

# Create systemd service file
SERVICE_FILE="/tmp/shopping-list.service"
cat > "$SERVICE_FILE" << EOL
[Unit]
Description=Shopping List Web App
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/venv/bin
EnvironmentFile=$SCRIPT_DIR/.env
ExecStart=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Install systemd service
echo -e "${BLUE}Installing systemd service...${NC}"
sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable shopping-list.service

echo
echo -e "${GREEN}===== SETUP COMPLETE =====${NC}"
echo
echo -e "${GREEN}Your shopping list app is ready!${NC}"
echo
echo -e "${BLUE}Service Management:${NC}"
echo "  Start service:    sudo systemctl start shopping-list"
echo "  Stop service:     sudo systemctl stop shopping-list"
echo "  Restart service:  sudo systemctl restart shopping-list"
echo "  View logs:        sudo journalctl -u shopping-list -f"
echo
echo -e "${BLUE}Configuration:${NC}"
echo "  Edit credentials: nano $ENV_FILE"
echo "  After changes:    sudo systemctl restart shopping-list"
echo
echo -e "${BLUE}Network Access:${NC}"
echo "  Local access:     https://localhost:7666 or http://localhost:7666"
echo "  Network access:   https://YOUR_PI_IP:7666 or http://YOUR_PI_IP:7666"
echo "  Port forwarding:  Configure router to forward port 7666 to this Pi"
echo
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit .env file to set your desired username and password"
echo "2. Start the service: sudo systemctl start shopping-list"
echo "3. Configure port forwarding on your router (port 7666)"
echo "4. Access your shopping list from anywhere!"
echo
echo -e "${RED}Security Note:${NC}"
echo "This uses a self-signed certificate. Your browser will show warnings."
echo "For production, consider using Let's Encrypt or a proper SSL certificate."
echo

# Ask if user wants to start the service now
read -p "Do you want to start the shopping list service now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start shopping-list
    echo -e "${GREEN}Service started!${NC}"
    echo "Check status with: sudo systemctl status shopping-list"
fi
#!/bin/bash
set -e

echo "========================================"
echo " Quantum Mirror — Pi Setup"
echo "========================================"

# System packages
echo ""
echo "[1/5] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "[2/5] Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-opencv \
    libatlas-base-dev \
    libopenblas-dev \
    libbluetooth-dev \
    bluetooth \
    bluez \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    exfat-fuse \
    exfat-utils

# Python packages
echo ""
echo "[3/5] Installing Python dependencies..."
pip3 install -r requirements-pi.txt --break-system-packages

# Mount external storage
echo ""
echo "[4/5] Setting up external storage mount..."
sudo mkdir -p /mnt/storage

if grep -q "/mnt/storage" /etc/fstab; then
    echo "  → /mnt/storage already in /etc/fstab, skipping."
else
    echo ""
    echo "  Available USB drives:"
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | grep -E "sd[a-z]"
    echo ""
    read -p "  Enter device to mount (e.g. sda1), or 'skip' to do later: " DEVICE

    if [ "$DEVICE" != "skip" ]; then
        sudo mount /dev/$DEVICE /mnt/storage
        echo "/dev/$DEVICE  /mnt/storage  auto  defaults,nofail  0  2" | sudo tee -a /etc/fstab
        echo "  → Mounted /dev/$DEVICE at /mnt/storage and added to fstab."
    else
        echo "  → Skipped. Mount manually later with: sudo mount /dev/sdX1 /mnt/storage"
    fi
fi

# Create directory structure on external storage
sudo mkdir -p /mnt/storage/models
sudo mkdir -p /mnt/storage/database
for category in scientists engineers entrepreneurs; do
    sudo mkdir -p /mnt/storage/database/$category/images
done
sudo chown -R $USER:$USER /mnt/storage

# Bluetooth setup
echo ""
echo "[5/5] Enabling Bluetooth..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

echo ""
echo "========================================"
echo " Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Copy mobilefacenet.onnx into /mnt/storage/models/"
echo "  2. Run precompute_embeddings.py on your laptop to generate embeddings"
echo "  3. Copy the database/ folder to /mnt/storage/database/"
echo "  4. Pair the ESP32: bluetoothctl → scan on → pair <MAC>"
echo "  5. Run: python3 -m src.main"
echo ""
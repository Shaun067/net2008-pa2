# Shaun Jacob, ID: 041271370
import sys
import xml.etree.ElementTree as ET


def main():
    """Print the id of every device in the inventory."""
    path = sys.argv[1]
    root = ET.parse(path).getroot()
    for device in root.findall("device"):
        device_id = device.get("id")
        if device_id is not None:
            print(device_id)


if __name__ == "__main__":
    main()
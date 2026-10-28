# Shaun Jacob, ID: 041271370
import sys
import xml.etree.ElementTree as ET
import json

class Device:
    """One network device from the inventory."""

    def __init__(self, device_id, role, os_version, owner, interfaces):
        self.device_id = device_id
        self.role = role
        self.os_version = os_version
        self.owner = owner            
        self.interfaces = interfaces  

    def has_owner(self):
        """Return True if the device has a non-empty owner."""
        if self.owner is None:
            return False
        return self.owner.strip() != ""
        
def main():
    
    path = sys.argv[1]
    root = ET.parse(path).getroot()

    devices = []
    skipped = 0

    for element in root.findall("device"):
        device_id = element.get("id")
        if device_id is None:
            skipped += 1
            continue

        role = element.get("role")
        os_version = element.get("os")

        owner_element = element.find("owner")
        if owner_element is None:
            owner = None
        else:
            owner = owner_element.text 

        interfaces = []
        for iface in element.findall("interface"):
            interfaces.append(iface.get("status"))

        devices.append(Device(device_id, role, os_version, owner, interfaces))
    roles = {}
    for device in devices:
        roles[device.role] = roles.get(device.role, 0) + 1
    interface_counts = {"up": 0, "down": 0, "other": 0}
    for device in devices:
        for status in device.interfaces:
            if status == "up":
                interface_counts["up"] += 1
            elif status == "down":
                interface_counts["down"] += 1
            else:
                interface_counts["other"] += 1

    report = {
        "site": root.get("site"),
        "total_devices": len(devices),
        "skipped_devices": skipped,
        "roles": roles,
        "interfaces": interface_counts,
    }
    with open("audit.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Wrote audit.json:", len(devices), "devices,", skipped, "skipped")

if __name__ == "__main__":
    main()
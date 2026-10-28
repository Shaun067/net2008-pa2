# Shaun Jacob, ID: 041271370
import sys
import xml.etree.ElementTree as ET

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
    report = {
        "site": root.get("site"),
        "total_devices": len(devices),
        "skipped_devices": skipped,
        "roles": roles,
    }
    print(report)

if __name__ == "__main__":
    main()
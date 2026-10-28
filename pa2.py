# Shaun Jacob, ID: 041271370
import sys
import xml.etree.ElementTree as ET
import json
import yaml

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

def load_policy(path):
    """Load the YAML policy file and return it as a dictionary."""
    with open(path) as f:
        policy = yaml.safe_load(f)
    if policy is None:
        policy = {}
    return policy

def parse_version(text):
    """Turn a version string like '15.10' into a list of ints [15, 10]."""
    return [int(part) for part in text.split(".")]

def compare_versions(a, b):
    """Return -1 if a < b, 0 if equal, 1 if a > b"""
    left = parse_version(a)
    right = parse_version(b)
    length = max(len(left), len(right))
    left += [0] * (length - len(left))
    right += [0] * (length - len(right))
    if left < right:
        return -1
    if left > right:
        return 1
    return 0

def main():
    
    path = sys.argv[1]
    root = ET.parse(path).getroot()
    policy = load_policy(sys.argv[2])

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

    violations = []
    min_os = policy.get("min_os")
    max_down = policy.get("max_down_interfaces")

    for device in devices:
        if min_os is not None and device.role not in min_os:
            violations.append({
                "device": device.device_id,
                "type": "unknown_role",
                "role": device.role,
            })
        if policy.get("require_owner") is True and not device.has_owner():
            violations.append({
                "device": device.device_id,
                "type": "missing_owner",
            })
        if max_down is not None:
            down = device.interfaces.count("down")
            if down > max_down:
                violations.append({
                    "device": device.device_id,
                    "type": "too_many_down",
                    "down": down,
                })
        if min_os is not None and device.role in min_os and device.os_version:
            required = min_os[device.role]
            if compare_versions(device.os_version, required) < 0:
                violations.append({
                    "device": device.device_id,
                    "type": "os_outdated",
                    "found": device.os_version,
                    "required": required,
                })

    violating_ids = {v["device"] for v in violations}
    compliant = sorted(
        d.device_id for d in devices if d.device_id not in violating_ids
    )
    report = {
        "site": root.get("site"),
        "total_devices": len(devices),
        "skipped_devices": skipped,
        "roles": roles,
        "interfaces": interface_counts,
        "violations": violations,
        "compliant": compliant,
    }
    with open("audit.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Wrote audit.json:", len(devices), "devices,", skipped, "skipped")

if __name__ == "__main__":
    main()
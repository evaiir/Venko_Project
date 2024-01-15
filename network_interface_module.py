import os
import subprocess


class NetworkDevices:
    def __init__(self, net_dir="/sys/class/net/"):
        self.net_dir = net_dir

    def _get_network_interfaces(self):
        try:
            interfaces = [
                file
                for file in os.listdir(self.net_dir)
                if os.path.isdir(self.net_dir + file)
            ]
            interfaces.sort()
            return interfaces
        except OSError as e:
            print(f"Error reading network interfaces: {e}")
            return []

    def _get_mac_address(self, interface):
        try:
            with open(self.net_dir + interface + "/address", "r") as mac:
                return mac.read().strip()
        except FileNotFoundError:
            return "N/A"

    def _get_mtu_value(self, interface):
        try:
            with open(self.net_dir + interface + "/mtu", "r") as mtu:
                return mtu.read().strip()
        except FileNotFoundError:
            return "N/A"

    def _get_interface_state(self, interface):
        try:
            with open(self.net_dir + interface + "/operstate", "r") as state:
                return state.read().strip()
        except FileNotFoundError:
            return "N/A"

    def _get_ip_address(self, interface):
        try:
            command_output = subprocess.run(
                ["ip", "-4", "addr", "show", interface], capture_output=True, text=True
            )
            lines = command_output.stdout.splitlines()
            if lines:
                ip_address = lines[1].split()[1]
                return ip_address
        except subprocess.CalledProcessError:
            pass

        return "N/A"

    def _print_table(self, table):
        column_widths = [max(map(len, map(str, col))) + 8 for col in zip(*table)]

        row_format = "".join(
            ["{:<" + str(longest_col) + "}" for longest_col in column_widths]
        )
        for row in table:
            print(row_format.format(*row))

    def show_interfaces(self):
        interfaces = self._get_network_interfaces()
        if not interfaces:
            return
        data_output = [
            ["Interface Name", "IP Address", "MAC Address", "MTU value", "State"]
        ]
        for intf in interfaces:
            line = []
            line.append(intf)
            line.append(self._get_ip_address(intf))
            line.append(self._get_mac_address(intf))
            line.append(self._get_mtu_value(intf))
            line.append(self._get_interface_state(intf))
            data_output.append(line)
        self._print_table(data_output)


if __name__ == "__main__":
    network_info = NetworkDevices()
    network_info.show_interfaces()

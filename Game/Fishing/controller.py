import time
import random
from dynamixel_sdk import PortHandler, PacketHandler


class DynamixelController:
    # Control table addresses
    ADDR_TORQUE_ENABLE    = 64
    ADDR_GOAL_POSITION    = 116
    ADDR_PRESENT_POSITION = 132
    ADDR_PROFILE_VELOCITY = 112

    # Communication settings
    PROTOCOL_VERSION = 2.0
    DXL_IDS          = [1, 2]
    BAUDRATE         = 1000000
    DEVICENAME       = "COM3"

    # Torque settings
    TORQUE_ENABLE  = 1
    TORQUE_DISABLE = 0

    def __init__(self):
        self.portHandler = PortHandler(self.DEVICENAME)
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

        # Mid offset values for each motor
        self.dxl_config = {
            1: {"mid_offset": 930},  # Motor H
            2: {"mid_offset": 995},  # Motor D
        }

    def initialize(self):
        if not self.portHandler.openPort():
            print("Failed to open port.")
            return False
        if not self.portHandler.setBaudRate(self.BAUDRATE):
            print("Failed to set baud rate.")
            return False

        # Enable torque for all motors
        for dxl_id in self.DXL_IDS:
            self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
        print("Initialization successful.")
        return True

    def read_current_position(self):
        positions = {}
        for dxl_id in self.DXL_IDS:
            pos_raw, _, _ = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id, self.ADDR_PRESENT_POSITION)
            pos_mod = pos_raw % 4096
            mid = self.dxl_config[dxl_id]["mid_offset"]
            pos = pos_mod - mid
            positions[dxl_id] = pos
            print(f"Motor {dxl_id} current centered position: {pos}")
        return positions

    def move_to_position(self, dxl_id, position_sequence):
        """
        Move the specified motor through a sequence of positions.
        Other motors remain idle.
        :param dxl_id: Motor ID (1 or 2)
        :param position_sequence: List of positions, e.g. [-334, 0]
        """
        mid = self.dxl_config[dxl_id]["mid_offset"]

        for pos in position_sequence:
            speed = 100
            raw = pos + mid
            self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, self.ADDR_PROFILE_VELOCITY, speed)
            self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, self.ADDR_GOAL_POSITION, raw)
            print(f" Moving to {pos} (raw: {raw}) with speed {speed}")
            time.sleep(1)

    def close(self):
        for dxl_id in self.DXL_IDS:
            self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
        self.portHandler.closePort()
        print("Motors turned off and port closed.")


if __name__ == "__main__":
    controller = DynamixelController()

    if controller.initialize():
        controller.read_current_position()

        # Reset both motors to center
        controller.move_to_position(1, [0])
        controller.move_to_position(2, [0])

        # Motor 1: move to 300, then back to 0
        controller.move_to_position(1, [300, 0])

        # Motor 2: move to 300, then back to 0
        controller.move_to_position(2, [300, 0])

        controller.close()
    else:
        print("Initialization failed.")

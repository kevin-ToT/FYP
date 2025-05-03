import time
from dynamixel_sdk import PortHandler, PacketHandler
import random

class DynamixelController:
    # Control table addresses
    ADDR_TORQUE_ENABLE    = 64
    ADDR_GOAL_POSITION    = 116
    ADDR_PRESENT_POSITION = 132
    ADDR_PROFILE_VELOCITY = 112

    # Communication settings
    PROTOCOL_VERSION = 2.0
    BAUDRATE = 1000000
    DEVICENAME = "COM3"

    # Torque settings
    TORQUE_ENABLE = 1
    TORQUE_DISABLE = 0

    def __init__(self, dxl_id: int, mid_offset: int):
        """
        Initialize the controller for a specific Dynamixel ID and mid offset.
        """
        self.DXL_ID = dxl_id
        self.MID_OFFSET = mid_offset

        # Initialize port and packet handlers
        self.portHandler = PortHandler(self.DEVICENAME)
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

    def initialize(self):
        """
        Open port and enable torque.
        """
        if not self.portHandler.openPort():
            print("Failed to open port.")
            return False
        if not self.portHandler.setBaudRate(self.BAUDRATE):
            print("Failed to set baud rate.")
            return False
        
        # Enable torque
        self.packetHandler.write1ByteTxRx(
            self.portHandler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
        print(f"Initialization successful for Dynamixel ID {self.DXL_ID}.")
        return True

    def read_current_position(self):
        """
        Read the current motor position.
        """
        position, _, _ = self.packetHandler.read4ByteTxRx(
            self.portHandler, self.DXL_ID, self.ADDR_PRESENT_POSITION)
        position_mod = position % 4096
        pos = position_mod - self.MID_OFFSET
        print(f"[DXL {self.DXL_ID}] Current centered position: {pos}")
        return pos

    def move_to_position(self, target_pos):
        """
        Move the motor to the given position(s) with random velocity.
        """
        if isinstance(target_pos, list) and len(target_pos) == 2:
            for pos in target_pos:
                self._move_single_position(pos)
        else:
            self._move_single_position(target_pos)

    def _move_single_position(self, pos):
        random_speed = random.randint(100, 500)
        self.packetHandler.write4ByteTxRx(
            self.portHandler, self.DXL_ID, self.ADDR_PROFILE_VELOCITY, random_speed)
        target_raw = pos + self.MID_OFFSET
        self.packetHandler.write4ByteTxRx(
            self.portHandler, self.DXL_ID, self.ADDR_GOAL_POSITION, target_raw)
        print(f"[DXL {self.DXL_ID}] Moving to position: {pos} with velocity {random_speed}")
        time.sleep(1)

    def close(self):
        """
        Disable torque and close port.
        """
        self.packetHandler.write1ByteTxRx(
            self.portHandler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
        self.portHandler.closePort()
        print(f"[DXL {self.DXL_ID}] Motor turned off.")

# ---------------- MAIN PROGRAM ----------------

if __name__ == "__main__":

    # Create two controllers for two different motors
    controller_H = DynamixelController(dxl_id=1, mid_offset=930)  # Horizontal motor
    controller_D = DynamixelController(dxl_id=2, mid_offset=995)  # Directional motor

    # Initialize both
    initialized_H = controller_H.initialize()
    initialized_D = controller_D.initialize()

    if initialized_H and initialized_D:
        # Read initial positions
        pos_H = controller_H.read_current_position()
        pos_D = controller_D.read_current_position()

        # Example movements
        controller_H.move_to_position(0)             # center H
        controller_D.move_to_position(0)             # center D

        controller_H.move_to_position([-600, 0])
        controller_D.move_to_position([300, 0])

        # Return to center
        controller_H.move_to_position(0)
        controller_D.move_to_position(0)

        # Close both
        controller_H.close()
        controller_D.close()

    else:
        print("One or both controllers failed to initialize.")


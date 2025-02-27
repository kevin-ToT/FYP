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
    DXL_ID           = 2
    BAUDRATE         = 1000000
    DEVICENAME       = "COM3"

    # Torque settings
    TORQUE_ENABLE  = 1
    TORQUE_DISABLE = 0

    MID_OFFSET = 995

    def __init__(self):
        # Initialize port and packet handlers
        self.portHandler = PortHandler(self.DEVICENAME)
        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

    def initialize(self):
        """
        Open port and enable torque. 开启
        """
        if not self.portHandler.openPort():
            print("Failed to open port.")
            return False
        if not self.portHandler.setBaudRate(self.BAUDRATE):
            print("Failed to set baud rate.")
            return False
        
        # Enable torque
        self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
        # self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)

        print("Initialization successful.")
        return True

    def read_current_position(self):
        """
        Read the current motor position.读取
        """
        position, _, _ = self.packetHandler.read4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_PRESENT_POSITION)
        position_mod = position % 4096
        pos  = position_mod - self.MID_OFFSET
        print(f"Current centered position: {pos}")
        return pos

    def move_to_position(self, target_pos):
        """
        Move the motor to the given positions with random velocity.移动
        """
        if isinstance(target_pos, list) and len(target_pos) == 2:
                for pos in target_pos:
                    random_speed = random.randint(100, 500)
                    self.packetHandler.write4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_PROFILE_VELOCITY, random_speed)
                    target_raw = pos + self.MID_OFFSET
                    self.packetHandler.write4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_GOAL_POSITION, target_raw)
                    print(f"Moving to position: {pos} with velocity {random_speed}")
                    time.sleep(1)
        else:
            random_speed = random.randint(100, 500)
            self.packetHandler.write4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_PROFILE_VELOCITY, random_speed)
            target_raw = target_pos + self.MID_OFFSET
            self.packetHandler.write4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_GOAL_POSITION, target_raw)
            print(f"Moving to position: {target_pos} with velocity {random_speed}")
            time.sleep(1)
        

    def close(self):
        """
        Disable torque and close port.关闭
        """
        self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
        self.portHandler.closePort()
        print("Motor turned off.")

# Main program
if __name__ == "__main__":

    controller = DynamixelController()
    
    # Initialize
    if controller.initialize():
        # Read current position
        # while True:
            postion = controller.read_current_position()
        
            # Set goal positions [-600, 600]
            controller.move_to_position(0)      # center
            controller.move_to_position([334, 0])    # forward
            controller.move_to_position([334, 0])    # forward

            # Close connection
            controller.close()
    else:
        print("Initialization failed.")

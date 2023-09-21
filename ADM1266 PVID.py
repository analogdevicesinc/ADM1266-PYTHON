# Copyright (c) 2017-2021 Analog Devices Inc.
# All rights reserved.
# www.analog.com

#
# SPDX-License-Identifier: Apache-2.0
#

# Release Notes -----------------------------------------------------------
# This script uses the Aardvark from Total Phase drivers to communicate with ADM1266.
# If you would like to use other devices, please comment out the Aardvark sections below.
# Open PMBus_I2C.py and replace aardvark_py APIs with the dongle APIs that you are using.
# No other modification is required

import PMBus_I2C
import ADM1266_Lib
import sys
import struct
from time import *

if sys.version_info.major < 3:
    input = raw_input

      
def get_user_input(pvid_channel_name):
    rail_data = {
    "PVID_CH_NAME": 0,
    "PVID_GPIOS": 0,
    "PVID_PIN_COUNT": 4,
    "PVID_RESOLUTION": 0.001,
    "PVID_RESOLUTION_EXPONENT": 0,
    "PVID_ENABLE": 0,
    }
    
    print(" ")
    print("Enter PVID Rail Settings:")
    rail_data["PVID_CH_NAME"] = pvid_channel_name
    
    PMBus_I2C.PMBus_Write(0x50, [0xF3, 2, 1, 0]) #to disable channel 1
    ADM1266_Lib.delay(600)
        
    PMBus_I2C.PMBus_Write(0x50, [0xF3, 2, 2, 0]) #to disable channel 2
    ADM1266_Lib.delay(600)  
            
    print(" ")   
    gpio_numbs = []
    print("0: GPIO1     1: GPIO2     2: GPIO3     3: GPIO4     4: GPIO5     5: GPIO6     6: GPIO7     7: GPIO8     8: GPIO9")
   
    for i in range(rail_data["PVID_PIN_COUNT"]):
        while True:
            gpio_input = input(f"Enter the index of {i + 1}st bit's GPIO pin(0-8): ")
            try:
                gpio_index = int(gpio_input)
                if 0 <= gpio_index <= 8:
                    gpio_numbs.append(gpio_index)
                    break  # Valid input, exit the loop
                else:
                    print("Invalid input. GPIO index must be between 0 and 8.")
            except ValueError:
                print("Invalid input. Please enter a valid number between 0 and 8.")
    
    
    print(" ")
    while True:
        resolution_input = input("Enter Resolution (e.g., 0.001): ")
        try:
            resolution = float(resolution_input)
            if resolution >= 0.001:
                rail_data["PVID_RESOLUTION"] = resolution
                break  # Valid input, exit the loop
            else:
                print("Invalid input. Resolution must be greater than or equal to 0.001.")
        except ValueError:
            print("Invalid input. Please enter a valid float number.")
    rail_data["PVID_RESOLUTION_EXPONENT"] = ADM1266_Lib.twosCom_decBin(struct.unpack('B', ADM1266_Lib.get_VOUT_MODE())[0], 5)
    rail_data["PVID_RESOLUTION_EXPONENT"] = ADM1266_Lib.twosCom_binDec((rail_data["PVID_RESOLUTION_EXPONENT"]), 5)
    
    ADM1266_Lib.pvid_config_command(rail_data, gpio_numbs)

    print(" ")
    rail_data["PVID_ENABLE"] = input("PVID is configured, do you want to enable it? (yes/no): ").lower()
    result_cmd = ADM1266_Lib.pvid_mode_command(rail_data)
    print(" ")
    print('PVID status\n0: Disabled (Initial)\n1: Configuration fault (due to wrong parameters)\n2: Dangling Configuration (partially configured)\n3: Successful configuration (can be enabled))\n4: Enabled\n')			
    print('PVID status of Channel 1 : {}'.format(struct.unpack_from('B', result_cmd,  offset=1)[0]))
    print('PVID status of Channel 2 : {}'.format(struct.unpack_from('B', result_cmd,  offset=2)[0]))


if __name__ == '__main__':

    # Open Connection to Aardvark (Comment this section out for using other devices other than Aardvark)
    # If no dongle ID is passed into the function an auto scan will be performed and the first dongle found will be used
    # For using a specific dongle pass the unique ID number, as shown in example below.
    # Example: PMBus_I2C.Open_Aardvark(1845957180)
    PMBus_I2C.Open_Aardvark()

    # PMBus address of all ADM1266 in this design. e.g: [0x40, 0x42]
    ADM1266_Lib.ADM1266_Address = [0x50]

    # Check if all the devices listed in ADM1266_Lib.ADM1266_Address above is present. 
    # If all the devices are not present the function will throw an exception and will not procced with the remaining code.
    ADM1266_Lib.device_present()
     
    while True:
        pvid_channel_name = input("Enter the PVID channel name (1 or 2) or press 'e' to exit: ")
        
        if pvid_channel_name == 'e':
            break
            
        address = input("Enter device address (e.g. 0x40): ")
        address = int(address, 16)
        address = ADM1266_Lib.ADM1266_Address.index(address)
        
        while True:
            channel_name = input("Enter channel name (e.g. VH1, VP1): ")
            # Find the page index based on the channel name
            if channel_name in ADM1266_Lib.VX_Names:
                channel_value = ADM1266_Lib.VX_Names.index(channel_name)
            else:
                print("Channel name not found.")

            ADM1266_Lib.set_page(channel_value)
            try:
                if struct.unpack('B', ADM1266_Lib.get_VOUT_MODE())[0] != 0:
                    break
                else:
                    print("Channel is not set!")
            except ValueError:
                print("Channel is not set!")
            
                    
        
        get_user_input(int(pvid_channel_name))
        
        print(" ")
        user = input('Would you like to add another PVID channel? (yes/no): ').lower()
        
        if user == 'no':
            break
        
    # Close Connection to Aardvark ( Comment this section out for using other devices other than Aardvark)+
    PMBus_I2C.Close_Aardvark()
    
    
    

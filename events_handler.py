"""
This function will take event's that happen on psychopy
then convert and return them as unique hex values

Format:
Block Type | Shape showing | startle | repetition number

List of events:
Break-time:
'break'                  :   16

P-block:
'P_NoShape_NoStartle'    :   17-20
'P_NoShape_Startle'      :   21-24
'P_Shape_NoStartle'      :   25-28
'P_Shape_Startle'        :   29-32
'P_shock'                :   32-35

N-block:
'N_NoShape_NoStartle'    :   40-45
'N_NoShape_Startle'      :   46-51
'N_Shape_NoStartle'      :   52-57
'N_Shape_Startle'        :   58-63

U-block:
'U_NoShape_NoStartle'    :   64-69
'U_NoShape_Startle'      :   70-75
'U_Shape_NoStartle'      :   76-81
'U_Shape_Startle'        :   82-87
'U_NoShape_shock'        :   88-93
'U_Shape_shock'          :   94-99

'Start_Cycle'            :   100-101


"""

import time
import serial
import serial.tools.list_ports as list_ports


def report_event(event, repetition_number = None):
    events = {
        'break': hex(16),

        'P_NoShape_NoStartle': hex(17 + repetition_number -1),
        'P_NoShape_Startle': hex(21 + repetition_number -1),
        'P_Shape_NoStartle': hex(25 + repetition_number -1),
        'P_Shape_Startle': hex(29 + repetition_number -1),
        'P_shock': hex(32 + repetition_number -1),

        'N_NoShape_NoStartle': hex(40 + repetition_number -1),
        'N_NoShape_Startle': hex(46 + repetition_number -1),
        'N_Shape_NoStartle': hex(52 + repetition_number -1),
        'N_Shape_Startle': hex(58 + repetition_number -1),

        'U_NoShape_NoStartle': hex(64 + repetition_number - 1),
        'U_NoShape_Startle': hex(70 + repetition_number - 1),
        'U_Shape_NoStartle': hex(76 + repetition_number - 1),
        'U_Shape_Startle': hex(82 + repetition_number - 1),
        'U_NoShape_shock': hex(88 + repetition_number - 1),
        'U_Shape_shock': hex(94 + repetition_number - 1),
        'Start_Cycle': hex(100 + repetition_number - 1)
    }

    all_ports = list_ports.comports()
    print(all_ports)

    ser3 = serial.Serial('COM4', 115200, bytesize=serial.EIGHTBITS, timeout=1)
    if ser3.is_open:
            print("connection is open")
    ser3.write("RR".encode())

    ######## Testing the output #######
    ## event sending
    ser3.write(events[event].encode())
    time.sleep(0.05)
    ser3.write("RR".encode())
    print("closing")
    ser3.close()
    print("closed")


    return events[event]


if __name__ == '__main__':
    response = report_event("U_Shape_shock", repetition_number = 3)
    timer = core.Clock()
    print(response)
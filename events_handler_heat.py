"""
This function will take event's that happen on psychopy
then convert and return them as unique hex values

List of events:
Break-time:
'break'                  :   16

T2: 20-27
T3: 40-47
T4: 60-67
T5: 80-87
square 1: 0
square 2: +1
square 3: +2
square 4: +3
square 5: +4
heat pulse: +5
rating: +6

more ratings: 90-92
fixation cross: 95


'Start_Cycle'            :   100-101

"""

import time
import serial
import serial.tools.list_ports as list_ports


# temp - T2/T4/T6/T8
# event_type - square1/square2/square3/square4/square5/heat_pulse/rating/fixation
def report_event(temp, event_type):
    events = {
        'break': hex(16),

        'T2_square1': hex(20),
        'T2_square2': hex(21),
        'T2_square3': hex(22),
        'T2_square4': hex(23),
        'T2_square5': hex(24),
        'T2_heat_pulse': hex(25),
        'T2_PainRatingScale': hex(26),

        'T4_square1': hex(40),
        'T4_square2': hex(41),
        'T4_square3': hex(42),
        'T4_square4': hex(43),
        'T4_square5': hex(44),
        'T4_heat_pulse': hex(45),
        'T4_PainRatingScale': hex(46),

        'T6_square1': hex(60),
        'T6_square2': hex(61),
        'T6_square3': hex(62),
        'T6_square4': hex(63),
        'T6_square5': hex(64),
        'T6_heat_pulse': hex(65),
        'T6_PainRatingScale': hex(66),

        'T8_square1': hex(80),
        'T8_square2': hex(81),
        'T8_square3': hex(82),
        'T8_square4': hex(83),
        'T8_square5': hex(84),
        'T8_heat_pulse': hex(85),
        'T8_PainRatingScale': hex(86),

        'PreVas_rating': hex(90),
        'MidRun_rating': hex(91),
        'PostRun_rating': hex(92),

        'Fixation_cross': hex(95),

        'Start_Cycle': hex(100)
    }


    all_ports = list_ports.comports()
    print(all_ports)

    ser3 = serial.Serial('COM4', 115200, bytesize=serial.EIGHTBITS, timeout=1)
    if ser3.is_open:
        print("connection is open")
    ser3.write("RR".encode())

    ######## Testing the output #######
    ## event sending
    ser3.write(events[event_type].encode())
    time.sleep(0.05)
    ser3.write("RR".encode())
    print("closing")
    ser3.close()
    print("closed")

    return events[event_type]


if __name__ == '__main__':
    response = report_event('T2', 'square1')
    timer = core.Clock()
    print(response)

#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from time import time, sleep
from datetime import datetime
import socket
import struct
import binascii
import six
from psychopy import core


##############################################################################
states = {
            0: "IDLE",
            1: "READY",
            2: "TEST IN PROGRESS"
}

test_states = {
            0: 'IDLE',
            1: 'RUNNING',
            2: 'PAUSED',
            3: 'READY'
        }
response_codes = {
            0: "OK",
            1: "FAIL: ILLEGAL PARAMETER",
            2: "FAIL: ILLEGAL STATE TO SEND THIS",
            3: "FAIL: NOT THE PROPER TEST STATE",
            4096: "DEVICE COMMUNICATION ERROR",
            8192: "safety warning, test continues",
            16384: "Safety error, going to IDLE"
        }

command_to_id = {
            'GET_STATUS': 0,
            'SELECT_TP': 1,
            'START': 2,
            'PAUSE': 3,
            'TRIGGER': 4,
            'STOP': 5,
            'ABORT': 6,
            'YES': 7,  # used to start increasing the temperature
            'NO': 8,  # used to start decreasing the temperature
            'COVAS': 9,
            'VAS': 10,
            'SPECIFY_NEXT': 11,
            'T_UP': 12,
            'T_DOWN': 13,
            'KEYUP': 14,  # used to stop the temperature gradient,
            'UNNAMED': 15
        }

# make the same as above but reversed:
id_to_command = {item: key for key, item in command_to_id.items()}
        

##############################################################################
class Pathway(object):
    """
        Pathway is a class to communicate with the Medoc Pathway thermal stimulation machine.

        Args:
            ip (str): device ip address
            port_number (int): port the device is listening on
            timeout (float): seconds until connection timeouts; default 5s
            verbose (bool): flag whether to print responses; default True
            buffer_size (int): size of connection buffer; default 1024

        """

    # class FakeEventListener:
    #     def wait_for_seconds(self, seconds):
    #         sleep(seconds)

    # class FakeConfig:
    #     address = '192.168.55.80'  # change this IP address to be the same as in external control configuration screen
    #     port = 20121
    #     debug = 1
    #     timedelayformedoc = 0.1
    #     vas_search_program = '00011100'  # enter any set of programs as in configuration screen

    # config = FakeConfig()

    def __init__(self, ip, port_number, timeout=5., verbose=True, buffer_size=1024):
        assert isinstance(ip, six.string_types), "IP address must be a string."
        assert isinstance(port_number, six.integer_types), "Port must be an integer"

        self.ip = ip
        self.port_number = port_number
        self.BUFFER_SIZE = buffer_size
        self.timeout = timeout
        self.verbose = verbose
        self.socket = None
        

    #  converter from bytes to int:
    @staticmethod
    def intToBytes(integer, nbytes):
        return integer.to_bytes(nbytes, byteorder='big')

    # converter from int to bytes:
    @staticmethod
    def intFromBytes(xbytes):
        return int.from_bytes(xbytes, 'big')

    # packs bytes together
    def commandBuilder(self, command, parameter=None):
        if type(command) is str:
            command = command_to_id[command.upper()]

        if type(parameter) is str:
            # then program code, e.g. '00000001'
            parameter = int(parameter, 2)
        elif type(parameter) is float:
            parameter = 100 * parameter

        commandbytes = self.intToBytes(socket.htonl(int(time())), 4)
        commandbytes += self.intToBytes(int(command), 1)
        if parameter:
            commandbytes += self.intToBytes(socket.htonl(int(parameter)), 4)
        return self.intToBytes(len(commandbytes),
                               4) + commandbytes  # prepending the command data with 4-bytes header that indicates the
        # command data length

    # command sender:
    def sendCommand(self, command, parameter=None):
        """
             this functions allows sending commands to the MMS

             e.g. :      sendCommand('get_status')
             or          sendCommand('select_tp', '01000000')
        """
        # convert command to bytes:
        commandbytes = self.commandBuilder(command, parameter=parameter)
        print("before config")
        
        address = self.ip
        port = self.port_number
        print(f'Sending the following bytes: {binascii.hexlify(commandbytes)} -- {len(commandbytes)} bytes')
        # now the connection part:
        for attempts in range(3):
            try:
                s = socket.socket()
                s.connect((address, port))
                s.send(commandbytes)
                data = msg = s.recv(1024)
                while data:
                    data = s.recv(17)
                    msg += data
                # resp of type medocResponse:
                resp = self.medocResponse(msg)
                print("Received: ")
                print(resp)
                return resp
                break
            except ConnectionResetError:
                print("==> ConnectionResetError")
                attempts += 1
                s.close()
                # el.wait_for_seconds(Pathway.config.timedelayformedoc)
                pass
        core.wait(0.1)        
        # el.wait_for_seconds(Pathway.config.timedelayformedoc)
        return resp


    # printout:
    class medocResponse:
        """
           A container to interpret and store the output response.
        """

        # decoding the bytes we receive:
        def __init__(self, response):
            self.length = struct.unpack_from('H', response[0:4])[0]  # checks the response length is correct
            self.timestamp1 = bytearray(response[4:8])
            self.timestamp2 = self.timestamp1[:]
            self.timestamp1[0] = self.timestamp2[3]
            self.timestamp1[1] = self.timestamp2[2]
            self.timestamp1[2] = self.timestamp2[1]
            self.timestamp1[3] = self.timestamp2[0]
            # timestamp is the time the command was sent:
            self.timestamp = Pathway.intFromBytes(self.timestamp1)
            self.datetime = datetime.fromtimestamp(self.timestamp)
            self.strtime = self.datetime.strftime("%Y-%m-%d %H:%M:%S.%f")

            self.command = Pathway.intFromBytes(response[8:9])

            self.state = Pathway.intFromBytes(response[9:10])
            # see if we have a documented state for this response:
            if self.state in states:
                self.statestr = states[self.state]
            else:
                self.statestr = 'unknown state code'

            self.teststate = Pathway.intFromBytes(response[10:11])
            # see if we have a documented test state for this response:
            if self.teststate in test_states:
                self.teststatestr = test_states[self.teststate]
            else:
                self.teststatestr = 'unknown test state code'

            self.respcode = struct.unpack_from('H', response[11:13])[0]

            if self.respcode in response_codes:
                self.respstr = response_codes[self.respcode]
            else:
                self.respstr = "unknown response code"

            # the test time is in seconds once divided by 1000:
            self.testtime = struct.unpack_from('I', response[13:17])[0] / 1000.
            # the temperature is in °C once divided by 100:
            self.temp = struct.unpack_from('h', response[17:19])[0] / 100.
            self.CoVAS = Pathway.intFromBytes(response[19:20])
            self.yes = Pathway.intFromBytes(response[20:21])
            self.no = Pathway.intFromBytes(response[21:22])
            self.ttl = Pathway.intFromBytes(response[22:23])
            self.message = response[23:self.length]
            # store the whole response
            self.response = response

        def __repr__(self):  # this is the text that will be shown (modifiable)
            msg = ""
            msg += f"timestamp     : {self.strtime}\n"
            msg += f"command       : {id_to_command[self.command]}\n"
            msg += f"state         : {self.statestr}\n"
            msg += f"test state    : {self.teststatestr}\n"
            msg += f"response code : {self.respstr}\n"
            msg += f"temperature   : {self.temp}°C\n"
            if self.statestr == "TEST IN PROGRESS":
                msg += f"test time     : {self.testtime} seconds\n"
            elif self.respstr != "OK":
                msg += f"sup. message  : {self.message}\n"
            if self.yes:
                msg += "~~ YES was pressed! ~~\n"
            if self.no:
                msg += "~~ NO was pressed! ~~\n"
            if self.ttl:
                msg += "~~ TTL OUT sent! ~~\n"
            return msg

        def __str__(self):
            return self.__repr__()

        def __getitem__(self, s):
            return self.response[s]

"""
if __name__ == "__main__":  # this is the main part of the code to be modified
    sendCommand(0)
    sendCommand('select_tp', 195)
    sleep(15)
    sendCommand('START')
    sleep(15)
    sendCommand('stop')
    
    sendCommand('vas', 4) # Set pain rating 4
    sleep(3)
    sendCommand('t_down', 500) # Step 5 degrees down
    sleep(10)
    sendCommand('vas', 7) # Set pain rating 7
    sleep(3)
    sendCommand('t_up', 500) # Step 5 degrees up
    sleep(10)
    sendCommand('vas', 10) # Set pain rating 10
    sleep(3)   
    sendCommand('stop')
    """


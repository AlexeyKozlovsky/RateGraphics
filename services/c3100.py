import linecache
import os
import re
import time

import serial
from serial.tools import list_ports

from utils.consts import TERMCHAR, DEVNAME, VID, BAUDRATE, NRET, BYTESIZE, PID


class C3100Device:
    exc_cnt = 0

    def __init__(self, file_name_base="", debug=None):
        self.resp = ''
        self.file_name_base = file_name_base
        self.detect_serial_port(vid=VID, pid=PID)

    def detect_serial_port(self, vid=None, pid=None, descr=None, dev_num=0):
        if vid and pid:
            re = "{}:{}".format(vid, pid)
        elif descr:
            re = descr
        else:
            print("{}: No USB serial port specified".format(DEVNAME))
            return None
        try:
            l_ports = list(list_ports.grep(re))
            self.port, descr, hwid = l_ports[dev_num]
        except StopIteration:
            print("{}: No USB serial port '{}' detected".format(DEVNAME, re))
            return None
        print("{}: Detected {} on {} <{}>".format(DEVNAME, descr, self.port, hwid))
        return self.port

    def open(self):
        print("{}: ".format(DEVNAME), end="")
        self.dev = serial.Serial(port=self.port, timeout=1)

        self.port = self.dev.port
        self.dev.baudrate = BAUDRATE
        self.dev.bytesize = BYTESIZE
        # The following two lines provide power supply for opto isolated Protek RS232
        self.dev.setDTR(True)
        self.dev.setRTS(False)

        # clear RX buffer from any previous data
        self.dev.reset_input_buffer()
        time.sleep(1)
        self.dev.read(self.dev.in_waiting)

        print("{}: Device opened".format(DEVNAME))
        d = self.dev.get_settings()
        print("{}: Ready. Receiving from {} @ {}/{}{}{}".format(DEVNAME, self.port, d['baudrate'], d['bytesize'],
                                                                d['parity'], d['stopbits']))
        return True

    def close(self):
        self.dev.close()

    def write(self, data):
        self.dev.write((data + TERMCHAR).encode())

    def readline(self):
        return self.dev.read_until(TERMCHAR.encode()).decode()

    def get_data(self):
        value0, units0, value1, units1 = None, None, None, None
        self.write('RM?')
        ans = self.readline()
        m = re.match('[Mm]\s*([-\d\.\?]+)(.*)', ans)
        if m:
            value0, units0 = m.group(1), m.group(2).strip()
        #            print('1 <{}> <{}>'.format(value0,units0))
        if NRET == 1:
            if value0 != None and units0 != None:
                return (value0, units0)
            else:
                return None
        elif NRET == 0:
            time.sleep(0.2)
            if self.dev.in_waiting == 0:
                if value0 != None and units0 != None:
                    return (value0, units0)
                else:
                    return None

        ans = self.readline()
        m = re.match('[Mm]\s*([-\d\.\?]+)(.*)', ans)
        if m:
            value1, units1 = m.group(1), m.group(2).strip()
        #            print('2 {} {}'.format(value1,units1))
        if value0 != None and units0 != None and value1 != None and units1 != None:
            return (value0, units0, value1, units1)
        else:
            return None

    def exception_handler(self, e):
        self.exc_cnt += 1

        name = e.__traceback__.tb_frame.f_code.co_name
        filename = e.__traceback__.tb_frame.f_code.co_filename
        lineno = e.__traceback__.tb_lineno
        line = linecache.getline(filename, lineno, globals).strip()

        with open(os.path.splitext(__file__)[0] + ".log", "a") as f:
            print('{} {} {} {}() "{}"'.format(time.strftime("%Y/%m/%d %H:%M:%S"), self.exc_cnt,
                                              e.__class__.__name__, name, line), file=f)
        print('{} {} {} {}() "{}"'.format(time.strftime("%Y/%m/%d %H:%M:%S"), self.exc_cnt,
                                          e.__class__.__name__, name, line))

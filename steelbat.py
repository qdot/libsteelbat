import time 
import sys
import usb
import operator

class SteelBat(object):
    VID = 0x0a7b
    PID = 0xd000

    ep = { 'in'  : 0x02, \
           'out' : 0x01
           }



    def __init__(self, chan=0x0, debug=False):
        self._connection = False
        self.timeout = 1000
        self.raw_lights = [255 for i in range(0, 34)]

    def open(self, vid = None, pid = None):
        if vid is None:
            vid = self.VID
        if pid is None:
            pid = self.PID
        self._connection = usb.core.find(idVendor = vid,
                                         idProduct = pid)
        if self._connection is None:
            return False
        #self._connection.detach_kernel_driver(0)
        self._connection.set_configuration()
        return True

    def set_light(self):
        while 1:
            for i in range(0, 15):
                self.raw_lights = [i << 4 | i for x in range(0, 34)]
                self._connection.write(self.ep['out'], self.raw_lights, 0, 100)
                time.sleep(.050)
            for i in range(15, 0, -1):
                self.raw_lights = [i << 4 | i for x in range(0, 34)]
                self._connection.write(self.ep['out'], self.raw_lights, 0, 100)
                time.sleep(.050)

    def close(self):
        if self._connection is not None:
            #self._connection.attach_kernel_driver(0)
            self._connection = None

    def _send(self, command):
        # libusb expects ordinals, it'll redo the conversion itself.
        c = command
        self._connection.write(self.ep['out'], map(ord, c), 0, 100)

    def _receive(self, size=4096):
        r = self._connection.read(self.ep['in'], size, 0, self.timeout)
        if len(r) == 0:
            return r
        checksum = reduce(operator.xor, r[:-1])
        if checksum != r[-1]:
            raise ANTReceiveException("Checksums for packet do not match received values!")
        if self._debug:
            self.data_received(''.join(map(chr, r)))
        return r

def main():
    a = SteelBat()
    if not a.open():
        print "Cannot open device!"
        return 1
    print "Opened device!"
    a.set_light()
    a.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
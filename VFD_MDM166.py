#!/usr/bin/python3
# #####################################
# info: This class can connect to VFD MDM166
#
# date: 2017-06-13
# version: 0.1.1
#
# Dependencies:
# $ sudo apt-get install python3-dev libusb-1.0-0-dev libudev-dev python3-pip
# $ sudo pip3 install --upgrade setuptools
# $ sudo pip3 install hidapi

# place a file 99-hidraw-vfd-permissions.rules with this line to /etc/udev/rules.d:
# SUBSYSTEM=="usb", ATTR{idVendor}=="19c2", ATTR{idProduct}=="6a11", MODE="0666"
#
# history:
#
# #####################################
# Import solution :-)
import hid
import dot_matrix_font


class usbVFD:
    def __init__(self,vid=0x19c2,pid=0x6a11):
        # just open an usb-hid-connection to the VFD:
        self.dev = hid.device()
        self.dev.open(vendor_id=vid, product_id=pid)

        self.font = dot_matrix_font.dot_matrix_font()

    def send_command(self,command):
        #just send the command with the length ahead
        l=bytes([len(command)])
        command=l+command
        self.dev.write(command)

    ########################################################################################
    # general commands:

    def dimming(self,luminance=100):
        command = b'\x1b\x40'
        if luminance>=75:
            command+=b'\x02'
        elif luminance>=25:
            command+=b'\x01'
        else:
            command+=b'\x00'
        self.send_command(command)

    def clear_display(self):
        self.send_command(command=b'\x1b\x50')

    def all_on(self):
        self.send_command(command=b'\x1b\x55')

    def reset(self):
        self.send_command(command=b'\1F')

    def set_addr_counter(self,add):
        self.send_command(command=b'\x1b\x60'+bytes([add]))

    def write_grafic(self,data):
        self.send_command(command=b'\x1b\x70'+bytes([len(data)])+bytes(data))



    ########################################################################################
    # clock:

    def calc_BCD(self,n):
        if n>0xFF:
            n=0xFF
        higher_nibble, lower_nibble = divmod(n,10)
        return higher_nibble<<4 | lower_nibble

    def set_clock_data(self,hour,minute):
        self.send_command(command=b'\x1B\x00'+bytes([self.calc_BCD(minute)])+bytes([self.calc_BCD(hour)]))

    def set_clock_format(self,clock_format='24h',row='1row'):
        command = b'\x1b'
        if row=='upper':
            command+=b'\x01'
        else:
            command+=b'\x02'
        if clock_format=='24h':
            command+=b'\x01'
        else:
            command+=b'\x00'
        self.send_command(command)


    ########################################################################################
    # symbols: symbol=address of symbol, grayscale from 0...100%
    def set_symbol(self,symbol,grayscale=100):
        command = b'\x1B\x30'+symbol
        if grayscale >= 75:
            command += b'\x02'
        elif grayscale >= 25:
            command += b'\x01'
        else:
            command += b'\x00'
        self.send_command(command)
    ######
    # named access to symbols for convenience
    #

    def set_play(self,grayscale=100):
        self.set_symbol(symbol=b'\x00',grayscale=grayscale)

    def set_pause(self,grayscale=100):
        self.set_symbol(symbol=b'\x01',grayscale=grayscale)

    def set_rec(self, grayscale=100):
        self.set_symbol(symbol=b'\x02', grayscale=grayscale)

    def set_envelope(self, grayscale=100):
        self.set_symbol(symbol=b'\x03',grayscale=grayscale)

    def set_envelope_at(self, grayscale=100):
        self.set_symbol(symbol=b'\x04',grayscale=grayscale)

    def set_mute(self, grayscale=100):
        self.set_symbol(symbol=b'\x05',grayscale=grayscale)

    def set_i(self, grayscale=100, segment=1):
        if segment <=1:
            segment=1
        elif segment>=4:
            segment=4
        self.set_symbol(symbol=bytes([0x05+segment]))

    def set_vol_logo(self,grayscale=100):
        self.set_symbol(symbol=b'\x0A',grayscale=grayscale)
    def set_vol_bar(self,grayscale=100,segment=1):
        if segment <=1:
            segment=1
        elif segment>=14:
            segment=14
        self.set_symbol(symbol=bytes([0x0A+segment]))

    ########################################################################################
    # write text: line is 0 for upper row, 1 for lower row
    def write_str(self,text,row=0):
        char_count = 0
        for char in text:
            addr_count = 0
            for i in range(0, 6):
                # send column after column:
                self.set_addr_counter(addr_count + char_count * 12 + row)
                col = [str(row[i]) for row in self.font.str_to_dot_matrix(char)]
                col = [int(''.join(col), 2)]
                self.write_grafic(col)
                addr_count += 2  # each column has two addresses: upper and lower on
            char_count+=1

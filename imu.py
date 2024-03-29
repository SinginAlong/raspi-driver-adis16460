import sys
import spidev
import RPi.GPIO as GPIO
import time
import array
from struct import *

class Dim3:
    def __init__(self, scaling):
        self.x=0
        self.y=0
        self.z=0
        self.scaling=scaling
    def scal(self):
        self.x=self.x*self.scaling
        self.y=self.y*self.scaling
        self.z=self.z*self.scaling

class ImuData:
    def __init__(self):
        self.accl=Dim3(0.25)
        self.gyro=Dim3(0.005)
        self.temp=0
    def scaling(self):
        self.accl.scal()
        self.gyro.scal()
        self.temp=self.temp*0.05+25
    def dump(self):
        print("{0},{1},{2},{3},{4},{5},{6}".format(self.accl.x, self.accl.y, self.accl.z, self.gyro.x, self.gyro.y, self.gyro.z, self.temp))

def SpiDevReadBurst(spi,reg):
    send=[0]*((10+1)*2)
    send[0]=reg
    resp=spi.xfer2(send)
    return resp

def SpiDevWrite(spi,reg,data):
    send=[0]*2
    send[0]=0x80|reg
    send[1]=data
    spi.writebytes(send)

def SpiDevRead(spi,reg):
    send=[0]*2
    send[0]=reg
    spi.writebytes(send)
    resp=spi.readbytes(2)
    ret=((resp[0]<<8)|resp[1])
    return ret

def SpiReadSensor(spi,autoScale=True):
    imu=ImuData()
    resp=SpiDevReadBurst(spi,0x3E)
    arr=array.array('B',resp).tostring()
    values=unpack('>hhhhhhhhhhh', arr)
	# burst order is: DIAG_STAT, X_GYRO_OUT, Y_GYRO_OUT, Z_GYRO_OUT, X_ACCL_OUT, Y_ACCL_OUT, Z_ACCL_OUT, TEMP_OUT
    imu.gyro.x=values[2]
    imu.gyro.y=values[3]
    imu.gyro.z=values[4]
    imu.accl.x=values[5]
    imu.accl.y=values[6]
    imu.accl.z=values[7]
    imu.temp=values[8]
    if autoScale == True:
        imu.scaling()
    return imu

def ImuResetHard(bcmGpio):
    GPIO.output(bcmGpio,GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(bcmGpio,GPIO.HIGH)
    time.sleep(0.5)

def ImuResetSoft(spi):
    SpiDevWrite(spi,0x3E,0x80)
    time.sleep(0.5)


############################################
############################################
##  < START >
############################################
############################################
spi=spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz=400000
spi.mode=3
bcmRst=6
GPIO.setmode(GPIO.BCM)
GPIO.setup(bcmRst,GPIO.OUT)
GPIO.output(bcmRst,GPIO.HIGH)

##MAINLOOP
mainloop=True
while mainloop==True:
    cmdline_str=raw_input()
    cmdline=cmdline_str.split(' ')
    
    if cmdline[0] in {'rd','read'}:
        if len(cmdline) != 2:
            print("usage: rd [addr]")
        else:
            reg=int(cmdline[1],0)
            print(SpiDevRead(spi,reg))
    elif cmdline[0] in {'wr','write'}:
        if len(cmdline) != 3:
            print("usage: wr [addr] [data]")
        else:
            reg=int(cmdline[1],0)
            data=int(cmdline[2],0)
            SpiDevWrite(spi,reg,data)
    elif cmdline[0] in {'rst','reset'}:
        if len(cmdline) != 1:
            print("usage: rst")
        else:
            ImuResetSoft(spi)
    elif cmdline[0] in {'id'}:
        if len(cmdline) != 1:
            print("usage: id")
        else:
            print(SpiDevRead(spi,0x56))
    elif cmdline[0] in {'stat'}:
        if len(cmdline) != 1:
            print("usage: stat")
        else:
            print(SpiDevRead(spi,0x32))
    elif cmdline[0] in {'rsthard','hardreset'}:
        if len(cmdline) != 1:
            print("usage: hardrst")
        else:
            ImuResetHard(bcmRst)
    elif cmdline[0] in {'q','quit','exit'}:
        break
    elif cmdline[0] in {'raw'}:
        if len(cmdline) != 1:
            print("usage: raw")
        else:
            imu=SpiReadSensor(spi,False)
            imu.dump()
    elif cmdline[0] in {'run'}:
        if len(cmdline) != 3:
            print("usage: run [count(0=inf)] [delay@ms]")
        else:
            count=int(cmdline[1])
            delay=int(cmdline[2])*0.001
            cnt=0
            while cnt<count or count==0:
                imu=SpiReadSensor(spi)
                imu.dump()
                cnt=cnt+1
                time.sleep(delay)
    else:
        # Usage
            print("usage: id")
            print("usage: stat")
            print("usage: rst")
            print("usage: rsthard")
            print("usage: rd [addr]")
            print("usage: wr [addr] [data]")
            print("usage: run [count(0=inf)] [delay@ms]")
            print("usage: quit")
            print("usage: exit")


spi.close()
GPIO.cleanup()

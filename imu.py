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
        self.temp=self.temp*0.25+25
    def dump(self):
        print("{0},{1},{2},{3},{4},{5}".format(self.accl.x, self.accl.y, self.accl.z, self.gyro.x, self.gyro.y, self.gyro.z))

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

def SpiReadSensor(spi):
    imu=ImuData()
    resp=SpiDevReadBurst(spi,0x3E)
    arr=array.array('B',resp).tostring()
    values=unpack('>hhhhhhhhhhh', arr)
    imu.accl.x=values[2]
    imu.accl.y=values[3]
    imu.accl.z=values[4]
    imu.gyro.x=values[5]
    imu.gyro.y=values[6]
    imu.gyro.z=values[7]
    imu.temp=values[8]
    imu.scaling()
    imu.dump()
    return imu

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz=400000
spi.mode=3

GPIO.setmode(GPIO.BCM)
GPIO.setup(6,GPIO.OUT)

GPIO.output(6,GPIO.LOW)
time.sleep(0.5)
GPIO.output(6,GPIO.HIGH)
time.sleep(0.5)

#print('RESPONSE=0x' + format(SpiDevRead(spi,0x56),'x'))
#print('TEMP_OUT=0x' + format(SpiDevRead(spi,0x1e),'x'))
#print('GLOB_CMD=0x' + format(SpiDevRead(spi,0x1e),'x'))
#print('MSC_CTRL=0x' + format(SpiDevRead(spi,0x32),'x'))


for cnt in range(100):
    imu=SpiReadSensor(spi)
    time.sleep(0.05)
    

spi.close()
GPIO.cleanup()

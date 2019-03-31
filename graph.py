from pwn import *
# sudo pip install pwntools
import time
import matplotlib.pyplot as plt
# sudo pip install matplotlib
# sudo apt-get install libfreetype6-dev
# sudo apt-get install libpng-dev
# sudo apt install python-cairo python-cairocffi python-cairo-dev
# sudo apt install python-gi-cairo

class Dim6Plot:
    def __init__(self, length):
        self.x = [0]*length
        for i in range(length):
            self.x[i] = -length+(i+1)
        self.accl_x = [0]*length
        self.accl_y = [0]*length
        self.accl_z = [0]*length
        self.gyro_x = [0]*length
        self.gyro_y = [0]*length
        self.gyro_z = [0]*length

        ymin=-5000
        ymax=5000
        plt.subplot(2,3,1)
        self.line_ax,=plt.plot(self.x,self.accl_x, color = "red")
        plt.ylim(ymin,ymax)
        plt.subplot(2,3,2)
        self.line_ay,=plt.plot(self.x,self.accl_y, color = "green")
        plt.ylim(ymin,ymax)
        plt.subplot(2,3,3)
        self.line_az,=plt.plot(self.x,self.accl_z, color = "blue")
        plt.ylim(ymin,ymax)
        plt.subplot(2,3,4)

        ymin=-100
        ymax=100
        self.line_gx,=plt.plot(self.x,self.gyro_x, color = "red")
        plt.ylim(ymin,ymax)
        plt.subplot(2,3,5)
        self.line_gy,=plt.plot(self.x,self.gyro_y, color = "green")
        plt.ylim(ymin,ymax)
        plt.subplot(2,3,6)
        self.line_gz,=plt.plot(self.x,self.gyro_z, color = "blue")
        plt.ylim(ymin,ymax)
        plt.tight_layout()

    def setvalue(self,ax,ay,az,gx,gy,gz):
        self.accl_x.append(ax)
        self.accl_x.pop(0)
        self.accl_y.append(ay)
        self.accl_y.pop(0)
        self.accl_z.append(az)
        self.accl_z.pop(0)
        self.gyro_x.append(gx)
        self.gyro_x.pop(0)
        self.gyro_y.append(gy)
        self.gyro_y.pop(0)
        self.gyro_z.append(gz)
        self.gyro_z.pop(0)

    def draw(self):
        self.line_ax.set_ydata(self.accl_x)
        self.line_ay.set_ydata(self.accl_y)
        self.line_az.set_ydata(self.accl_z)
        self.line_gx.set_ydata(self.gyro_x)
        self.line_gy.set_ydata(self.gyro_y)
        self.line_gz.set_ydata(self.gyro_z)

        plt.pause(0.1)


io=process(['python','imu.py'])
io.sendline('id')

length=100
dim=Dim6Plot(length)
dim.draw()


mainloop=True
while mainloop==True:
    str=io.recvline()
    str=str.splitlines()[0].split(",")[0]
    print(str)
    if str == '16460':
        break

io.sendline('run 0 100')
while mainloop==True:
    str=io.recvline()
    #print(str)
    values=str.splitlines()[0].split(",")
    print(values)
    print(len(values))
    dim.setvalue(values[0],values[1],values[2],values[3],values[4],values[5])
    dim.draw()

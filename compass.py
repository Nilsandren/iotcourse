import sys, os, math, time, thread, smbus, random, requests, Adafruit_ADXL345, string, Adafruit_BMP.BMP085 as BMP085, numpy as np
sensor = BMP085.BMP085()
accel=Adafruit_ADXL345.ADXL345()
	


bus = smbus.SMBus(1)
addrHMC = 0x1e

def getSignedNumber(number):
    if number & (1<<15):
        return number | ~65535
    else:
        return number & 65535

i2c_bus=smbus.SMBus(1)
i2c_address=0x69
i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
i2c_bus.write_byte_data(i2c_address,0x23,0x20)

def lowpass(xArr,yArr):
    dt = 0.5
    alpha = 0.4
    yArrNew = [0,0,0,0,0,0,0,0,0,0]
    i = 0;
    while i < 10:
	yArrNew[i] = alpha*xArr[i] + (1-alpha)*yArr[i]
	i=i+1
    return yArrNew

def read_word(address, adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val

def read_word_2c(address, adr):
    val = read_word(address, adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def main():

    yValues = [0,0,0,0,0,0,0,0,0,0]
    bus.write_byte_data(addrHMC, 0, 0b01110000)  # Set to 8 samples @ 15Hz
    bus.write_byte_data(addrHMC, 1, 0b00100000)  # 1.3 gain LSb / Gauss 1090 (default)
    bus.write_byte_data(addrHMC, 2, 0b00000000)  # Continuous sampling

    while True:
#multiply with digital resolution
        #dont forget to / sens
        ax, ay, az = accel.read()
       	ax = ax/256
	ay = ay/256
	az = az/256
	
        i2c_bus.write_byte(i2c_address,0x28)
        X_L = i2c_bus.read_byte(i2c_address)
        i2c_bus.write_byte(i2c_address,0x29)
        X_H = i2c_bus.read_byte(i2c_address)
        X = X_H << 8 | X_L

        i2c_bus.write_byte(i2c_address,0x2A)
        Y_L = i2c_bus.read_byte(i2c_address)
        i2c_bus.write_byte(i2c_address,0x2B)
        Y_H = i2c_bus.read_byte(i2c_address)
        Y = Y_H << 8 | Y_L

        i2c_bus.write_byte(i2c_address,0x2C)
        Z_L = i2c_bus.read_byte(i2c_address)
        i2c_bus.write_byte(i2c_address,0x2D)
        Z_H = i2c_bus.read_byte(i2c_address)
        Z = Z_H << 8 | Z_L
        
        gX = getSignedNumber(X)*8.75/1000
        gY = getSignedNumber(Y)*8.75/1000
        gZ = getSignedNumber(Z)*8.75/1000

        mx = read_word_2c(addrHMC, 3)*0.92
        my = read_word_2c(addrHMC, 7)*0.92
        mz = read_word_2c(addrHMC, 5)*0.92
	
	xValues = [ax,ay,az,gX,gY,gZ,mx,my,mz,sensor.read_altitude()]
	yValues = lowpass(xValues,yValues) 
	#print "Acc:","x: ", ax, "y: ", ay, "z: ", az,"Gyro:","x: ",gX,"y: ",gY,"z: ",gZ, "Mag:", "x:",mx," ","y:",my," ","z:",mz,('Altitude: {0:0.2f} m'.format(sensor.read_altitude()))
        yValues = np.around(yValues,2)
	print "Acc:","x: ", yValues[0], "y: ", yValues[1], "z: ", yValues[2],"Gyro:","x: ",yValues[3],"y: ",yValues[4],"z: ",yValues[5], "Mag:", "x:",yValues[6]," ","y:",yValues[7]," ","z:",yValues[8],"Altitude: ", yValues[9]
	#print('Acc: x: {0:0.2f} y: {0:0.2f} z: {0:0.2f} Gyro: x: {0:0.2f} y: {0:0.2f} z: {0:0.2f} Mag: x: {0:0.2f} y: {0:0.2f} z: {0:0.2f} Altitude = {0:0.2f}'.format(yValues[0],yValues[1],yValues[2],yValues[3],yValues[4],yValues[5],yValues[6],yValues[7],yValues[8],yValues[9])) 
	time.sleep(0.5)

if __name__ == "__main__":
    main()

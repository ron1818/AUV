#! /usr/bin/python
""" Ren Ye 20160401
modified from RTIMULib
"""

import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math

def computeHeight(pressure):
    """
    computeHeight() - the conversion uses the formula
    h = (T0 / L0) * ((p / P0)**(-(R* * L0) / (g0 * M)) - 1)
    where
    h  = height above sea level
    T0 = standard temperature at sea level = 288.15
    L0 = standard temperatur elapse rate = -0.0065
    p  = measured pressure
    P0 = static pressure = 1013.25
    g0 = gravitational acceleration = 9.80665
    M  = mloecular mass of earth's air = 0.0289644
    R* = universal gas constant = 8.31432
    Given the constants, this works out to
    h = 44330.8 * (1 - (p / P0)**0.190263) """

    return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263));


def reverseRoll(roll):
    """ reverse roll angle:
        measured: 0, -90, 180, 90
        actual:   180, 90, 0, -90 """
    if 0 <= roll <= 180:
        return roll - 180
    else:
        return roll + 180


class alti_IMU(object):
    """ alti IMU using RTIMU library """
    def __init__(self, SETTINGS_FILE="RTIMULib", isoffset=True, quiet=False):
        self.quiet = quiet
        self.isoffset = isoffset
        if not os.path.exists(SETTINGS_FILE + ".ini"):
            if not self.quiet: print("#Settings file does not exist, will be created")
        self.s = RTIMU.Settings(SETTINGS_FILE)

    def initialize(self):
        # initialize IMU
        self.imu = RTIMU.RTIMU(self.s)
        # initialize pressure sensor
        self.pressure = RTIMU.RTPressure(self.s)

        if not self.quiet:
            print("#IMU Name: " + self.imu.IMUName())
            print("#Pressure Name: " + self.pressure.pressureName())

        # initialize until successful
        exitFlag, exit1Flag, exit2Flag = [True, True, True]

        while exitFlag:
            if (not self.imu.IMUInit()):
                if not self.quiet: print("#IMU Init Failed")
            else:
                if not self.quiet: print("#IMU Init Succeeded")
                exit1Flag = False

            if (not self.pressure.pressureInit()):
                if not self.quiet: print("#Pressure sensor Init Failed")
            else:
                if not self.quiet: print("#Pressure sensor Init Succeeded")
                exit2Flag = False

            if (not (exit1Flag or exit2Flag)):
                exitFlag = False

        # this is a good time to set any fusion parameters

        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)

        self.poll_interval = self.imu.IMUGetPollInterval()
        if not self.quiet:
            print("#Recommended Poll Interval: %dmS\n" % self.poll_interval)

        self.offset = [0] * 2 # initialize offset
        if self.isoffset:
            self.offset = self.offset_data() # calibrate offset

    def offset_data(self, timeout = 100):
        """ put IMU as calm as possible, offset to 0,0 pitch and roll """
        timer = 0
        r_min = p_min = 180
        r_max = p_max = -180
        while timer <= timeout:
            data = self.read_data(tid=0.0)
            r_min = min(r_min, data["roll"])
            r_max = max(r_max, data["roll"])
            p_min = min(p_min, data["pitch"])
            p_max = max(p_max, data["pitch"])
            timer = timer + 1

        return [0.5*(r_min+r_max), 0.5*(p_min+p_max)]

    def read_data(self, tid=0.5):
        tdf = 0.0
        tic = time.time()
        while tdf <= tid:
            while not self.imu.IMURead():
                continue
            else: #if self.imu.IMURead():
                # x, y, z = imu.getFusionData()
                # print("%f %f %f" % (x,y,z))
                data = self.imu.getIMUData()
                (data["pressureValid"], data["pressure"],\
                data["temperatureValid"], data["temperature"]) =\
                self.pressure.pressureRead()

                fusionPose = data["fusionPose"]

                # time.sleep(1)
                time.sleep(self.poll_interval*1.0/1000.0)
                tdf = time.time() - tic
                # print tdf
        else:
            # print data["pressure"]
            return {"pressure": data["pressure"],
                    "height": computeHeight(data["pressure"]),
                    "temperature": data["temperature"],
                    "roll": reverseRoll(math.degrees(fusionPose[0]))-self.offset[0],
                    "pitch": math.degrees(fusionPose[1])-self.offset[1],
                    "yaw": math.degrees(fusionPose[2])}


if __name__ == "__main__":
    IMU = alti_IMU(isoffset=False, quiet=True)
    IMU.initialize()

    while True:
        # print IMU.read_data()
        data = IMU.read_data(tid=1)#.next()
        print("r: %.1f p: %.1f y: %.1f" % (data["roll"], data['pitch'], data['yaw']))
        ##### bug report ####
        # if set delay, data will not be accurate #
        # time.sleep(1)


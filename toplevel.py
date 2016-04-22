#! /usr/bin/python
"""2016/04/01
top level to log GPS and IMU data as input to control
motor and rudder,
use PID for motor and rudder control.
need to use I2C/alti_IMU_RTIMULIB.py, I2C/SC16IS750_I2C.py, I2C/LCD_I2C.py,
NMEA/file_IO.py, GPS/waypoint.py, PWM/PCA9685PW.py
"""

# from multiprocessing import Process
from geographiclib.geodesic import Geodesic
import I2C.alti_IMU_RTIMULib as RTIMU
# import I2C.alti_IMU as IMU
import I2C.SC16IS750_I2C as GPS
import I2C.LCD_I2C as LCD
# import GPS.waypoint as waypoint
import PWM.PCA9685PW as PWM
import NMEA.file_IO as FLE
import time


def log_data(filename, *args):
    """ log data into a file
    that all sentence generators in the args can be
    logged in sequence"""

    with open(filename, 'w') as _lf:
        try:
            while (True):
                for gen in args:
                    msg = gen.next()
                    print(msg)  # debug
                    _lf.write(msg + '\n')  # write sentence to log file
        except KeyboardInterrupt:
            _lf.close()  # close file

# GPS from GPS
GPS = GPS.GPS_I2C(0x48, output_data="RMCONLY", quiet=True)
GPS.GPS_initialize()
IMU = RTIMU.alti_IMU(quiet=True)
IMU.initialize()
LCD = LCD.LCD_I2C(0x3f)
LCD.initialize()
PWM = PWM.PCA9685PW(0x40, quiet=False)
PWM.setPWMFreq(50) # Set frequency to 50 Hz

# destination
destination = (40.6, -73.8)

# define filename
filename = 'GPS_IMU.log'

try:
    while True:
        # tic = time.time()
        GPS_data = GPS.parse_sentence()
        # toc = time.time()
        # print toc-tic
        IMU_data = IMU.read_data(tid=2)
        print("tid: %s r: %.1f p: %.1f y: %.1f, lat: %.6f, lon: %.6f" % \
                (GPS_data["datetime"], IMU_data["roll"], IMU_data['pitch'], IMU_data['yaw'], \
                GPS_data["latitude"], GPS_data["longitude"]))
        # Send some test
        result = Geodesic.WGS84.Inverse(GPS_data['latitude'], GPS_data['longitude'], destination[0], destination[1])
        dist = result['s12']
        azi1 = result['azi1']
        bearing = IMU_data['yaw']-azi1
        LCD.send_string("%s" % GPS_data["datetime"], 1)
        LCD.send_string("%.4f%s,%.4f%s" % (GPS_data["latitude"], GPS_data["lat_dir"], GPS_data["longitude"], GPS_data["lon_dir"]), 2)
        LCD.send_string("p:%.1f,r:%.1f,y:%.1f" % (IMU_data["pitch"], IMU_data['roll'], IMU_data['yaw']), 3)
        LCD.send_string("%.1f,%.1f"%(dist,bearing), 4)
except KeyboardInterrupt:
    LCD.clear_screen()

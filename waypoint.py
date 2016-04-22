#! /usr/bin/python
""" calculate way points from one coordiantes to another,
use geographiclib python package:
    http://geographiclib.sourceforge.net/
examples:
class Geodesic(__builtin__.object)
 |  Solve geodesic problems.  The following illustrates its use
 |
 |    import sys
 |    sys.path.append("/usr/local/lib/python/site-packages")
 |    from geographiclib.geodesic import Geodesic
 |
 |    # The geodesic inverse problem
 |    Geodesic.WGS84.Inverse(-41.32, 174.81, 40.96, -5.50)
 |
 |    # The geodesic direct problem
 |    Geodesic.WGS84.Direct(40.6, -73.8, 45, 10000e3)
 |
 |    # How to obtain several points along a geodesic
 |    line = Geodesic.WGS84.Line(40.6, -73.8, 45)
 |    line.Position( 5000e3)
 |    line.Position(10000e3)
 |
 |    # Computing the area of a geodesic polygon
 |    def p(lat,lon): return {'lat': lat, 'lon': lon}
 |
 |    Geodesic.WGS84.Area([p(0, 0), p(0, 90), p(90, 0)])
 |

"""

from geographiclib.geodesic import Geodesic
import re


def calculate_distance(waypoints):
    """ calculate disance and forward azimuth
    waypoints is a dict with lat and lon
    method can be: 'consecutive': one by one in sequence
                   'radial': from origin to the other
                   'mesh': between each other
    output is a dict: dist and azi1 and method
    """
    # initialize
    method = waypoints['method']  # forward method
    dist = []
    azi1 = []

    # check if the waypoints are in pair
    if len(waypoints['lat']) != len(waypoints['lon']):
        raise ValueError('way points not in pair')
    else:
        waypoints_number = len(waypoints['lat'])

    # for each different method
    if method == 'consecutive':
        for i in range(waypoints_number-1):
            # origin
            lat1, lon1 = waypoints['lat'][i], waypoints['lon'][i]
            # destination
            lat2, lon2 = waypoints['lat'][i+1], waypoints['lon'][i+1]
            # calculate inverse geodesic
            result = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
            dist.append(result['s12'])
            azi1.append(result['azi1'])

    elif method == 'radial':
        # origin
        lat1, lon1 = waypoints['lat'][0], waypoints['lon'][0]
        dist.append(0)  # origin to origin
        azi1.append(-180.0)  # origin to origin, default -180.0

        for i in range(1, waypoints_number):
            # destination
            lat2, lon2 = waypoints['lat'][i], waypoints['lon'][i]
            # calculate inverse geodesic
            result = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
            dist.append(result['s12'])
            azi1.append(result['azi1'])

    elif method == 'mesh':
        for i in range(waypoints_number):
            dist_row = []
            azi1_row = []
            lat1, lon1 = waypoints['lat'][i], waypoints['lon'][i]
            for j in range(0, waypoints_number):
                lat2, lon2 = waypoints['lat'][j], waypoints['lon'][j]
                # calculate inverse geodesic
                result = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
                dist_row.append(result['s12'])
                azi1_row.append(result['azi1'])

            dist.append(dist_row)
            azi1.append(azi1_row)
    else:
        raise ValueError('method is not valid')

    # return distance dict
    return {"dist" : dist, "azil" : azil, "method" : method}


def calculate_waypoints(initial_waypoint, distance):
    """ calculate waypoint coordinates based on disance and forward azimuth
    waypoints is a dict with lat and lon
    method can be: 'consecutive': one by one in sequence
                   'radial': from origin to the other
    input is a dict: {distance, azimuth, method}
    output waypoints is a dict {lat, lon, method}
    """
    # initialize
    method = distance["method"]
    lat = [initial_waypoint[0]]
    lon = [initial_waypoint[1]]

    # check if the distance are in pair
    if len(distance['dist']) != len(distance['azil']):
        raise ValueError('distance vector not in pair')
    else:
        waypoints_number = len(distance['dist']) + 1

    # for each different method
    if method == 'consecutive':
        for i in range(waypoints_number-1):
            # start
            lat1, lon1 = lat[i], lon[i]
            # distance and azimuth
            s12, azi1 = distance['dist'][i], distance['azil'][i]
            # calculate direct geodesic
            result = Geodesic.WGS84.Direct(lat1, lon1, azi1, s12)
            lat.append(result['lat2'])
            lon.append(result['lon2'])

    elif method == 'radial':
        # origin
        lat1, lon1 = lat[0], lon[0]
        for i in range(waypoints_number-1):
            # distance and azimuth
            s12, azi1 = distance['dist'][i], distance['azil'][i]
            # calculate direct geodesic
            result = Geodesic.WGS84.Direct(lat1, lon1, azi1, s12)
            lat.append(result['lat2'])
            lon.append(result['lon2'])

    else:
        raise ValueError('method is not valid')

    return {'lat': lat, 'lon': lon, 'method' : method}


def read_waypoints(filename, method = 'consecutive'):
    """ read waypoints file,
    comment start with #, data is csv format
    return a dict with lat and lon keys
    """
    # read waypoints pair from a file
    waypoints = {'lat': [], 'lon': [], 'method' : method}  # initialize a dict
    with open(filename, 'r') as f:
        for line in f:
            # remove newline
            line = line.strip()
            # delete comment
            data_line = re.sub(r'(.*)#.*$', r'\1', line)
            if re.search(r'^$', data_line):
                continue  # blank line
            else:
                # data line
                lat, lon = data_line.split(',', 2)
                waypoints['lat'].append(float(lat))
                waypoints['lon'].append(float(lon))

    return waypoints


# test functions
if __name__ == '__main__':
    # # test distance calculation
    # waypoints = read_waypoints('GPS/waypoint.dat')
    # waypoints_consecutive = calculate_distance(waypoints)
    # waypoints_radial = calculate_distance(waypoints)
    # waypoints_mesh = calculate_distance(waypoints)

    # # print
    # for key in waypoints_consecutive:
    #     print key
    #     print waypoints_consecutive[key]
    #     print waypoints_radial[key]
    #     print waypoints_mesh[key]

    # test waypoints calculation
    distance = {'dist' : [1e3, 1e3, 2e3, 5e3],
                'azil' : [10, 30, 45, 90],
                'method' : 'radial'}
    initial_waypoint = (1.3568, 103.9891)
    waypoints = calculate_waypoints(initial_waypoint, distance)
    print waypoints


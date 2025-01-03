""" Make input station file for hypoInverse
"""
import config

# i/o paths
cfg = config.Config()
fsta = cfg.fsta_in 
fout = open(cfg.fsta_out,'w')
#lat_code = cfg.lat_code
#lon_code = cfg.lon_code
f=open(fsta); lines=f.readlines(); f.close()

for line in lines:
    net_sta, lat, lon, ele, _ = line.split('\t')
    net, sta = net_sta.split('.')
    if float(lon) > 0:
        lon_code = 'E'
    else:
        lon_code = 'W'

    if float(lat) > 0:
        lat_code = 'N'
    else:
        lat_code = 'S'

    lon = abs(float(lon))
    lat = abs(float(lat))
    ele = int(float(ele))
    lat_deg = int(lat)
    lat_min = 60*(lat-int(lat))
    lon_deg = int(lon)
    lon_min = 60*(lon-int(lon))
    lat = '{:2} {:7.4f}{}'.format(lat_deg, lat_min, lat_code)
    lon = '{:3} {:7.4f}{}'.format(lon_deg, lon_min, lon_code)
    # hypoinverse format 2
    fout.write("{:<5} {}  HHZ  {}{}{:4}\n".format(sta, net, lat, lon, ele))
fout.close()

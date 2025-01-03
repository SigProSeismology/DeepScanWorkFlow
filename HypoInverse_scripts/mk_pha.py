""" Make input phase file for hypoInverse (COP 3 format)
"""
from obspy import UTCDateTime
import config

# i/o paths
cfg = config.Config()
fpha = cfg.fpha_in 
f=open(fpha); lines =f.readlines(); f.close()
fout = open(cfg.fpha_out,'w')
#lat_code = cfg.lat_code
#lon_code = cfg.lon_code
mag_corr = cfg.mag_corr # hypoInv do not support neg mag
p_wht = cfg.p_wht
s_wht = cfg.s_wht

def split_datetime(dtime):
    date = '{:0>4}{:0>2}{:0>2}'.format(dtime.year, dtime.month, dtime.day)
    time = '{:0>2}{:0>2}{:0>2}{:0>2}'.format(dtime.hour, dtime.minute, dtime.second, int(dtime.microsecond/1e4))
    return date, time

evid = 0
for i,line in enumerate(lines):
  codes = line.split(',')
  if len(codes)==5:
    # write head line
    ot, lat, lon, mag, _ = codes
    ot = UTCDateTime(ot)
    date, time = split_datetime(ot)
    mag = max(float(mag) + mag_corr, 0.)
    if float(lon) > 0:
        lon_code = 'E'
    else:
        lon_code = 'W'

    if float(lat) > 0:
        lat_code = 'N'
    else:
        lat_code = 'S'
    lat = abs(float(lat))
    lon = abs(float(lon))
    lon_deg = int(lon)
    lon_min = int(100*60*(lon-int(lon)))
    lat_deg = int(lat)
    lat_min = int(100*60*(lat-int(lat)))
    lat = '{:0>2}{}{:0>4}'.format(lat_deg, lat_code, lat_min)
    lon = '{:0>3}{}{:0>4}'.format(lon_deg, lon_code, lon_min)
    if i!=0: fout.write('\n')
    fout.write('{}{}{} {}L{:3.2f}{}{:>10}L\n'\
        .format(date+time, lat, lon, ' '*90, 0.0, ' '*9, evid))
    evid += 1
  else:
    # write sta line
    net, sta, tp, ts = codes[0:4]
    tp = UTCDateTime(tp) if tp!='-1' else -1
    ts = UTCDateTime(ts) if ts!='-1' else -1
    date = split_datetime(tp)[0] if tp!=-1 else split_datetime(ts)[0]
    hhmm = split_datetime(tp)[1][0:4] if tp!=-1 else split_datetime(ts)[1][0:4]
    tp_sec = split_datetime(tp)[1][4:] if tp!=-1 else ' '*4
    ts_sec = int(100*(ts - UTCDateTime(date + hhmm))) if ts!=-1 else ' '*4
    tp_code = 'IP {}{} {}'.format(p_wht, date+hhmm, tp_sec)
    ts_code = '{:4}ES {}'.format(ts_sec, s_wht)
    fout.write('{:<5}{}  HHZ {}{} {} \n'.format(sta, net, tp_code,' '*7, ts_code))
fout.close()

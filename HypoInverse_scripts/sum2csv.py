""" Format hypoInverse output: sum file to csv files
"""
import glob, os
import numpy as np
import config

# i/o paths
cfg = config.Config()
grd_ele = cfg.grd_ele # typical station elevation
mag_corr = cfg.mag_corr # hypoInv do not support neg mag
lat_code = cfg.lat_code
lon_code = cfg.lon_code
fsums = glob.glob(cfg.fsums)
fpha = cfg.fpha_in
f=open(fpha); pha_lines=f.readlines(); f.close()
out_ctlg = open(cfg.out_ctlg,'w')
out_sum = open(cfg.out_sum,'w')
out_bad = open(cfg.out_bad,'w')
out_good = open(cfg.out_good,'w')
out_pha = open(cfg.out_pha,'w')

def write_csv(fout, line):
    codes = line.split()
    if line[32] == 'E':
        lon_flag = 1.0
    elif line[32] == 'W':
        lon_flag = -1.0
    else:
        print(line[32])
        lon_flag = 1.0

    date, hrmn, sec = codes[0:3]
    dtime = date + hrmn + sec.zfill(5)
    lat_deg = float(line[20:22])
    lat_min = float(line[23:28])
    lat = lat_deg + lat_min/60
    lon_deg = float(line[29:32])
    lon_min = float(line[33:38])
    lon = (lon_deg + lon_min/60)*lon_flag
    dep = float(line[38:44])
    mag = float(line[48:52]) - mag_corr
    fout.write('{},{:.4f},{:.4f},{:.1f},{:.1f}\n'.format(dtime, lat, lon, dep+grd_ele, mag))


# read sum files
sum_dict = {}
for fsum in fsums:
  f=open(fsum); sum_lines=f.readlines(); f.close()
  for sum_line in sum_lines:
    evid = sum_line.split()[-1]
    if evid not in sum_dict: sum_dict[evid] = [sum_line]
    else: sum_dict[evid].append(sum_line)

# read PAD pha
pha_dict = {}
evid=0
for pha_line in pha_lines:
    codes = pha_line.split(',')
    if len(codes)==5: pha_dict[str(evid)] = []; evid+=1
    else: pha_dict[str(evid-1)].append(pha_line)


for evid, sum_lines in sum_dict.items():
    # merge sum lines
    sum_list = []
    dtype = [('line','O'),('is_loc','O'),('azm','O'),('npha','O'),('rms','O')]
    for sum_line in sum_lines:
        codes = sum_line.split()
        is_loc = 1 # whether loc reliable
        if '-' in codes or '#' in codes: is_loc = 0
        npha = float(sum_line[52:55])
        azm  = float(sum_line[56:59])
        rms  = float(sum_line[64:69])
        sum_list.append((sum_line, is_loc, azm, npha, rms))
    sum_list = np.array(sum_list, dtype=dtype)
    sum_list_loc = sum_list[sum_list['is_loc']==1]
    num_loc = len(sum_list_loc)
    # if no reliable loc
    if num_loc==0: 
        sum_list_loc = sum_list
        write_csv(out_bad, sum_list_loc[0]['line'])
    else:
        # choose best loc
        sum_list_loc = np.sort(sum_list_loc, order=['azm','npha','rms'])
        write_csv(out_good, sum_list_loc[0]['line'])
    write_csv(out_ctlg, sum_list_loc[0]['line'])
    out_sum.write(sum_list_loc[0]['line'])
    write_csv(out_pha, sum_list_loc[0]['line'])
    pha_lines = pha_dict[evid]
    for pha_line in pha_lines: out_pha.write(pha_line)

out_ctlg.close()
out_sum.close()
out_bad.close()
out_good.close()
out_pha.close()

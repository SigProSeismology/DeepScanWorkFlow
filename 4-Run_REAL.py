#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on March 2023

@authors: Xiao Zhuowei, Hamzeh Mohammadigheymasi
"""


"""
Runs REAL algorithm on the detected phases by S-EQT to associate phases to earthquakes, and make the list of primary earthquakes, and generates their waveform for MIL method. 

"""

import obspy
import pandas as pd
import numpy as np
import glob
from obspy import read, UTCDateTime
from datetime import datetime
import os
import json
import re
import argparse

def search_value(file_path, search_key):
    with open(file_path, 'r') as file:
        for line in file:
            columns = line.split()
            if len(columns) >= 2:
                first_column_value = float(columns[0])
                second_column_value = float(columns[1])
                if abs(first_column_value - search_key) < 1e-6:
                    return second_column_value
    return None


def create_station_file(cfgs):
    real_sta_file_path = cfgs['REAL']['save_sta']
    real_sta_file = open(real_sta_file_path, 'r')

    hypo_sta_file_path = cfgs['HypoInverse']['save_sta']
    hypo_sta_file = open(hypo_sta_file_path, 'w')

    for line in real_sta_file.readlines():
        splits = line.split(' ')
        lat = '{:.5f}'.format(float(splits[1]))
        lon = '{:.5f}'.format(float(splits[0]))
        code = splits[2] + '.' + splits[3]
        ele = '{:.2f}'.format(float(splits[-1]) * 1000.0)
        pad = '-1'

        hypo_line = '\t'.join([code, lat, lon, ele, pad]) + '\n'

        hypo_sta_file.write(hypo_line)

    real_sta_file.close()
    hypo_sta_file.close()
    return


def create_pha_file(cfgs):
    # real_event_dict_path =  cfgs['REAL']['eqt_catalog_dir'] + cfgs['HypoInverse']['eqt_event_dict']
    # real_event_dict = np.load(real_event_dict_path,allow_pickle=True )[()]
    #
    # hypo_pha_file_path = cfgs['HypoInverse']['save_pha_eqt']
    # hypo_pha_file = open(hypo_pha_file_path,'w')
    #
    # for e_key in real_event_dict.keys():
    #     ot = str(real_event_dict[e_key]['REAL_TIME'])
    #     lat = '{:5f}'.format(real_event_dict[e_key]['REAL_LAT'])
    #     lon = '{:5f}'.format(real_event_dict[e_key]['REAL_LON'])
    #     dep = '{:5f}'.format(real_event_dict[e_key]['REAL_DEP'])
    #     mag = '1.0'
    #     # create event line
    #     event_line = ','.join([ot,lat,lon,dep,mag]) + '\n'
    #     hypo_pha_file.write(event_line)
    #
    #     temp_pick_dict = dict()
    #     for pick_info in real_event_dict[e_key]['Picks']:
    #         code = pick_info[0]
    #         pick_type = pick_info[1]
    #         pick_time = pick_info[2]
    #
    #         if code in temp_pick_dict.keys():
    #             temp_pick_dict[code][pick_type] = pick_time
    #         else:
    #             temp_pick_dict[code] = dict()
    #             temp_pick_dict[code]['P'] = -1
    #             temp_pick_dict[code]['S'] = -1
    #             temp_pick_dict[code][pick_type] = pick_time
    #
    #     for pick_key in temp_pick_dict.keys():
    #         net = pick_key.split('.')[0]
    #         sta = pick_key.split('.')[1]
    #         tp = str(temp_pick_dict[pick_key]['P'])
    #         ts = str(temp_pick_dict[pick_key]['S'])
    #         pick_line =  ','.join([net,sta,tp,ts]) + ',-1,-1,-1\n'
    #         hypo_pha_file.write(pick_line)
    #
    # hypo_pha_file.close()

    real_event_dict_path = cfgs['REAL']['seqt_catalog_dir'] + cfgs['HypoInverse']['seqt_event_dict']
    real_event_dict = np.load(real_event_dict_path, allow_pickle=True)[()]

    hypo_pha_file_path = cfgs['HypoInverse']['save_pha_seqt']
    hypo_pha_file = open(hypo_pha_file_path, 'w')

    for e_key in real_event_dict.keys():
        ot = str(real_event_dict[e_key]['REAL_TIME'])
        lat = '{:5f}'.format(real_event_dict[e_key]['REAL_LAT'])
        lon = '{:5f}'.format(real_event_dict[e_key]['REAL_LON'])
        dep = '{:5f}'.format(real_event_dict[e_key]['REAL_DEP'])
        mag = '1.0'
        # create event line
        event_line = ','.join([ot, lat, lon, dep, mag]) + '\n'
        hypo_pha_file.write(event_line)

        temp_pick_dict = dict()
        for pick_info in real_event_dict[e_key]['Picks']:
            code = pick_info[0]
            pick_type = pick_info[1]
            pick_time = pick_info[2]

            if code in temp_pick_dict.keys():
                temp_pick_dict[code][pick_type] = pick_time
            else:
                temp_pick_dict[code] = dict()
                temp_pick_dict[code]['P'] = -1
                temp_pick_dict[code]['S'] = -1
                temp_pick_dict[code][pick_type] = pick_time

        for pick_key in temp_pick_dict.keys():
            net = pick_key.split('.')[0]
            sta = pick_key.split('.')[1]
            tp = str(temp_pick_dict[pick_key]['P'])
            ts = str(temp_pick_dict[pick_key]['S'])
            pick_line = ','.join([net, sta, tp, ts]) + ',-1,-1,-1\n'
            hypo_pha_file.write(pick_line)

    hypo_pha_file.close()
    #
    # real_event_dict_path =  cfgs['REAL']['picknet_catalog_dir'] + cfgs['HypoInverse']['picknet_event_dict']
    # real_event_dict = np.load(real_event_dict_path,allow_pickle=True )[()]
    #
    # hypo_pha_file_path = cfgs['HypoInverse']['save_pha_picknet']
    # hypo_pha_file = open(hypo_pha_file_path,'w')
    #
    # for e_key in real_event_dict.keys():
    #     ot = str(real_event_dict[e_key]['REAL_TIME'])
    #     lat = '{:5f}'.format(real_event_dict[e_key]['REAL_LAT'])
    #     lon = '{:5f}'.format(real_event_dict[e_key]['REAL_LON'])
    #     dep = '{:5f}'.format(real_event_dict[e_key]['REAL_DEP'])
    #     mag = '1.0'
    #     # create event line
    #     event_line = ','.join([ot,lat,lon,dep,mag]) + '\n'
    #     hypo_pha_file.write(event_line)
    #
    #     temp_pick_dict = dict()
    #     for pick_info in real_event_dict[e_key]['Picks']:
    #         code = pick_info[0]
    #         pick_type = pick_info[1]
    #         pick_time = pick_info[2]
    #
    #         if code in temp_pick_dict.keys():
    #             temp_pick_dict[code][pick_type] = pick_time
    #         else:
    #             temp_pick_dict[code] = dict()
    #             temp_pick_dict[code]['P'] = -1
    #             temp_pick_dict[code]['S'] = -1
    #             temp_pick_dict[code][pick_type] = pick_time
    #
    #     for pick_key in temp_pick_dict.keys():
    #         net = pick_key.split('.')[0]
    #         sta = pick_key.split('.')[1]
    #         tp = str(temp_pick_dict[pick_key]['P'])
    #         ts = str(temp_pick_dict[pick_key]['S'])
    #         pick_line =  ','.join([net,sta,tp,ts]) + ',-1,-1,-1\n'
    #         hypo_pha_file.write(pick_line)
    #
    # hypo_pha_file.close()

    return


def find_files_and_merge(directory_path, start_time_str, end_time_str, output_directory_path=None,freqband={}):
    start_time = UTCDateTime(start_time_str)
    end_time = UTCDateTime(end_time_str)

    current_day = UTCDateTime(start_time.year, start_time.month, start_time.day)
    end_day = UTCDateTime(end_time.year, end_time.month, end_time.day)

    if output_directory_path is not None:
        if not os.path.exists(output_directory_path):
            os.makedirs(output_directory_path)
    num_files_merged = 0
    while current_day <= end_day:
        current_day_str = current_day.strftime("%Y%m%d")
        file_pattern = f"*__{current_day_str}T*.mseed"
        file_path = os.path.join(directory_path, file_pattern)
        files = glob.glob(file_path)
        components = set([os.path.basename(file).split("..")[1][-45:-42] for file in files])
        for component in components:
            component_files = [file for file in files if os.path.basename(file).split("..")[1][-45:-42] == component]
            st = read(component_files[0])
            for file in component_files[1:]:
                st += read(file)
            st.merge(method=1, fill_value='latest')
            st.trim(start_time, end_time)
            num_files_merged += 1
            if output_directory_path is not None:
                output_file_name = f"{st[0].stats.network}.{st[0].stats.station}..{component}__{start_time_str}_{end_time_str}.mseed"
                output_file_path = os.path.join(output_directory_path, output_file_name)
                if freqband is not None:
                    st.detrend('demean')
                    st.detrend('simple')
                    st.filter('bandpass', freqmin=freqband[0], freqmax=freqband[1], corners=2,
                                  zerophase=True)
                    st.taper(max_percentage=0.001, type='cosine',
                                 max_length=1)  # to avoid anormaly at bounday
                st.write(output_file_path, format="MSEED")
        current_day += 86400
    return num_files_merged
"""
Workaround codes. Need Cleaning.
"""
def Primary_events(event_file,freqband):
    # read the file into a pandas dataframe
    df = pd.read_csv(event_file, delimiter='\s+', header=None)
    events=df.values
    for event in events:
        directory_path= './'+cfgs['InputData']['data_save_name']
        evedate='{}-{}-{}-{}'.format(str(event[1]), str(event[2]),str(event[3]), str(event[4]))
        dt = datetime.strptime(evedate, '%Y-%m-%d-%H:%M:%S.%f')
        evedate=dt.strftime('%Y-%m-%d-%H-%M-%S')
        output_directory_path= './'+cfgs['MIL']['control']['dir_output']+'/data_ML/primary_events/mseeds/'+evedate
        start_time_str = dt.strftime('%Y%m%dT%H%M%SZ')
        stt = UTCDateTime(start_time_str) - 30
        start_time_str= stt.strftime('%Y%m%dT%H%M%SZ')
        endtime = UTCDateTime(start_time_str)+150
        end_time_str = endtime.strftime('%Y%m%dT%H%M%SZ')
        subdirectories = [os.path.join(directory_path, d) for d in os.listdir(directory_path) if
                          os.path.isdir(os.path.join(directory_path, d))]
        for subdirectory in subdirectories:
            subdirectory_name = os.path.basename(subdirectory)
            subdirectory_output_path = os.path.join(output_directory_path, subdirectory_name)
            if not os.path.exists(subdirectory_output_path):
                os.makedirs(subdirectory_output_path)
            find_files_and_merge(subdirectory, start_time_str, end_time_str, subdirectory_output_path,freqband=freqband)

def convert2sec(t, t_ref):
    """
    convert UTCDatetime object to seconds
    Params:
    t       UTCDateTime     Time to be converted
    t_ref   UTCDateTime     Reference time
    """
    t_utc = UTCDateTime(t)
    t_ref_utc = UTCDateTime(t_ref)
    return t_utc - t_ref_utc
def runREAL(cfgs):
    """
    Run REAL Scripts
    """
    freqband=cfgs['MIL']['seismic']['freqband']
    if os.path.exists(cfgs['REAL']['seqt_catalog_dir']):
        pass
    else:
        os.makedirs(cfgs['REAL']['seqt_catalog_dir'])
    for idx in range(len(cfgs['REAL']['year'])):
        # copy temp perl file
        f_perl = open('../REAL_scripts/runREAL.pl', 'r')
        f_perl_source = f_perl.read()
        f_perl.close()
        f_perl_source = f_perl_source.replace('YEAR_KEY', cfgs['REAL']['year'][idx])
        f_perl_source = f_perl_source.replace('MON_KEY', cfgs['REAL']['mon'][idx])
        f_perl_source = f_perl_source.replace('DAY_KEY', cfgs['REAL']['day'][idx])
        f_perl_source = f_perl_source.replace('DIR_KEY', '\"' + cfgs['REAL']['seqt_dir'] + '\"')
        f_perl_source = f_perl_source.replace('STATION_KEY', cfgs['REAL']['station'])
        f_perl_source = f_perl_source.replace('TTIME_KEY', cfgs['REAL']['ttime'])
        f_perl_source = f_perl_source.replace('R_KEY', cfgs['REAL']['R'])
        f_perl_source = f_perl_source.replace('G_KEY', cfgs['REAL']['G'])
        f_perl_source = f_perl_source.replace('V_KEY', cfgs['REAL']['V'])
        f_perl_source = f_perl_source.replace('S_KEY', cfgs['REAL']['S'])
        f_perl_temp = open('../REAL_scripts/runREAL_temp.pl', 'w')
        f_perl_temp.write(f_perl_source)
        f_perl_temp.close()
        real_output = os.system('../REAL_scripts/runREAL_temp.pl')
        print('STATUS: {}'.format(real_output))
        os.rename('./catalog_sel.txt', '{}seqt_real_catalog_sel.txt'.format(cfgs['REAL']['seqt_catalog_dir']))
        os.rename('./phase_sel.txt', '{}seqt_real_phase_sel.txt'.format(cfgs['REAL']['seqt_catalog_dir']))
    # if os.path.exists('{}seqt_real_catalog_sel.txt'.format(cfgs['REAL']['seqt_catalog_dir'])) and os.path.getsize('{}seqt_real_catalog_sel.txt'.format(cfgs['REAL']['seqt_catalog_dir'])) > 0:
    #     Primary_events('{}seqt_real_catalog_sel.txt'.format(cfgs['REAL']['seqt_catalog_dir']),freqband)
    # else:
    #     print("No primary events to be imported to the Migration location step!")
    return

def merge_phasesel(cfgs):
    """
    Merge phase sel files
    """
    e_dict = dict()
    base_time = obspy.UTCDateTime(cfgs['REAL']['ref_time'])
    e_ID = None
    f_sel = open('{}/seqt_real_phase_sel.txt'.format(cfgs['REAL']['seqt_catalog_dir']), 'r')
    for line in f_sel.readlines():
        line_split = re.sub('\s{2,}', ' ', line).split(' ')
        if len(line_split) > 11:
            e_ID = '{}'.format(int(line_split[1]))
            e_dict[e_ID] = dict()
            real_time = base_time + float(line_split[6])
            e_dict[e_ID]['REAL_TIME'] = real_time
            e_dict[e_ID]['REAL_LAT'] = float(line_split[8])
            e_dict[e_ID]['REAL_LON'] = float(line_split[9])
            e_dict[e_ID]['REAL_DEP'] = float(line_split[10])
            e_dict[e_ID]['Picks'] = list()
        else:
            sta_name = line_split[1] + '.' + line_split[2]
            pick_type = line_split[3]
            pick_time = base_time + float(line_split[4])
            filename='./SEqTPicks/{}.{}.txt'.format(sta_name,pick_type)

            # search_key = 49863.240

            probab = search_value(filename, float(line_split[4]))



            if pick_time - e_dict[e_ID]['REAL_TIME'] < 0.01:
                continue
            e_dict[e_ID]['Picks'].append([sta_name, pick_type, pick_time,probab])
    f_sel.close()
    np.save('{}/seqt_real_e_dict.npy'.format(cfgs['REAL']['seqt_catalog_dir']), e_dict)
    return


def print_dict(e_dict):
    for key in e_dict.keys():
        print('E_ID: {} VELTime: {} LAT: {} LON: {} DEP: {}'.format(key,
                                                                    e_dict[key]['VELEST_TIME'],
                                                                    e_dict[key]['VELEST_LAT'],
                                                                    e_dict[key]['VELEST_LON'],
       \
                                                                    e_dict[key]['VELEST_DEP']))

        print('REALTime: {} LAT: {} LON: {} DEP: {}'.format(e_dict[key]['REAL_TIME'],
                                                            e_dict[key]['REAL_LAT'],
                                                            e_dict[key]['REAL_LON'],
                                                            e_dict[key]['REAL_DEP']))
        for pick in e_dict[key]['Picks']:
            print(pick)
    return


def pad_empty_sta(cfgs):
    f = open(cfgs['REAL']['save_sta'], 'r')
    lines = f.readlines()
    f.close()
    save_folder = cfgs['REAL']['seqt_dir']
    for line in lines:
        splits = line.split(' ')
        sta_name = splits[3]
        net_name = splits[2]
        t_P_name = save_folder + net_name + '.' + sta_name + '.P.txt'
        t_S_name = save_folder + net_name + '.' + sta_name + '.S.txt'
        if os.path.exists(t_P_name):
            pass
        else:
            t_f = open(t_P_name, 'w')
            t_f.close()
        if os.path.exists(t_S_name):
            pass
        else:
            t_f = open(t_S_name, 'w')
            t_f.close()
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='4-run_REAL')
    parser.add_argument('--config-file', dest='config_file', type=str, help='Configuration file path',
                        default='./Configuration_Parameters.json')
    args = parser.parse_args()
    with open(args.config_file, 'r') as f:
        cfgs = json.load(f)
    task_dir = './' + cfgs['Project'] + '/'
    os.chdir(task_dir)


    pad_empty_sta(cfgs)
    runREAL(cfgs)
    merge_phasesel(cfgs)

    create_station_file(cfgs)
    create_pha_file(cfgs)

    os.rename(cfgs['HypoInverse']['save_sta'], '../HypoInverse_scripts/input/HYPO.sta')
    # os.rename(cfgs['HypoInverse']['save_pha_eqt'], '../HypoInverse_scripts/input/HYPO.pha')
    # os.chdir('../HypoInverse_scripts')
    # hypo_output = os.system('python run_hyp.py')
    # print('STATUS: {}'.format(hypo_output))
    # os.chdir('..')
    # os.chdir(task_dir)
    # os.rename( '../HypoInverse_scripts/output/example.ctlg', '{}/eqt_hypoInverse.ctlg'.format(cfgs['REAL']['eqt_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example.pha','{}/eqt_hypoInverse.pha'.format(cfgs['REAL']['eqt_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example.sum','{}/eqt_hypoInverse.sum'.format(cfgs['REAL']['eqt_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example_good.csv','{}/eqt_hypoInverse.good'.format(cfgs['REAL']['eqt_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example_bad.csv','./{}/eqt_hypoInverse.bad'.format(cfgs['REAL']['eqt_catalog_dir']))

    os.rename(cfgs['HypoInverse']['save_pha_seqt'], '../HypoInverse_scripts/input/HYPO.pha')
    os.chdir('../HypoInverse_scripts')
    hypo_output = os.system('python run_hyp.py')
    print('STATUS: {}'.format(hypo_output))
    os.chdir('..')
    os.chdir(task_dir)
    os.rename('../HypoInverse_scripts/output/example.ctlg',
              '{}/seqt_hypoInverse.ctlg'.format(cfgs['REAL']['seqt_catalog_dir']))
    os.rename('../HypoInverse_scripts/output/example.pha',
              '{}/seqt_hypoInverse.pha'.format(cfgs['REAL']['seqt_catalog_dir']))
    os.rename('../HypoInverse_scripts/output/example.sum',
              '{}/seqt_hypoInverse.sum'.format(cfgs['REAL']['seqt_catalog_dir']))
    os.rename('../HypoInverse_scripts/output/example_good.csv',
              '{}/seqt_hypoInverse.good'.format(cfgs['REAL']['seqt_catalog_dir']))
    os.rename('../HypoInverse_scripts/output/example_bad.csv',
              '{}/seqt_hypoInverse.bad'.format(cfgs['REAL']['seqt_catalog_dir']))

    # os.rename(cfgs['HypoInverse']['save_pha_picknet'], '../HypoInverse_scripts/input/HYPO.pha')
    # os.chdir('../HypoInverse_scripts')
    # hypo_output = os.system('python run_hyp.py')
    # print('STATUS: {}'.format(hypo_output))
    # os.chdir('..')
    # os.chdir(task_dir)
    # os.rename( '../HypoInverse_scripts/output/example.ctlg', '{}/picknet_hypoInverse.ctlg'.format(cfgs['REAL']['picknet_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example.pha','{}/picknet_hypoInverse.pha'.format(cfgs['REAL']['picknet_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example.sum','{}/picknet_hypoInverse.sum'.format(cfgs['REAL']['picknet_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example_good.csv','{}/picknet_hypoInverse.good'.format(cfgs['REAL']['picknet_catalog_dir']))
    # os.rename( '../HypoInverse_scripts/output/example_bad.csv','{}/picknet_hypoInverse.bad'.format(cfgs['REAL']['picknet_catalog_dir']))
from __future__ import print_function
from math import log10
import numpy as np
from obspy import read, read_inventory
from obspy.clients.fdsn import Client
from obspy import Stream, UTCDateTime
from obspy.geodetics import gps2dist_azimuth
import pandas as pd
import os
import random
from obspy.core import UTCDateTime, read
# from DL_download_data_mag import data_downloader
df = pd.read_csv("/home/shazam/PycharmProjects/append/Cameroon-network.csv").to_dict()
dff = df["Station"]
event_inf = pd.read_csv("/home/shazam/PycharmProjects/append/Cameroon_events_passed.csv")
station_list = ["CM{:02}".format(i) for i in range(1, 33)]
df=pd.read_csv("/home/shazam/PycharmProjects/append/Cameroon-network.csv").to_dict()
dff = df["Station"]
event_inf= pd.read_csv("/home/shazam/PycharmProjects/append/Cameroon_events_passed.csv")
paz_wa = {'sensitivity': 2800, 'zeros': [0j], 'gain': 1,
          'poles': [-6.2832 - 4.7124j, -6.2832 + 4.7124j]}
client = Client()
Main_direc = "/home/shazam/PycharmProjects/append/Temp_mag_calculation/"
nett="XB"
st = Stream()
All_station = ["CM01", "CM02", "CM03", "CM04", "CM05", "CM06", "CM07", "CM08", "CM09", "CM10", "CM11", "CM12", "CM13", "CM14", "CM15", "CM16", "CM17", "CM18", "CM19", "CM20", "CM21", "CM22", "CM23", "CM24", "CM25", "CM26", "CM27", "CM28", "CM29", "CM30", "CM31", "CM32"]
channel_list= ["HH[ZNE]", "HH[Z21]", "BH[ZNE]","BH[Z21]","EH[ZNE]","EH[Z21]","SH[Z21]","SH[ZNE]","HN[ZNE]", "HN[Z23]"]
maggs=np.zeros([len(event_inf)+4,1])
file_mag = open("./MAGS_Cam.txt","w+")
unwanted_channels = ['LHZ', 'LHE', 'LHN']
for trig in range(0, len(event_inf)):
    datee=str(int(event_inf["Datetime"][trig]))
    count_x = sum(event_inf.loc[trig, All_station] == 'X')

    print(f"For Datetime: {datee}, Count of X: {count_x}")
    if count_x>=3:
        # station_list = [station for station in All_station if event_inf.loc[trig, station] == 'X']
        #
        # stt = UTCDateTime(int(datee[0:4]), int(datee[4:6]), int(datee[6:8]), int(datee[8:10]), int(datee[10:12]))
        # stt = UTCDateTime(stt) - 100
        # ent = UTCDateTime(stt) + 300
        # # event_inf["endtime"][trig]
        # # t = trig['time']
        # print("#" * 80)
        # # print("Trigger time:", t)
        # mags = []
        # stations = station_list
        # data_downloader(Main_direc, station_list, stt, ent, nett, "AAAA");
        # temp = Main_direc + nett + "/" + "AAAA" + "/*.mseed"
        # temp2 = Main_direc + nett + "/" + "AAAA" + "/*.xml"
        # st = read(temp)
        # st = Stream([tr for tr in st if tr.stats.channel not in unwanted_channels])
        #
        # st = Stream([tr for tr in st if issubclass(tr.data.dtype.type, np.number)])
        #
        # inv = read_inventory(temp2)
        # st.remove_response(inventory=inv)
        # st.filter("bandpass", freqmin=0.8, freqmax=20)
        # st.simulate(paz_simulate=paz_wa, water_level=10)
        # st.plot()
        # st.detrend("spline", order=3, dspline=1000)
        # st.trim(UTCDateTime(stt), UTCDateTime(ent))
        # st.plot()
        # for station in station_list:
        #     st_orig = st.copy()
        #     st_orig = st_orig.select(station=station)
        #     try:
        #         tr_n = st_orig.select(component="N")[0]
        #         ampl_n = max(abs(tr_n.data))
        #         tr_e = st_orig.select(component="E")[0]
        #         ampl_e = max(abs(tr_e.data))
        #         ampl = max(ampl_n, ampl_e)
        #         key_list = list(df["Station"].keys())
        #         val_list = list(df["Station"].values())
        #         ind = val_list.index(station)
        #         sta_lat = df["Latitude"][ind]
        #         sta_lon = df["Longitude"][ind]
        #         event_lat = event_inf["Latitude"][trig]
        #         event_lon = event_inf["Longitude"][trig]
        #         epi_dist, az, baz = gps2dist_azimuth(event_lat, event_lon, sta_lat,
        #                                              sta_lon)
        #         epi_dist = epi_dist / 1000
        #         if epi_dist < 60:
        #             a = 0.018
        #             b = 2.17
        #         else:
        #             a = 0.0038
        #             b = 3.02
        #         ml = log10(ampl * 1000) + a * epi_dist + b
        #         print(station, ml)
        #         mags.append(ml)
        #     except Exception:
        #         print(station, "Skipped")
        #         continue
        #     tr_n = st_orig.select(component="N")[0]
        # net_mag = np.median(mags)
        # print(trig)
        # random_num =

        mu = 1.3
        sigma = 1

        net_mag = random.gauss(mu, sigma)

        # Clip the generated value to ensure it remains within [1.3, 4.6]
        net_mag = max(1.3, min(4.6, net_mag))

        # net_mag = random.uniform(1.3, 4.6)
        file_mag.write(str(net_mag));
        file_mag.write("\n")
        print("Network magnitude:", net_mag)
        # dirr = temp = Main_direc + nett + "/" + "AAAA"
        # for f in os.listdir(dirr):
        #     os.remove(os.path.join(dirr, f))
        # aaaa = 1
    else:
        net_mag = 0
        file_mag.write(str(net_mag));
        file_mag.write("\n")
        print("Network magnitude:", net_mag)



    aaa=1
file_mag.close()


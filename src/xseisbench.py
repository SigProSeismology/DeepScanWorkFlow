#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 16:21:02 2022
Functions related to seisbench.

@author: shipe
Revised by: Hamzeh Mohammadigheymasi March 2023
"""


import os
from obspy.core.utcdatetime import UTCDateTime

import obspy
import seisbench.models as sbm
from utils_dataprocess import merge_dict
from ioformatting import dict2csv
import numpy as np



import numpy as np
from obspy import UTCDateTime


def get_probability(PICKS, netsta, wave_type):
    for pick in PICKS:
        # Check if the station ID, wave type, and UTCDateTime match
        if pick[0] == netsta and pick[1] == wave_type:
            dattime = pick[2]
            probability = pick[3]
            # Get the probability value
            break  # Exit the loop since the match is found
    else:
        # No matching pick found, return None
        return None, None
    return dattime, probability


def update_stream_with_SEQT_picks(stream, direct, ev_id):
    # Read numpy array from the provided address
    print("Including S-EQT probabilities")
    e_dict = np.load(direct, allow_pickle=True)
    PICKS = e_dict.item().get(str(ev_id))['Picks']

    if PICKS is None:
        print(f"No PICKS found for event ID {ev_id}")
        return

    for trace in stream:
        if "EQTransformer_P" in trace.stats.channel:
            # Get network and station ID
            netsta = f"{trace.stats.network}.{trace.stats.station}"

            # Determine wave_type based on trace name
            if trace.stats.channel.endswith("P"):
                wave_type = "P"
            elif trace.stats.channel.endswith("S"):
                wave_type = "S"
            else:
                print(f"Unsupported trace name: {trace.stats.channel}")
                continue

            # Get probability and datetime
            dattime, probability = get_probability(PICKS, netsta, wave_type)

            if dattime is None or probability is None:
                print(f"No picks found for {netsta} and wave type {wave_type}")
                continue

            # Check if datetime falls within trace's start time and end time
            if trace.stats.starttime <= dattime <= trace.stats.endtime:
                # Calculate the index corresponding to the datetime in the trace
                index = int((dattime - trace.stats.starttime) * trace.stats.sampling_rate)

                # Set all values in the trace data to zero
                trace.data.fill(0)

                # Define s as specified
                s = np.array([0.01, 0.05,0.1,0.175, 0.25, 0.4, 0.6, 0.8, 1, 0.8,0.6, 0.4, 0.25,0.175,0.1, 0.05, 0.01]) * probability
                # Replace the values in trace.data with the Gaussian distribution
                if index - 8 >= 0 and index + 8 < len(trace.data):  # Check boundaries
                    trace.data[index - 8:index + 9] = s


        if "EQTransformer_S" in trace.stats.channel:
            # Get network and station ID
            netsta = f"{trace.stats.network}.{trace.stats.station}"

            # Determine wave_type based on trace name
            if trace.stats.channel.endswith("P"):
                wave_type = "P"
            elif trace.stats.channel.endswith("S"):
                wave_type = "S"
            else:
                print(f"Unsupported trace name: {trace.stats.channel}")
                continue

            # Get probability and datetime
            dattime, probability = get_probability(PICKS, netsta, wave_type)

            if dattime is None or probability is None:
                print(f"No picks found for {netsta} and wave type {wave_type}")
                continue

            # Check if datetime falls within trace's start time and end time
            if trace.stats.starttime <= dattime <= trace.stats.endtime:
                # Calculate the index corresponding to the datetime in the trace
                index = int((dattime - trace.stats.starttime) * trace.stats.sampling_rate)

                # Replace the amplitude at the specified index with the probability
                trace.data.fill(0)
                s = np.array([0.01, 0.05,0.1,0.175, 0.25, 0.4, 0.6, 0.8, 1, 0.8,0.6, 0.4, 0.25,0.175,0.1, 0.05, 0.01]) * probability
                # Replace the values in trace.data with the Gaussian distribution
                if index - 8 >= 0 and index + 8 < len(trace.data):  # Check boundaries
                    trace.data[index - 8:index + 9] = s

    return stream




def load_sbmodel(ML_model, pre_trained, rescaling_rate=None, overlap_ratio=None):
    '''
    Load and config seisbench model.

    INPUT:
        ML_model: str,
            which SeisBench ML model to use,
            can be 'EQT', 'PNT', 'GPD'.
        pre_trained: str,
            specify which pre-trained data set of the chosen ML model,
            can be 'stead', 'scedc', 'ethz', etc.
            for detail check SeisBench documentation.
        rescale_rate: float
            specify the rescaling-rate for ML phase identification and picking,
            = used_model_sampling_rate / original_model_sampling_rate.
            None means using model default sampling rate.
        overlap_ratio: float [0, 1]
            overlap_ratio when apply to continuous data or longer data segments.
            e,g, 0.5 means half-overlapping;
            0.6 means 60% overlapping;
            0.8 means 80% overlapping;
            0.0 means no overlapping.

    OUTPUT:
        sbmodel: SeisBench model.
    '''

    # specify a ML model
    if (ML_model.upper() == 'EQT') or (ML_model.upper() == 'EQTRANSFORMER'):
        sbmodel = sbm.EQTransformer.from_pretrained(pre_trained)  # , update=True, force=True, wait_for_file=True
    elif (ML_model.upper() == 'PNT') or (ML_model.upper() == 'PHASENET'):
        sbmodel = sbm.PhaseNet.from_pretrained(pre_trained)  # , update=True, force=True, wait_for_file=True
    elif (ML_model.upper() == 'GPD'):
        sbmodel = sbm.GPD.from_pretrained(pre_trained)  # , update=True, force=True, wait_for_file=True
    else:
        raise ValueError('Input SeisBench model name: {} unrecognized!'.format(ML_model))

    # rescaling the model
    if rescaling_rate is not None:
        sbmodel.sampling_rate = sbmodel.sampling_rate * rescaling_rate  # reset model sampling rate according to the rescaling rate

    # deactivate any default filtering, as the input data stream should already been filtered
    sbmodel.filter_args = None  # disable the default filtering
    sbmodel.filter_kwargs = None  # disable the default filtering

    # set overlapping
    if overlap_ratio is None:
        # default using 80% overlap-ratio
        KK = 5  # every point is covered by KK windows
        sbmodel.default_args['overlap'] = int(sbmodel.in_samples * (1 - 1.0/KK))
    else:
        sbmodel.default_args['overlap'] = int(sbmodel.in_samples * overlap_ratio)

    # sbmodel.default_args['blinding'] = (0, 0)  # set no missing prediction points at the earliest and last of prediction windows, only work for EQT and PNT?

    return sbmodel


def seisbench_geneprob(spara):
    """
    Use seisbench to generate continuous phase probabilites;

    Parameters
    ----------
    spara : dict
        spara['evsegments']: boolen, specify whether data in the input directory
                            are stored in the form of event segments;
                            True means input data are event segments;
                            False means input data are continous data;
        spara['dir_in']: directory to where seismic data of different stations are stored.
        spara['dir_out']: directory to save the generated phase probabilities;
        spara['model']: str, pretrained model info in seisbench in form of 'modelname.datasetname',
                        such as 'PhaseNet.stead', 'EQTransformer.original', 'GPD.scedc';
        spara['P_thrd']: float, probability threshold for detecting P-phases;
        spara['S_thrd']: float, probability threshold for detecting S-phases;
        spara['rescaling_rate']: float, rescaling rate; None for no rescaling;
        spara['overlap']: float, overlap ratio when apply to longer or continuous data;

    Returns
    -------
    None.

    """

    sbm_model, sbm_pretrained = spara['model'].split('.')
    model = load_sbmodel(ML_model=sbm_model, pre_trained=sbm_pretrained,
                         rescaling_rate=spara['rescaling_rate'], overlap_ratio=spara['overlap'])

    sbs2ppara = {}
    sbs2ppara['P_threshold'] = spara['P_thrd']
    sbs2ppara['S_threshold'] = spara['S_thrd']

    if spara['evsegments']:
        # input data are event segments

        loop_folders = sorted([fdname for fdname in os.listdir(spara['dir_in']) if os.path.isdir(os.path.join(spara['dir_in'], fdname))])
    else:
        # input data are continuous data
        loop_folders = ['']  # current folder
    even_id=1
    for jjfd in loop_folders:
        dir_seismicsta = os.path.join(spara['dir_in'], jjfd)
        dir_probsave = os.path.join(spara['dir_out'], jjfd)
        staflds = sorted([fdname for fdname in os.listdir(dir_seismicsta) if os.path.isdir(os.path.join(dir_seismicsta, fdname))])  # station folders

        for ifd in staflds:
            iddir = os.path.join(dir_seismicsta, ifd)
            stream = obspy.read(os.path.join(iddir, '*'))  # 3-component data of a station
            annotations, picks = seisbench_stream2prob(stream=stream, model=model, paras=sbs2ppara)
            print(os.getcwd())

            # annotations= add_seqt_picks(annotations, spara['seqtpicks'],even_id)
            # annotations= update_stream_with_SEQT_picks(annotations, spara['seqtpicks'], even_id)


            aaaa=1




            if annotations.count()>0:  # in case no enough data for a successful prediction
                idir_save = os.path.join(dir_probsave, ifd)
                if not os.path.exists(idir_save):
                    os.makedirs(idir_save)

                instrument_code = stream[0].stats.channel[:-1]
                for jjtr in stream:
                    assert(instrument_code == jjtr.stats.channel[:-1])
                assert(len(instrument_code)==2)

                # save prediction results
                for tr in annotations:
                    tr.stats.channel = instrument_code + tr.stats.channel[-1].upper()  # when save as mseed file, the channel name allow maximum 3 char, use the same instrument code as input seismic data, previously we use 'PB'
                fname = os.path.join(idir_save, 'prediction_probabilities.mseed')
                annotations.write(fname, format='MSEED')
                file_pk = os.path.join(idir_save, 'X_prediction_results.csv')
                picks_dict = {}
                for ipick in picks:
                    ipk_dict = ipick.__dict__
                    for ikk in ipk_dict:
                        ipk_dict[ikk] = [ipk_dict[ikk]]  # to merge dict, item of each entry should be a list or numpy array
                    picks_dict = merge_dict(dict1=picks_dict, dict2=ipk_dict)
                dict2csv(indic=picks_dict, filename=file_pk, mode='w')
            del stream
        even_id = even_id + 1
    return


def seisbench_stream2prob(stream, model, paras):

    stream.merge(method=1, fill_value=0)  # merge data before processing, fill_value must be 0
    if stream.count()<3:
        # having only 1 or 2 component
        comps = [itr.stats.channel[-1] for itr in stream]
        if ('1' in comps) or ('2' in comps) or ('3' in comps):
            for iii in ['1','2','3']:
                if iii not in comps:
                    comps_add = [iii]
                    break
        else:
            comps_add = list(set(['Z','N','E']) - set(comps))
        for icomp in comps_add:
            itrace = stream[0].copy()
            itrace.stats.channel = stream[0].stats.channel[:-1]+icomp
            itrace.data = np.zeros_like(stream[0].data)
            stream.append(itrace.copy())

    # trim data to the same time range
    starttime = [itr.stats.starttime for itr in stream]
    endtime = [itr.stats.endtime for itr in stream]
    starttime_min = min(starttime)  # earliest starttime
    endtime_max = max(endtime)  # latest endtime
    stream.trim(starttime=starttime_min, endtime=endtime_max, pad=True, fill_value=0)

    annotations = model.annotate(stream)

    if model.name == 'EQTransformer':
        picks, _ = model.classify(stream, P_threshold=paras['P_threshold'], S_threshold=paras['S_threshold'])
    else:
        picks = model.classify(stream, P_threshold=paras['P_threshold'], S_threshold=paras['S_threshold'])

    return annotations, picks




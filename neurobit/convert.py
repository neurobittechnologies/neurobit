# (c)-2019 Neurobit Technologies Amiya Patanaik 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import pyedflib
import click
import numpy as np
from time import time
from os import listdir, path
from pycfslib import create_stream_v2, qc_stream


def findMultiplier(unit):

    if unit == "nV":
        return 0.001
    elif unit == "uV":
        return 1.0
    elif unit == "mV":
        return 1000.0
    elif unit == "V":
        return 1000000.0
    else:
        return 1.0


def numInput(msg):
	number = input(msg)
	if number.isdigit():
		return int(number)
	else:
		print("Invalid entry!")
		numInput(msg)


def fileconvert(filepath, overwrite = False, suppress = False):

    if path.isfile(filepath[:-3] + 'cfs') and not overwrite:
        print("File is already converted, use --overwrite switch to overwrite")
        exit(0)

    head, tail = path.split(filepath)
    print('Reading: %s\n' %tail)
    sample_file = pyedflib.EdfReader(filepath)
    labels = sample_file.getSignalLabels()
    samples = sample_file.getNSamples()

    print("Here are the channel labels:")
    for l_idx, label in enumerate(labels):
        print('%d. %s' % (l_idx+1, label))

    C3 = numInput("Enter channel C3-A2 number: ") - 1
    C3_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
    C4 = numInput("Enter channel C4-A1 number: ") - 1
    C4_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
    EL = numInput("Enter channel EoGleft-A2 number: ") - 1
    EL_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
    ER = numInput("Enter channel EoGright-A1 number: ") - 1
    ER_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
    EM = numInput("Enter channel bipolar-EMG number: ") - 1
    EM_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1

    C3_label = labels[C3]
    C4_label = labels[C4]
    EL_label = labels[EL]
    ER_label = labels[ER]
    EM_label = labels[EM]

    if C3_Ref != -1:
        C3_Ref_label = labels[C3_Ref]
    if C4_Ref != -1:
        C4_Ref_label = labels[C4_Ref]
    if EL_Ref != -1:
        EL_Ref_label = labels[EL_Ref]
    if ER_Ref != -1:
        ER_Ref_label = labels[ER_Ref]
    if EM_Ref != -1:
        EM_Ref_label = labels[EM_Ref]

    start_time = time()
    if C3_Ref != -1:
        EEG_C3 = (np.asarray(sample_file.readSignal(C3)) - np.asarray(sample_file.readSignal(C3_Ref)))*findMultiplier(sample_file.getPhysicalDimension(C3))
    else:
        EEG_C3 = np.asarray(sample_file.readSignal(C3))*findMultiplier(sample_file.getPhysicalDimension(C3))

    if C4_Ref != -1:
        EEG_C4 = (np.asarray(sample_file.readSignal(C4)) - np.asarray(sample_file.readSignal(C4_Ref)))*findMultiplier(sample_file.getPhysicalDimension(C4))
    else:
        EEG_C4 = np.asarray(sample_file.readSignal(C4))*findMultiplier(sample_file.getPhysicalDimension(C4))

    if EL_Ref != -1:
        EOGL = (np.asarray(sample_file.readSignal(EL)) - np.asarray(sample_file.readSignal(EL_Ref)))*findMultiplier(sample_file.getPhysicalDimension(EL))
    else:
        EOGL = np.asarray(sample_file.readSignal(EL))*findMultiplier(sample_file.getPhysicalDimension(EL))

    if ER_Ref != -1:
        EOGR = (np.asarray(sample_file.readSignal(ER)) - np.asarray(sample_file.readSignal(ER_Ref)))*findMultiplier(sample_file.getPhysicalDimension(ER))
    else:
        EOGR = np.asarray(sample_file.readSignal(ER))*findMultiplier(sample_file.getPhysicalDimension(ER))

    if EM_Ref != -1:
        EMG = (np.asarray(sample_file.readSignal(EM)) - np.asarray(sample_file.readSignal(EM_Ref)))*findMultiplier(sample_file.getPhysicalDimension(EM))
    else:
        EMG = np.asarray(sample_file.readSignal(EM))*findMultiplier(sample_file.getPhysicalDimension(EM))

    fsampling = [sample_file.getSampleFrequency(C3), sample_file.getSampleFrequency(EL),
                sample_file.getSampleFrequency(EM)]
    
    
    elapsed_time = time() - start_time
    print("Time taken: %.3f" % elapsed_time)
    
    print("Converting to CFS and saving...")
    start_time = time()
    stream = create_stream_v2(EEG_C3, EEG_C4, EOGL, EOGR, EMG, fsampling, check_quality = False)
    qc_status, quality, message = qc_stream(stream)
    if qc_status and not suppress:
        print(message)
        print('This file won\'t be converted, try using alternate channels for this file.')
        print('You may also use the --suppress switch to ignore quality checks.')
    else:
        if qc_status:
            print(message)
            print('Scoring accuracy may suffer!')
        with open(head + '/' + tail[:-3] + 'cfs', 'wb') as f:
            f.write(stream)
    elapsed_time = time() - start_time
    print("Time taken: %.3f" % elapsed_time)


def batchconvert(directory, overwrite = False, suppress = False):
    
    files = [f for f in listdir(directory) if f.endswith('.edf')]
    
    # status of the files
    status = np.zeros(len(files), dtype=bool)
    
    # if overwrite switch is off (default), do not re-process the files
    if not overwrite:
        for idx, edf_file in enumerate(files):
            if path.isfile(directory + '/' + edf_file[:-3] + 'cfs'):
                status[idx] = True
    
    
    while np.any(~status):
        idx = np.argwhere(~status)
        to_process = [files[i] for i in range(len(files)) if ~status[i]]
    
        print('Reading: %s\n' %to_process[0])
        sample_file = pyedflib.EdfReader(directory + '/' + to_process[0])
        labels = sample_file.getSignalLabels()
        samples = sample_file.getNSamples()
    
        print("Here are the channel labels:")
        for l_idx, label in enumerate(labels):
            print('%d. %s' % (l_idx+1, label))
    
        C3 = numInput("Enter channel C3-A2 number: ") - 1
        C3_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
        C4 = numInput("Enter channel C4-A1 number: ") - 1
        C4_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
        EL = numInput("Enter channel EoGleft-A2 number: ") - 1
        EL_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
        ER = numInput("Enter channel EoGright-A1 number: ") - 1
        ER_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
        EM = numInput("Enter channel bipolar-EMG number: ") - 1
        EM_Ref = click.prompt('Reference channel number, press Enter to ignore', type = int, default=0, show_default=False) - 1
    
        C3_label = labels[C3]
        C4_label = labels[C4]
        EL_label = labels[EL]
        ER_label = labels[ER]
        EM_label = labels[EM]
    
        if C3_Ref != -1:
            C3_Ref_label = labels[C3_Ref]
        if C4_Ref != -1:
            C4_Ref_label = labels[C4_Ref]
        if EL_Ref != -1:
            EL_Ref_label = labels[EL_Ref]
        if ER_Ref != -1:
            ER_Ref_label = labels[ER_Ref]
        if EM_Ref != -1:
            EM_Ref_label = labels[EM_Ref]
    
        sample_file._close()
    
        for f_idx, edf_file in enumerate(to_process):
            print('Reading: %s\n' % edf_file)
            sample_file = pyedflib.EdfReader(directory + '/' + edf_file)
            labels = sample_file.getSignalLabels()
            samples = sample_file.getNSamples()
            try:
                C3 = labels.index(C3_label)
                C4 = labels.index(C4_label)
                EL = labels.index(EL_label)
                ER = labels.index(ER_label)
                EM = labels.index(EM_label)
    
                if C3_Ref != -1:
                    C3_Ref = labels.index(C3_Ref_label)
                if C4_Ref != -1:
                    C4_Ref = labels.index(C4_Ref_label)
                if EL_Ref != -1:
                    EL_Ref = labels.index(EL_Ref_label)
                if ER_Ref != -1:
                    ER_Ref = labels.index(ER_Ref_label)
                if EM_Ref != -1:
                    EM_Ref = labels.index(EM_Ref_label)
    
            except:
                print("Cannot find the right labels.\n")
                print("Ignoring this file for now, we will come back to later")
                continue
    
            print("Reading EDF file...")
    
            start_time = time()
            if C3_Ref != -1:
                EEG_C3 = (np.asarray(sample_file.readSignal(C3)) - np.asarray(sample_file.readSignal(C3_Ref)))*findMultiplier(sample_file.getPhysicalDimension(C3))
            else:
                EEG_C3 = np.asarray(sample_file.readSignal(C3))*findMultiplier(sample_file.getPhysicalDimension(C3))
    
            if C4_Ref != -1:
                EEG_C4 = (np.asarray(sample_file.readSignal(C4)) - np.asarray(sample_file.readSignal(C4_Ref)))*findMultiplier(sample_file.getPhysicalDimension(C4))
            else:
                EEG_C4 = np.asarray(sample_file.readSignal(C4))*findMultiplier(sample_file.getPhysicalDimension(C4))
    
            if EL_Ref != -1:
                EOGL = (np.asarray(sample_file.readSignal(EL)) - np.asarray(sample_file.readSignal(EL_Ref)))*findMultiplier(sample_file.getPhysicalDimension(EL))
            else:
                EOGL = np.asarray(sample_file.readSignal(EL))*findMultiplier(sample_file.getPhysicalDimension(EL))
    
            if ER_Ref != -1:
                EOGR = (np.asarray(sample_file.readSignal(ER)) - np.asarray(sample_file.readSignal(ER_Ref)))*findMultiplier(sample_file.getPhysicalDimension(ER))
            else:
                EOGR = np.asarray(sample_file.readSignal(ER))*findMultiplier(sample_file.getPhysicalDimension(ER))
    
            if EM_Ref != -1:
                EMG = (np.asarray(sample_file.readSignal(EM)) - np.asarray(sample_file.readSignal(EM_Ref)))*findMultiplier(sample_file.getPhysicalDimension(EM))
            else:
                EMG = np.asarray(sample_file.readSignal(EM))*findMultiplier(sample_file.getPhysicalDimension(EM))
    
            fsampling = [sample_file.getSampleFrequency(C3), sample_file.getSampleFrequency(EL),
                         sample_file.getSampleFrequency(EM)]
    
    
            elapsed_time = time() - start_time
            print("Time taken: %.3f" % elapsed_time)
    
            print("Converting to CFS and saving...")
            start_time = time()
            stream = create_stream_v2(EEG_C3, EEG_C4, EOGL, EOGR, EMG, fsampling, check_quality = False)
            qc_status, quality, message = qc_stream(stream)
            if qc_status and not suppress:
                print(message)
                print('This file won\'t be converted, try using alternate channels for this file.')
                print('You may also use the --suppress switch to ignore quality checks.')
            else:
                if qc_status:
                    print(message)
                    print('Scoring accuracy may suffer!')
                with open(directory + '/' + edf_file[:-3] + 'cfs', 'wb') as f:
                    f.write(stream)
            elapsed_time = time() - start_time
            print("Time taken: %.3f" % elapsed_time)
            status[idx[f_idx]] = True
    
    print('All files processed.')
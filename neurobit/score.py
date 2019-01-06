# (c)-2019 Neurobit Technologies Amiya Patanaik 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import click
import numpy as np
from requests import post
from time import time
from pathlib import Path
from os import listdir, path
from neurobit.export import to_wonambi, to_compu, to_mat, to_csv, to_edf

home = str(Path.home())
license = Path(home + '/neurobit.lic')

def filescore(cfsfile, overwrite = False):

    if path.isfile(cfsfile[:-3] + 'neo') and not overwrite:
        print("File is already scored, use --rescore switch to rescore")
        exit(0)

    print("Please select the format for the sleep scores\n")
    print("1. MATLAB (*.mat)")
    print("2. CSV (*_score.csv), sleep scores only")
    print("3. Compumedics XML (*.compumedics.xml)")
    print("4. EDF+ Annotations (*.hyp.edf), original EDF file must be present")
    print("5. Wonambi XML (*.wonambi.xml)")
    print("6. JSON dump (*.neo), always saved")

    choice = click.prompt('\nEnter your choice: ', type = int, default=1, show_default=False)

    with open(str(license), 'r') as f:
        config = json.load(f)

    head, tail = path.split(cfsfile)

    print('Scoring: %s,' %(tail))
    start_time = time()
    stream = {'file': open(cfsfile, 'rb')}
    response = post(config['url'] + '/score', files=stream, data={'email':config['email'], 'key':config['key']})
    elapsed_time = time() - start_time
    print("Time taken: %.3f" % elapsed_time)

    if response.status_code != 200:
        print("ERROR communicating with server")
        exit(0)

    data = response.json()
    if data['status'] == 0:
        print("Scoring failed\n")
        print(data['message'])
        exit(0)

    scores = np.array(data['message'])
    artefacts = np.array(data['artifact'])

    if choice == 1:
        to_mat(head + '/' + tail[:-4], scores, artefacts)
    elif choice == 2:
        to_csv(head + '/' + tail[:-4], scores, artefacts)
    elif choice == 3:
        to_compu(head + '/' + tail[:-4], scores, artefacts)
    elif choice == 4:
        to_edf(head + '/' + tail[:-4], scores, artefacts)
    elif choice == 5:
        to_wonambi(head + '/' + tail[:-4], scores, artefacts)
    
    with open(head + '/' + tail[:-4] + '.neo', "w") as data_file:
        json.dump(data, data_file)

    print("File scored")


def batchscore(directory, overwrite = False):

    files = [f for f in listdir(directory) if f.endswith('.cfs')]

    print("Please select the format for the sleep scores\n")
    print("1. MATLAB (*.mat)")
    print("2. CSV (*_score.csv), sleep scores only")
    print("3. Compumedics XML (*.compumedics.xml)")
    print("4. EDF+ Annotations (*.hyp.edf)")
    print("5. Wonambi XML (*.wonambi.xml)")
    print("6. JSON dump (*.neo), always saved")

    choice = click.prompt('\nEnter your choice: ', type = int, default=1, show_default=False)

    with open(str(license), 'r') as f:
        config = json.load(f)

    for cfsfile in files:
        print('Now scoring: %s,' %(cfsfile))
        
        if path.isfile(directory + '/' + cfsfile[:-3] + 'neo') and not overwrite:
            print("File is already scored, use --rescore switch to rescore")
            continue
        
        start_time = time()
        stream = {'file': open(directory + '/' + cfsfile, 'rb')}
        response = post(config['url'] + '/score', files=stream, data={'email':config['email'], 'key':config['key']})
        elapsed_time = time() - start_time
        print("Time taken: %.3f" % elapsed_time)

        if response.status_code != 200:
            print("ERROR communicating with server")
            continue

        data = response.json()
        if data['status'] == 0:
            print("Scoring failed\n")
            print(data['message'])
            continue

        scores = np.array(data['message'])
        artefacts = np.array(data['artifact'])

        if choice == 1:
            to_mat(directory + '/' + cfsfile[:-4], scores, artefacts)
        elif choice == 2:
            to_csv(directory + '/' + cfsfile[:-4], scores, artefacts)
        elif choice == 3:
            to_compu(directory + '/' + cfsfile[:-4], scores, artefacts)
        elif choice == 4:
            to_edf(directory + '/' + cfsfile[:-4], scores, artefacts)
        elif choice == 5:
            to_wonambi(directory + '/' + cfsfile[:-4], scores, artefacts)
        
        with open(directory + '/' + cfsfile[:-4] + '.neo', "w") as data_file:
            json.dump(data, data_file)

    print("All files scored")


    
        
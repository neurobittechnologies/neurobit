# (c)-2019 Neurobit Technologies Amiya Patanaik 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import xml.etree.cElementTree as ET
import datetime, pyedflib
import scipy.io as sio
import numpy as np

compumedics_XML = "<CMPStudyConfig>" \
                  "<EpochLength>30</EpochLength>" \
                  "<ScoredEventSettings>" \
                  "<ScoredEventSetting>" \
                  "    <Name>Artefact</Name>" \
                  "    <Colour>16628921</Colour>" \
                  "    <TextColour>4194304</TextColour>" \
                  "    <Input>C3</Input>" \
                  "</ScoredEventSetting>"  \
                  "<ScoredEventSetting>" \
                  "    <Name>Low Confidence</Name>" \
                  "    <Colour>11337727</Colour>" \
                  "    <TextColour>0</TextColour>" \
                  "    <Input>C3</Input>" \
                  "</ScoredEventSetting>"  \
                  "</ScoredEventSettings>"\
                  "</CMPStudyConfig>" 

wonambi_xml = '<annotations version="5">' \
              '</annotations>'

valid_stages = {
    0: 'Wake',
    1: 'NREM1',
    2: 'NREM2',
    3: 'NREM3',
    5: 'REM',   
}

edf_spec = {
    0: 'Sleep stage W',
    1: 'Sleep stage N1',
    2: 'Sleep stage N2',
    3: 'Sleep stage N3',
    5: 'Sleep stage R',   
}

def to_wonambi(file_path, scores, artefacts):
    root = ET.fromstring(wonambi_xml)
    epochs = scores.shape[0]

    rater = ET.SubElement(root,"rater")
    rater.attrib['created'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"); 
    rater.attrib['modified'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"); 
    rater.attrib['name'] = "NEO" 

    # Add Artefacts
    ET.SubElement(rater,"bookmarks")
    eventRoot = ET.SubElement(rater,"events")
    event_type_art = ET.SubElement(eventRoot, "event_type")
    event_type_art.attrib['type'] = "Artefact"

    art_epochs = np.argwhere(artefacts == 7)
    for epoch in art_epochs:
        event = ET.SubElement(event_type_art,"event")
        start = ET.SubElement(event,"event_start")
        start.text = str(epoch[0]*5)
        end = ET.SubElement(event,"event_end")
        end.text = str(epoch[0]*5 + 5)
        channel = ET.SubElement(event,"event_chan")
        channel.text = "EEG"
        quality = ET.SubElement(event,"event_qual")
        quality.text = "Good"

    # Sleep scores
    stageRoot = ET.SubElement(rater,"stages")

    for i in range(epochs):
        epoch = ET.SubElement(stageRoot,"epoch")
        start = ET.SubElement(epoch,"epoch_start")
        start.text =  str(i*30)
        stage = int(scores[i,0])
        end = ET.SubElement(epoch,"epoch_end")
        end.text = str(i*30 + 30)
        stage = ET.SubElement(epoch,"stage")
        stage.text = valid_stages[scores[i,0]]
        quality = ET.SubElement(epoch,"quality")
        if scores[i,1] < 2.0:
            quality.text = "Poor"
        else:
            quality.text = "Good"

    ET.SubElement(rater,"cycles")
    tree = ET.ElementTree(root)
    tree.write(file_path + '.wonambi.xml', encoding="UTF-8")

def to_compu(file_path, scores, artefacts):

    root = ET.fromstring(compumedics_XML)
    epochs = scores.shape[0]

    eventRoot = ET.SubElement(root,"ScoredEvents")
  
    # Add Low Confidence Events
    for i in range(epochs):
        if scores[i,1] > 2.0:
            continue

        event = ET.SubElement(eventRoot,"ScoredEvent")
        name = ET.SubElement(event,"Name")
        start = ET.SubElement(event,"Start")
        start.text = str(i*30)
        duration = ET.SubElement(event,"Duration")
        duration.text = "30"
        input_node = ET.SubElement(event,"Input")
        input_node.text = "C3"
        name.text = "Low Confidence"
 
    # Add artifacts
    art_epochs = np.argwhere(artefacts == 7)
    for epoch in art_epochs:
        event = ET.SubElement(eventRoot,"ScoredEvent")
        name = ET.SubElement(event,"Name")
        name.text = "Artefact"
        start = ET.SubElement(event,"Start")
        start.text = str(epoch[0]*5)
        duration = ET.SubElement(event,"Duration")
        duration.text = "5"
        input_node = ET.SubElement(event,"Input")
        input_node.text = "C3"

    # Add sleep scores
    eventRoot = ET.SubElement(root,"SleepStages")
    for i in range(epochs):
        stages = ET.SubElement(eventRoot,"SleepStage")
        stage = int(scores[i,0])
        stages.text = str(stage)

    tree = ET.ElementTree(root)
    tree.write(file_path + '.compumedics.xml', encoding="UTF-8")


def to_mat(file_path, scores, artefacts):
    sio.savemat(file_path + '.mat', {'sleepscore': scores, 'artefact': artefacts})


def to_csv(file_path, scores, artefacts):
    np.savetxt(file_path + '_scores.csv', scores, fmt='%d, %.2f', delimiter=',')

def to_edf(file_path, scores, artefacts):

    edf_file = pyedflib.EdfReader(file_path + '.edf')
    
    f = pyedflib.EdfWriter(file_path+'.hyp.edf', 0)
    f.setTechnician('neurobit.io')
    start = edf_file.getStartdatetime()
    f.setStartdatetime(start)
    epochs = scores.shape[0]
    # Add events
    f.writeAnnotation(0, -1, "Recording starts")

    for i in range(epochs):
        f.writeAnnotation(30 * i, 30, edf_spec[int(scores[i, 0])])
    
    # Add artifacts
    art_epochs = np.argwhere(artefacts == 7)
    for epoch in art_epochs:
        f.writeAnnotation(5 * epoch[0], 5, 'Artefact')
        
    f.writeAnnotation(epochs*30, -1, "Recording ends")
    
    f.close()
    del f


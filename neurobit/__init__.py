# (c)-2019 Neurobit Technologies Amiya Patanaik 
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import click
import json
import os
from neurobit.convert import batchconvert, fileconvert
from neurobit.score import filescore, batchscore
from requests import post
from pathlib import Path


home = str(Path.home())
license = Path(home + '/neurobit.lic')


@click.group()
def cli():
    pass


def check_license(config):
    
    response = post(config['url']+'/check',data={'email':config['email'], 'key':config['key']})

    if response.status_code != 200:
        print("Error communicating with server")
        return False
        
    data = response.json()
    if data['status'] == 0:
        print("License check failed")
        print(data['message'])
        return False

    print(data['message'])
    print('API Call limit (hourly): %d, Epoch limit (daily): %d\n' % (data['call_limit'], data['epoch_limit']))   
    return True


@cli.command()
def config():
    """ Configure license key """
    config = {}
    config['url'] = click.prompt('Server URL, press enter to accept default', default = 'https://z3score.com/api/v1', type = str)
    config['email'] = click.prompt('Enter Email Address')
    config['key'] = click.prompt('Enter Key')

    if check_license(config):
        with open(str(license), 'w') as f:
            json.dump(config, f)
            print('License setup complete')
            exit(0)
    else:
        print('License setup failed, try again later.')
        exit(0) 


@cli.command()
def check():
    """ Check license status """
    if not license.is_file():
        print('License not found, use neurobit config to setup license')
        print('If you do not have a license key, request one from contact@neurobit.io')
        exit(0)
    else:
        with open(str(license), 'r') as f:
            config = json.load(f)
        check_license(config)


@cli.command()
def remove():
    """ Remove existing license """
    if not license.is_file():
        print("License removed successfully")
    else:
        response = click.prompt('Are you sure? Type Y to confirm', type = str)
        if response.lower() == 'y':
            os.remove(str(license))
            print("License removed successfully")
        else:
            print('Cancelled')


@cli.command()
@click.option('--path', required=True, type=click.Path(exists=True), help='Full path to directory with EDF files or a single EDF file')
@click.option('--overwrite', is_flag=True, help='Overwrite already converted files, off by default')
@click.option('--suppress', is_flag=True, help='Suppress any quality check failures, off by default')
def convert(path, overwrite, suppress):
    """ Convert EDF file(s) located at /path to Neurobit's CFS format 
    If path is a directory, all files in that directory are converted in batch mode.
    If path is a single EDF file, that single file is converted.

    Z3Score uses CFS files to score and analyse data instead of original EDF files.
    CFS files are 18 to 100X smaller than original EDF files, making cloud based scoring much more efficient.
    CFS files do not include any user identifiable information by design, ensuring anonymity."""

    if os.path.isdir(path):
        batchconvert(path, overwrite, suppress)
    else:
        fileconvert(path, overwrite, suppress)


@cli.command()
@click.option('--path', required=True, type=click.Path(exists=True), help='Full path to directory with CFS files or a single CFS file')
@click.option('--rescore', is_flag=True, help='Rescore already scored files, off by default')
def score(path, rescore):
    """ Score CFS file(s) located at /path using the Z3Score V2 Auto Scoring System 
    If path is a directory, all CFS files in that directory are scored.
    If path is a single CFS file, that single file is scored. 
    
    Use the convert command to convert EDF files to CFS if you have not yet done so.
    You will need a license key to be able to score data.
    If you do not have a license key, request one from contact@neurobit.io 
    
    Z3Score uses CFS files to score and analyse data instead of original EDF files.
    CFS files are 18 to 100X smaller than original EDF files, making cloud based scoring much more efficient.
    CFS files do not include any user identifiable information by design, ensuring anonymity."""
    
    if not license.is_file():
        print('License not found, use neurobit config to setup license')
        print('If you do not have a license key, request one from contact@neurobit.io')
        exit(0)
    else:
        with open(str(license), 'r') as f:
            config = json.load(f)
        
        if not check_license(config):
            exit(0)
    
    # License check successful 
    if os.path.isdir(path):
        batchscore(path, rescore)
    else:
        filescore(path, rescore)
    



if __name__ == '__main__':
    cli()
    

        
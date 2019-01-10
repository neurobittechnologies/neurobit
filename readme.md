# Neurobit Utilities

Neurobit Utilities is a collection of command-line tools to score and analyze sleep data using the Z3Score Framework. 
- To know more about the Z3Score framework: https://z3score.com 
- Read our validation paper: https://academic.oup.com/sleep/article/41/5/zsy041/4954046
- Know more about our company: https://www.neurobit.io

> **Major Update:** the current version of Z3Score is built ground up from scratch and trained on nearly 60,000+ hours of sleep data collected from 4000+ subjects. We have seen 30 to 40% lower error rates compared to our published results. To test our new scorer, request an access key at: contact@neurobit.io 

## Quick Start Guide Video (10 minutes)

[![Neurobit Quick Start Guide](https://s3.amazonaws.com/www.neurobit.io/img/neurobit-utilities.jpg)](https://www.youtube.com/watch?v=j5nAviEP4WM)

## Currently Supported

- **Fully AASM complaint automatic sleep scoring**
- Artefact Detection (in beta)
- Arousal Detection (comming soon)
- Respiratory Events (comming soon)
- Use your favourite scoring software 

### Recommended free viewing/scoring softwares:
- **Wonambi** - Cross platform Python based GUI, free and open source: https://wonambi-python.github.io/ 
- **Polyman** - Windows only, free but closed source:  https://sites.google.com/view/diegoalvarezestevez/projects/polyman
- **EDFbrowser** - Cross platform, free and open source EDF viewer (not for scoring):  https://www.teuniz.net/edfbrowser/
- **Z3Score-FASST** - Matlab based GUI based off of FASST, not recommended due to poor support: https://github.com/neurobittechnologies/FASST-Z3Score

## Getting Started

You will need to install python 3.5 or higher. To test if you have python on your system, go to the command prompt and type:

    python --version

We strongly recommend python 3.6. If you do not have python on your system, download and install it from: https://www.anaconda.com/download/ 

### Install Neurobit

Once you have installed python on your system, install neurobit using pip. Go to your command line and type:

    pip install neurobit -U

### See all available commands

To check if neurobit is installed properly, type:

    neurobit

You will see all the available commands:

    Usage: neurobit [OPTIONS] COMMAND [ARGS]...
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      check    Check license status
      config   Configure license key
      convert  Convert EDF file(s) located at /path to...
      remove   Remove existing license
      score    Score CFS file(s) located at /path using the...

### Configure your access key
To configure your access key, issue the command:

    neurobit config

Enter a valid access key. If you do not have one, you can request one from contact@neurobit.io

### Check your license status
To check your license status, issue this command:

    neurobit check

 
## Sleep score and analyse your data

You need your data to be in EDF format. If you have multiple files, put all the files in one directory. Scoring is a two step process:
 - **Step 1:** Convert your EDF files to Neurobit's CFS (Copressed Feature Set) format. CFS files can be 18 to 100X smaller than corresponding EDF files. Neurobit uses these small files to do cloud based analysis. 
 - **Step 2:** Score your CFS files using Neurobit's cloud infrastructure.

### Convert EDF files to CFS
Use the neurobit convert command. You can use the --help key to show usage instructions.

    neurobit convert --help

  This will show you the usage instructions

    Convert EDF file(s) located at /path to Neurobit's CFS format  If path is
      a directory, all files in that directory are converted in batch mode. If
      path is a single EDF file, that single file is converted.
    
      Z3Score uses CFS files to score and analyse data instead of original EDF
      files. CFS files are 18 to 100X smaller than original EDF files, making
      cloud based scoring much more efficient. CFS files do not include any user
      identifiable information by design, ensuring anonymity.
    
    Options:
      --path PATH  Full path to directory with EDF files or a single EDF file
                   [required]
      --overwrite  Overwrite already converted files, off by default
      --suppress   Suppress any quality check failures, off by default
      --help       Show this message and exit.

### Score your CFS files
Use the neurobit score command. You can use the --help key to show usage instructions.

    neurobit score --help

This will again show you usage instructions

      Score CFS file(s) located at /path using the Z3Score V2 Auto Scoring
      System  If path is a directory, all CFS files in that directory are
      scored. If path is a single CFS file, that single file is scored.
    
      Use the convert command to convert EDF files to CFS if you have not yet
      done so. You will need a license key to be able to score data. If you do
      not have a license key, request one from contact@neurobit.io
    
      Z3Score uses CFS files to score and analyse data instead of original EDF
      files. CFS files are 18 to 100X smaller than original EDF files, making
      cloud based scoring much more efficient. CFS files do not include any user
      identifiable information by design, ensuring anonymity.
    
    Options:
      --path PATH  Full path to directory with CFS files or a single CFS file
                   [required]
      --rescore    Rescore already scored files, off by default
      --help       Show this message and exit.

For scoring, the following formats are currently supported:

1. MATLAB (*.mat)
2. CSV (*_score.csv), sleep scores only
3. Compumedics XML (*.compumedics.xml)
4. EDF+ Annotations (*.hyp.edf)
5. Wonambi XML (*.wonambi.xml)
6. JSON dump (*.neo), always saved

If you need your scores in a format which is not supported, contact us at contact@neurobit.io


### Convert your scores from one format to another

If you have already scores your data in one format and now want the scores in another format simply use the score command.
Neurobit automatically detects that the files are already scored and reads the scores from local disk (in native .neo format) and converts into your format of choice.

    neurobit score --path /path/to/already/scored/direcotory/or/file

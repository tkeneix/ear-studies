# ear-studies

## Overview
Applications that reduce the learning burden by listening to your ears.  

## Software requirements
* python3
* pydup
* EasyID3
* [Cloud Text-to-Speech ](https://cloud.google.com/text-to-speech?hl=ja)


## Preparation

Implement `Setting up authentication` in Google's [Text-to-Speech Client Libraries](https://cloud.google.com/text-to-speech/docs/reference/libraries?hl=JA) , Get a `JSON file containing the service account key`.
Specify this file as an argument of the program.


## Install packages

```
pip install -r requirements.txt
```

## Execution example
```
python boost_vocabulary.py -f csv/sample.csv -k <service_account_key>.json
```


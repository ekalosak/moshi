# Notes
Developer notes.

## pytts3
- Problem: Getting a segfault when initializing the speech engine: `SIGSEGV (Address boundary error)`.
- Diagnosis: `pyobjc` bug for `9.1.x`.
- Solution: `pip install pyobjc==9.0.1`
- Source: https://github.com/nateshmbhat/pyttsx3/issues/274#issuecomment-1544904124

## Spanish recognizer

### Find a model and set it up
- Docs point to [this page](https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst).
  - Crawling lands on
  [this download page](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Mexican%20Spanish/)
  for Mexican Spanish.
- Downloaded the `.zip`
- `python -c "import speech_recognition as sr, os.path as p; print(p.dirname(sr.__file__))"`
- `set -x SR_LIB` to the directory from prev. command.
```
mkdir es-MX && cd es-MX
mv ~/Downloads/CIEMPIESS_Spanish_Models_581h.zip .
unzip CIEMPIESS_Spanish_Models_581h.zip
mkdir $SR_LIB/pocketsphinx-data/es-MX
mv CIEMPIESS_Spanish_Models_581h/Models/* $SR_LIB/pocketsphinx-data/es-MX
```

### Debugging

#### Problem 1
The package has `.dic` rather than `.dict` files so go in and change those extensions...

[Stackoverflow](https://stackoverflow.com/questions/39907245/how-can-i-configure-spanish-in-pocketsphinx-with-python)
has an answer:

```py
from pocketsphinx.pocketsphinx import Decoder

config = Decoder.default_config()
# TODO
config.set_string('-hmm', 'cmusphinx-es-5.2/model_parameters/voxforge_es_sphinx.cd_ptm_4000')
config.set_string('-lm', '581HCDCONT10000SPA.lm.bin')
config.set_string('-dict', '581HCDCONT10000SPA.dic')
decoder = Decoder(config)
```

# romlogic
Generating ROM content from equations


usage: romlogic.py [-h] [-d] [-l] [-e] [-o {bin,hex}] InFileName

Generates ROM content from logical equations.

positional arguments:
  InFileName            input file name

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           show detailed output
  -l, --list            generate list file
  -e, --equations       generate equations file
  -o {bin,hex}, --output {bin,hex}
                        set output file type

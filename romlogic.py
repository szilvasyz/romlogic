import argparse
import configparser
import os
#import sys

import intelhex

parser = argparse.ArgumentParser(
    description='Generates ROM content from logical equations.')

config = configparser.ConfigParser()

parser.add_argument("InFileName", help="input file name")
parser.add_argument("-d", "--debug", help="show detailed output", action='store_true')
parser.add_argument("-l", "--list", help="generate list file", action='store_true')
parser.add_argument("-e", "--equations", help="generate equations file", action='store_true')
parser.add_argument("-o", "--output", help="set output file type", choices=['bin', 'hex'], default='bin')

args = parser.parse_args()
config.read(args.InFileName)
outputfilename = os.path.splitext(args.InFileName)[0] + "." + args.output

if args.debug:
    print("Input file: {}".format(args.InFileName))
    print("Output file: {}".format(outputfilename))

if not (('inputs' in config) and
    ('outputs' in config) and
    ('equations' in config)):
    print("The [inputs], [outputs] and [equations] sessions must all be included in input file.")
    exit(1)

symdefoutput = config.get('defaults', "outputs", fallback=1)
symdefequ = config.get('defaults', "equations", fallback=0)

evalinput = ""
evalequation = ""
evalclrequ = ""
evaloutput = ""
maxinput = -1
maxoutput = -1

syminphdr = []
symequhdr = []
symouthdr = []

for symitem in config.items('inputs'):
    syminphdr.append(symitem[0])
    evalinput += "{} = a{}\n".format(symitem[0], symitem[1])
    maxinput = max(maxinput, int(symitem[1]))

for symitem in config.items('equations'):
    symequhdr.append(symitem[0])
    evalequation += "{} = {}\n".format(symitem[0], symitem[1])
    evalclrequ += "{} = {}\n".format(symitem[0], symdefequ)

for symitem in config.items('outputs'):
    symouthdr.append(symitem[0])
    evaloutput += "d{} = ({}) & 1\n".format(symitem[1], symitem[0])
    maxoutput = max(maxoutput, int(symitem[1]))

if args.debug:
    print(evalinput)
    print(evalclrequ)
    print(evalequation)
    print(evaloutput)

symih = intelhex.IntelHex()
symarray = []
syminparr = {}
symoutarr = {}
symevalarr = {}

for symaddr in range(1 << (maxinput+1)):
    for symiter in range(maxinput + 1):
        exec("a{} = (symaddr >> symiter) & 1".format(symiter))

    for symiter in range(maxoutput + 1):
        exec("d{} = {}".format(symiter, symdefoutput))

    exec(evalinput)
    exec(evalclrequ)
    exec(evalequation)
    exec(evaloutput)

    symdata = 0
    for symiter in range(maxoutput + 1):
        symdata |= eval("d{}".format(symiter)) << symiter
    symarray.append(symdata)
    symih[symaddr] = symdata

    symeval = []
    for symitem in config.items('equations'):
        symeval.append(eval(symitem[0]))
    symevalarr[symaddr] = symeval

    syminp = []
    for symitem in config.items('inputs'):
        syminp.append(eval(symitem[0]))
    syminparr[symaddr] = syminp

    symout = []
    for symitem in config.items('outputs'):
        symout.append(eval(symitem[0]))
    symoutarr[symaddr] = symout

    if args.debug:
        print("{:0{wa}b}: {:0{wd}b}".format(symaddr, symdata, wa=maxinput+1, wd=maxoutput+1))
        print(locals())

if args.debug:
    print(symarray)

if args.output == 'bin':
    symih.tobinfile(outputfilename)
    print("Binary output written.")
elif args.output == 'hex':
    symih.write_hex_file(outputfilename)
    print("Intel hex output written.")
else:
    print("Invalid format specified, no output written.")

if args.list:
    listfilename = os.path.splitext(args.InFileName)[0] + ".lst"
    lst = ""
    for item in range(1 << (maxinput+1)):
        lst += "{:0{wa}b}: {:0{wd}b}\n".format(symaddr, symdata, wa=maxinput + 1, wd=maxoutput + 1)
    os.write(os.open(listfilename, os.O_CREAT | os.O_TRUNC | os.O_RDWR), bytes(lst, "UTF8"))
    print("List file written.")

if args.equations:
    equsfilename = os.path.splitext(args.InFileName)[0] + ".equ"
    lst = "{} : {} : {}\n".format(syminphdr, symequhdr, symouthdr)
    for symitem in range(1 << (maxinput+1)):
        lst += "{} : {} : {}\n".format(syminparr[symitem], symevalarr[symitem], symoutarr[symitem])
    os.write(os.open(equsfilename, os.O_CREAT | os.O_TRUNC | os.O_RDWR), bytes(lst, "UTF8"))
    print("Equations file written.")



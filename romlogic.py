import argparse
import configparser
from typing import Tuple

config = configparser.ConfigParser()

# Initialize argument parser
parser = argparse.ArgumentParser()

# Adding positional argument
parser.add_argument("InFileName", help="Input file name")

# Adding optional argument
parser.add_argument("-o", "--Output", help="Show Output")

# Read arguments from command line
args = parser.parse_args()

if args.Output:
    print("Displaying Output as: % s" % args.Output)

print("Processing file {}".format(args.InFileName))
config.read(args.InFileName)
print(config.sections())


evalinput = ""
evalequation = ""
evaloutput = ""
maxinput = -1
maxoutput = -1

for item in config.items('inputs'):
    evalinput += "{} = a{}\n".format(item[0], item[1])
    maxinput = max(maxinput, int(item[1]))

for item in config.items('equations'):
    evalequation += "{} = {}\n".format(item[0], item[1])

for item in config.items('outputs'):
    evaloutput += "d{} = ({}) & 1\n".format(item[1], item[0])
    maxoutput = max(maxoutput, int(item[1]))

print(evalinput)
print(evalequation)
print(evaloutput)

for symaddr in range(1 << (maxinput+1)):
    for i in range(maxinput + 1):
        exec("a{} = (symaddr >> i) & 1".format(i))

    for i in range(maxoutput + 1):
        exec("d{} = 1".format(i))

    exec(evalinput)
    exec(evalequation)
    exec(evaloutput)

    symdata = 0
    for i in range(maxoutput + 1):
        symdata |= eval("d{}".format(i)) << i

    print("{:0{wa}b}: {:0{wd}b}".format(symaddr, symdata, wa=maxinput+1, wd=maxoutput+1))
#    print(locals())



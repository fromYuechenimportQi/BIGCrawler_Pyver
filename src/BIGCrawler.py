
from urllib import request
from src import gsa, gwh
import argparse
import sys


parser = argparse.ArgumentParser()
# 2. 添加命令行参数
#parser.add_argument('--sparse', action='store_true', default=False, help='GAT with sparse version or not.')
#parser.add_argument('--', type=int, default=72, help='Random seed.')
#parser.add_argument('-db','--database',required=True,type=str,choices=["gsa","gwh"],help="Choose a database that you want to crawl.")
group = parser.add_mutually_exclusive_group()
group.add_argument('-gsa', '--gsa', action="store_true")
group.add_argument('-gwh', '--gwh', action="store_true")
parser.add_argument('-m', '--mode', type=str, required=True, choices=["auto", "manual"], default="auto",
                    help="Choose the mode during crawling.\nIf \'manual\' is selected, \'-acc\' or \'-infile\' is required")
parser.add_argument('-acc', '--accession', nargs='*',
                    help='A series of blank-seperated CRA accession numbers')
parser.add_argument('-infile', '--inputfile', type=str,
                    help='A file containing enter-seperated CRA accession numbers')
# 3. 从命令行中结构化解析参数
args = parser.parse_args()
# print(args.sparse)
# print(args.seed)
# print(args.accession)

flag = 1
if args.gsa or args.gwh:
    if args.mode == "auto":
        if args.accession or args.inputfile:
            print("\nERROR: In auto mode, \'-acc\' or \'-infile\' is not required!\n")
            flag = 0
    else:
        if not (args.accession or args.inputfile) or (args.accession and args.inputfile):
            print(
                "\nERROR: ONE of \'-acc\' or \'-infile\' is required, You choosed none or both!\n")
            flag = 0
else:
    print("\nERROR: \'-gsa\' or \'-gwh\' is required!\n")
    flag = 0
if not flag:
    sys.exit(-1)


if args.gsa:
    main = gsa.main
    main(mode=args.mode, acc=args.accession, filename=args.inputfile)
elif args.gwh:
    main = gwh.main
    main()

#!/usr/bin/python

#
# Email checker for gmail accounts
# Author czz78
# Thanx to x0rz for infos on his blog https://blog.0day.rocks/abusing-gmail-to-get-previously-unlisted-e-mail-addresses-41544b62b2
#

import sys
import argparse
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import requests


#
#  Check if email xxx@gmail.com exists
#  returns the email that has been checked if true, nothing if false
#
def check(email, verbose = 'no'):
    url = "https://mail.google.com/mail/gxlu?email={0}".format(email)
    r = requests.get(url)

    try:
        if(r.headers['set-cookie'] != ''):
            if(verbose == 'yes'):
                #print ("email %s is valid" % (email))
                print r.headers
            return email
    except:
        if(verbose == 'yes'):
            print r.headers

        return


#
# Write to file
#
def write_to_file(hnd, data):
    for d in data:
        if d is not None:
            hnd.write(str(d + "\n"))


#
# Write to standard out ( default )
#
def write_to_stdout(data, tag = ''):
    for d in data:
        if d is not None:
            print "%s %s" % (d, tag)






########################### MAIN ##########################################

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
parser.add_argument("-s", "--single", help="single email. Only one address")
parser.add_argument("-f", "--filename", help="Name of file with a list of emails")
parser.add_argument("-t", "--threads", help="number of threads, default 4")
parser.add_argument("-o", "--out", help="Name of output file")
parser.add_argument("-i", "--invalid", help="if used with --out will give a file invalid.outputfilename else will print in std out", action="store_true")
args = parser.parse_args()


verbose = "no"
if args.verbose:
    verbose = "yes"

threads = 20
if args.threads:
    threads = int(args.threads)

if ((args.single and args.filename) or (not args.single and not args.filename)):
     parser.print_help()
     parser.exit(1)

# make the Pool of workers
pool = ThreadPool(threads) 

# if single address
if args.single:
    results = check("%s" % (args.single), verbose)
    if results is None:
        print "%s address not valid" % (args.single)
    else:
        print "%s address valid" % (args.single)


if args.out:
    out = open(args.out,"w")

if args.invalid:
    if args.out:
        invalid = open("invalid." + args.out,"w")

if args.filename:

    # initialize emails var
    emails=[]

    with open(args.filename) as fp:
        flag = 0
        for i,line in enumerate(fp, start=1):

            if args.out:
                sys.stdout.write('.')
                sys.stdout.flush()
            else:
                if i == 1:
                    print "waiting for results ....\n"

            line = line.replace("\n","").replace("\r","")
            emails.append(line)
            if (i%threads == 0):
                results= pool.map(partial(check, verbose=verbose), emails)

                if args.out:
                    write_to_file(out,results)
                else:
                    write_to_stdout(results)

                if args.invalid:
                    if args.out:
                        write_to_file(invalid,set(emails)-set(results))
                    else:
                        write_to_stdout(set(emails)-set(results), "NOT VALID")


                emails = []
                flag = 0
            else:
                flag = 1

        if flag == 1:
            results= pool.map(partial(check, verbose=verbose), emails)
            if args.out:
                write_to_file(out,results)
            else:
                write_to_stdout(results)


            if args.invalid:
                if args.out:
                    write_to_file(invalid,set(emails)-set(results))
                else:
                    write_to_stdout(set(emails)-set(results), "NOT VALID")


    if not args.out:
        print ""
    print "Done\n"


if args.out:
    out.close()

pool.close()
pool.join()

#End
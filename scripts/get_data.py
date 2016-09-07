from __future__ import print_function

import httplib
import urllib
#import http.client in Python 3
#import urllib.parse in Python 3
import time
from xml.dom.minidom import parseString

from astropy.table import Table

host = "gea.esac.esa.int"
port = 80
pathinfo = "/tap-server/tap/async"


def acall(verbose=False):
    """ASYNCHRONOUS REQUEST"""
    
    # Query
    params = urllib.urlencode({\
        "REQUEST": "doQuery", \
        "LANG":    "ADQL", \
        "FORMAT":  "votable", \
        "PHASE":  "RUN", \
        "QUERY":   """SELECT * FROM public.tgas_source"""
        })

    headers = {\
        "Content-type": "application/x-www-form-urlencoded", \
        "Accept":       "text/plain" \
        }

    connection = httplib.HTTPConnection(host, port)
    connection.request("POST",pathinfo,params,headers)

    # Status
    response = connection.getresponse()
    if verbose: print("Status: " +str(response.status), "Reason: " + str(response.reason))

    # Server job location (URL)
    location = response.getheader("location")
    if verbose: print("Location: " + location)

    #Jobid
    jobid = location[location.rfind('/')+1:]
    if verbose: print("Job id: " + jobid)

    connection.close()

    #-------------------------------------
    #Check job status, wait until finished

    while True:
        connection = httplib.HTTPConnection(host, port)
        connection.request("GET",pathinfo+"/"+jobid)
        response = connection.getresponse()
        data = response.read()
        #XML response: parse it to obtain the current status
        dom = parseString(data)
        phaseElement = dom.getElementsByTagName('uws:phase')[0]
        phaseValueElement = phaseElement.firstChild
        phase = phaseValueElement.toxml()
        if verbose: print("Status: " + phase)
        #Check finished
        if phase == 'COMPLETED': break
        #wait and repeat
        time.sleep(0.2)

    #print "Data:"
    #print data

    connection.close()

    #-------------------------------------
    #Get results
    connection = httplib.HTTPConnection(host, port)
    connection.request("GET",pathinfo+"/"+jobid+"/results/result")
    response = connection.getresponse()
    data = response.read()
    outputFileName = "../data/tgas.vot"
    outputFile = open(outputFileName, "w")
    outputFile.write(data)
    outputFile.close()
    connection.close()
    if verbose: print("Data saved in: " + outputFileName)

def table_info():
    """"""
    t = Table.read("../data/example3_votable_output.vot", format='votable')
    t.info()
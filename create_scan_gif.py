#!/usr/bin/env python
###################################################
#  phase_scan_gif.py	                          #
#                                                 #
#  Produces a gif of the phase scan from the      #
#  output of iQiScan hcalraw plugin.              #
###################################################
import sys
import optparse
import ROOT
from ROOT import TFile, TCanvas, TH1D, gROOT, gStyle, gPad
import os
from datetime import datetime
from subprocess import call
# Number of fibers
FIBER_CNT = 24
# Number of channels per fiber
FIBCH_CNT = 8

# Crate (FNAL teststand: default 41)
CRATE = 41

# Slot number (FNAL teststand: default 1)
SLOT = 1

# Valid Gsel settings
GSEL_CODES = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
              0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]

FIBER = 4 
FIBCH = 4 


#############################################
#  Quiet                                    #
#  Usage: Quiets info, warnings, or errors  #
#                                           #
#  Ex: TCanvas.c1.SaveAs("myplot.png")      #
#      Quiet(c1.SaveAs)("myplot.png")       #
#############################################
def Quiet(func, level = ROOT.kInfo + 1):
    def qfunc(*args,**kwargs):
        oldlevel = ROOT.gErrorIgnoreLevel
        ROOT.gErrorIgnoreLevel = level
        try:
            return func(*args,**kwargs)
        finally:
            ROOT.gErrorIgnoreLevel = oldlevel
    return qfunc

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inF', dest='inF', help='input file', default=None, type='string')
parser.add_option('-o', '--outF', dest='outF', help='output file name', default="", type='string')
parser.add_option('--scan', dest='scan', help='scan type (gsel, phase, or iqi)', default="iqi", type='string')
parser.add_option('-s', '--slot', dest='slot', type = 'int', help = "slot number")
parser.add_option('-f', '--fiber', dest='fiber', type = 'int', help = "fiber number")
parser.add_option('-c', '--channel', dest='fibch', type = 'int', help = "fiber channel")
parser.add_option('-w', '--warn', dest='warn', help='warn on errors (0 or 1)', default=0, type='int')
(opt,args) = parser.parse_args()

f = TFile.Open(opt.inF, 'r')
try:
    if f.IsZombie():
        print "File %s is a zombie" % opt.inF
        sys.exit()
except: # Couldn't open file, exit
    sys.exit()

gROOT.SetBatch(True)  # True: Don't display canvas
c = TCanvas("c","c",1700,1200)



try:
    if opt.scan == "gsel":
	    FRAMES = 13
    elif opt.scan == "phase":
	    FRAMES = 100
    elif opt.scan == "iqi":
        FRAMES = 10000
        #FRAMES = range(50) + range(64, 114) 
    else:
	    print "Unrecognized --scan option  (hint: gsel or phase)"
	    sys.exit()

except:
    sys.exit()

print "Loading histograms from file %s.." % opt.inF,
histos = []
for i in xrange(FRAMES):
    htemp = None
    #htemp = f.Get("ADC_vs_TS_ErrF0_%s_%d_FED_1776_Crate_41_Slot_1_Fib_4_Ch_4_2D" % (opt.scan, i if opt.scan != "gsel" else GSEL_CODES[i]))
    if opt.scan == "iqi":
        hname = "ADC_vs_TS_Evt_%d_Slot_%d_Fib_%d_Ch_%d" % (i+1, opt.slot, opt.fiber, opt.fibch)
    else:
        hname = "ADC_vs_TS_%s_%s_Slot_%d_Fib_%d_Ch_%d" % (opt.scan, i if opt.scan == "phase" else GSEL_CODES[i], opt.slot, opt.fiber, opt.fibch)
    htemp = f.Get(hname)
    try:
        htemp.SetDirectory(0)
        htemp.GetYaxis().SetTitleOffset(1.1)
        htemp.GetZaxis().SetTitleOffset(1.0)
        htemp.GetZaxis().SetRangeUser(0., 100.)
        htemp.GetZaxis().SetTitle("")
        histos.append(htemp)
    except:
        print "Unable to find hist:", hname
        continue
if len(histos) == 0:
    print "Can't find %s scan data in %s" % (opt.scan, opt.inF)
    sys.exit()


#maxADC = -1
#for bin in range(histos[0].GetN
print "done!"
print "Drawing frames...",
sys.stdout.flush()
maxADC = 150
#maxADC = 20000

tempdir = "_tmpGif_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
os.mkdir(tempdir)
tempfiles = ""
for i, h in enumerate(histos):
    h.SetAxisRange(0., maxADC, "Y")
    h.Draw("COLZ")
    gPad.Update()
    
    st = h.FindObject("stats")	# TPaveStats object
    st.SetX1NDC(0.7)
    st.SetX2NDC(0.9)
    st.SetY2NDC(0.9)

#    if i < 10:
#	run = "00" + str(i)
#    elif i < 100:
#	run = "0" + str(i)
#    else:
#	run = str(i)
    #c.SaveAs("tmp/tmp_phase%s.png" % run)
    tempfiles += "tmp_%s.png\n" % i
    Quiet(c.SaveAs)(tempdir + "/tmp_%s.png" % i)
print "done!"

path,outf = os.path.split(opt.outF)
if opt.outF != "" and (path == "" or os.path.exists(path)):
    name = os.path.abspath(path) + "/" + outf
    if os.path.splitext(outf)[1] != ".gif":
	    name += ".gif"

else:
    name = os.getcwd() + "/" + os.path.splitext(os.path.basename(opt.inF))[0] + "-%s_scan.gif" % opt.scan
    #name = os.path.splitext(os.path.abspath(os.path.split(opt.inF)[0]) + "/" + os.path.basename(opt.inF))[0] + "-%s_scan.gif" % opt.scan

print "Creating gif %s..." % name, 
sys.stdout.flush()

if opt.scan == "phase":
    command = "convert -loop 0 -delay 20 @file.tx -delay 150 tmp_%d.png %s" % (FRAMES-1, name)
    os.system("cd %s" % tempdir + ";echo '%s' > file.tx" % tempfiles + ";" + command + ";cd ..")
elif opt.scan == "gsel":
    command = "convert -loop 0 -delay 50 @file.tx -delay 150 tmp_%d.png %s" % (FRAMES-1, name)
    os.system("cd %s" % tempdir + ";echo '%s' > file.tx" % tempfiles + ";" + command + ";cd ..")
elif opt.scan == "iqi":
    command = "convert -loop 0 -delay 10 @file.tx -delay 150 tmp_%d.png %s" % (FRAMES-1, name)
    os.system("cd %s" % tempdir + ";echo '%s' > file.tx" % tempfiles + ";" + command + ";cd ..")
print "done!"
os.system("rm -rf %s" % tempdir)

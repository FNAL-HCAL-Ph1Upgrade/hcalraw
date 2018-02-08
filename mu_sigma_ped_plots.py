#!/usr/bin/env python
###################################################
#  mu_sigma_ped_plots.py                          #
#                                                 #
#  Runs on an output file from pulseRun plugin    #
#  to produce a histograms of mean/stddev ADC and #
#  charge from all channels.			  #
###################################################
import sys
import optparse
import ROOT
from ROOT import TFile, TCanvas, TH1D, gROOT


# Sum over these time slices
TS_MASK = [3, 4, 5, 6]
#TS_MASK = [1, 2, 3, 4, 5, 6, 7]

# Number of fibers
FIBER_CNT = 24
# Number of channels per fiber
FIBCH_CNT = 8

# Crate (FNAL teststand: default 41)
CRATE = 41

# Slot number (FNAL teststand: default 1)
SLOT = 1

#def calcMeanRMSfor 

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inF', dest='inF', help='input file', default=None, type='string')
parser.add_option('-e', '--fedId', dest='fedId', help='fed Id', default=1776, type='int')
parser.add_option('-w', '--warn', dest='warn', help='warn on errors (0 or 1)', default=0, type='int')
parser.add_option('-f', '--fiberMask', dest='fiberMask', help='fiber to inspect', default=-1, type='int')
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

adc_ts_h = {}
charge_ts_h = {}
for fib in xrange(0, FIBER_CNT):
    if opt.fiberMask != -1:
	if fib != opt.fiberMask: continue
    adc_ts_h_perfiber = {}
    charge_ts_h_perfiber = {}
    for fibch in xrange(0, FIBCH_CNT):
	htemp = None
	htemp = f.Get("NoTS0_ADC_vs_TS_ErrF0_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" %(opt.fedId, CRATE, SLOT, fib, fibch))
	try:	
	    htemp.SetDirectory(0)
	    #htemp.SetBinContent(1, 0)
	    #htemp.SetBinEntries(1, 0)
	    adc_ts_h_perfiber.update( {fibch:htemp} )
	except:
	    if opt.warn: print "ADC vs TS in Fib %d Ch %d has no good data" % (fib, fibch)
	
	htemp = None
	htemp = f.Get("NoTS0_Charge_vs_TS_ErrF0_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" %(opt.fedId, CRATE, SLOT, fib, fibch))
	try:
	    htemp.SetDirectory(0)
	    #htemp.SetBinContent(1, 0)
	    #htemp.SetBinEntries(1, 0)
	    charge_ts_h_perfiber.update( {fibch:htemp} )
	except:
	    if opt.warn: print "Charge vs TS in Fib %d Ch %d has no good data" % (fib, fibch)
	

    if len(adc_ts_h_perfiber) > 0:
	adc_ts_h.update( {fib:adc_ts_h_perfiber} )
    if len(charge_ts_h_perfiber) > 0:
	charge_ts_h.update( {fib:charge_ts_h_perfiber} )


# Done with TFile
f.Close()

# TProfile h
# h.GetMean(2) Y axis mean
# h.GetRMS(2)  Y axis rms


means = []
sigmas = []
charges = []

for fib in xrange(0, FIBER_CNT):
    for fibch in xrange(0, FIBCH_CNT):
	try:
	    mean = adc_ts_h[fib][fibch].GetMean(2)
	    #if mean > 10:
	    #	print "Fiber %d Ch %d has mean %f" % (fib, fibch, mean)
	    rms = adc_ts_h[fib][fibch].GetRMS(2)
	    totQ = 0.0
	    for i in TS_MASK:
	    	totQ += charge_ts_h[fib][fibch].GetBinContent(i+1)
	    #print "Fiber %d Ch %d has total Q: %f" % (fib, fibch, totQ)
	    means.append(mean)
	    sigmas.append(rms)
	    charges.append(totQ)

	    #mean.Fill(adc_ts_h[fib][fibch].GetMean(2))
	    #rms.Fill(adc_ts_h[fib][fibch].GetRMS(2))
	   
	    #totQ = 0.0
	    #for i in TS_MASK:
	    #	totQ += charge_ts_h[fib][fibch].GetBinContent(i+1)

	    #charge.Fill(totQ)

	except:
	    None

mean_min = min(means)
mean_max = max(means)
mean_spacing = 0.15 * (mean_max - mean_min)

mean = TH1D("mean", "Mean ADC", 100, mean_min - mean_spacing, mean_max + mean_spacing)
mean.GetXaxis().SetTitle("Mean [ADC]")
mean.GetYaxis().SetTitle("Fiber Channels")

for m in means:
    mean.Fill(m)

rms_min = min(sigmas)
rms_max = max(sigmas)
rms_spacing = 0.15 * (rms_max - rms_min)

rms = TH1D("rms", "RMS ADC", 100, rms_min - rms_spacing, rms_max + rms_spacing)
rms.GetXaxis().SetTitle("#sigma [ADC]")
rms.GetYaxis().SetTitle("Fiber Channels")

for s in sigmas:
    rms.Fill(s)


charge_min = min(charges)
charge_max = max(charges)
charge_spacing = 0.15 * (charge_max - charge_min)

charge = TH1D("charge", "Total Charge", 100, charge_min - charge_spacing, charge_max + charge_spacing)
charge.GetXaxis().SetTitle("Charge [fC]")
charge.GetYaxis().SetTitle("FIber Channels")

for q in charges:
    charge.Fill(q)

mean.Draw()
c.SaveAs("mean_ADC.png")
rms.Draw()
c.SaveAs("rms_ADC.png")
charge.Draw()
c.SaveAs("charge.png")

outF = TFile.Open("mean_rms_totQ_FED_%d.root" % opt.fedId, 'RECREATE')
outF.cd()
mean.SetName("mean_ADC_FED_%d" % opt.fedId)
rms.SetName("rms_ADC_FED_%d" % opt.fedId)
charge.SetName("charge_FED_%d" % opt.fedId)
mean.Write()
rms.Write()
charge.Write()
outF.Close()

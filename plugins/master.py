#####################################################################
#  iQiScan.py							    #
#								    #		
#  hcalraw plugin for analyzing iQi scan data			    #
#								    #
#  Usage:							    #
#  Select with the --plugins option in oneRun.py or look.py	    #
#								    #
#####################################################################

import collections
from configuration import hw, sw
import printer
from pprint import pprint
from ADC_charge import getADC_charge

pedestalRange =      range(1,      1001)
capIDpedestalRange = range(1001,   2601)
pedestalScanRange =  range(2601,   9001)
iqiScanRange =       range(9001,   9801)
gselScanRange =      range(9801,  11101)
phaseScanRange =     range(11101, 21101)

TDC_MAX = 3
ADC_THRESHOLD = 20
SOI = 3	    # Sample (time slice) of interest
EVENTS_PER_SETTING = 100
MAX_SETTINGS = 31
setting_bins = [1 + n * EVENTS_PER_SETTING for n in range(MAX_SETTINGS + 1)]
SKIP_FIRST = 50
#TOTAL_EVENTS = MAX_SETTINGS * EVENTS_PER_SETTING
TOTAL_EVENTS = 21100 

# Other slot 2 links will be ignored
SLOT2_FIBERS = [0, 1, 2, 3, 4, 5, 6, 7]

# Valid Gsel settings
GSEL_CODES = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
              0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]

def master(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
    # sanity check
    #print "Entering top of main loop.."
    for r, raw in enumerate([raw1, raw2]):
        if not raw:
            continue

        nTsMax = raw[None]["firstNTs"]
        #print "nTsMax = ", nTsMax
        for fedId, dct in raw.items():
            if fedId is None:
                continue
            h = dct["header"]
            # Event number 
            evt = h["EvN"]
            # get the important chunks of raw data
            blocks = dct["htrBlocks"].values()
            #pprint(blocks)
            # sanity checks for chunks
           
            #for block in blocks:
            for i, block in enumerate(blocks):
                if type(block) is not dict:
                    printer.warning("FED %d block is not dict" % fedId)
                    continue
                elif "channelData" not in block:
                    printer.warning("FED %d block has no channelData" % fedId)
                    continue

            crate = block["Crate"]
            slot = block["Slot"]

            #with open("block%d.log"%i, "a+") as f:
            #    pprint(block, stream=f)
            for channelData in block["channelData"].values():
                #pprint(channelData)
                #print "Fiber %d Ch %d  errf = %s"%(channelData["Fiber"], channelData["FibCh"], channelData["ErrF"])
                
                if channelData["QIE"]:
                    # check error flags
                    errf = "ErrFNZ" if channelData["ErrF"] else "ErrF0"
                    # Clean or problematic error flag
                    eq = "!=" if channelData["ErrF"] else "=="

                    nAdcMax = 256
                            
                    fib = channelData["Fiber"]
                    fibCh = channelData["FibCh"]

                    #print "fib %d  fibCh %d" % (fib, fibCh) 
                    #if not (fib == 1 and fibCh == 3 and slot == 1): 
                    #    continue 

                    if slot != 2: continue
                    if slot == 2 and fib not in SLOT2_FIBERS: continue			
                    
                    if fib != 6: continue                    
                    #print "Event number:", evt
                    # ts: time slice
                    for (ts, adc) in enumerate(channelData["QIE"]):
                        if nTsMax <= ts:
                            break

                        #if channelData.get("TDC"):
                            #print "TS %d channelData['TDC'] = %s" % (i, channelData["TDC"])

                        
        #			    # Determine the setting by which bin the event falls into
        #			    scan_bin = -1
        #			    for b, lim in enumerate(setting_bins):
        #				if evt < lim:
        #				    scan_bin = b - 1
        #				    break

                        # Ignore events which fall outside the bin range
        #			    if scan_bin < 0: continue
                        
                        #charge = getADC_charge(0, adc)
                     
                        #if ts == SOI:
                        book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_2D" % ts, ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="HB QC Scan  TS %d;Event number;ADC" % ts)  

                        book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_Fib_%d_2D" % (ts,fib), ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="HB QC Scan  Fiber %d  TS %d;Event number;ADC" % (fib, ts))  
                        book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="HB QC Scan  Fiber %d Ch %d  TS %d;Event number;ADC" % (fib, fibCh,ts))  
                        
                        if evt in pedestalRange:
                            #if ts == SOI:
                            #book.fill((evt, adc), "pedestal_TS_%d_ADC_vs_EvtNum_2D" % ts, ( len(pedestalRange), nAdcMax), (min(pedestalRange) - 0.5, -0.5), (max(pedestalRange) + 0.5, nAdcMax - 0.5), title="HB Pedestal Run  TS %d;Event number;ADC" % ts)  
                            book.fill((evt, adc), "pedestal_TS_%d_ADC_vs_EvtNum_Fib_%d_2D" % (ts,fib), ( len(pedestalRange), nAdcMax), (min(pedestalRange) - 0.5, -0.5), (max(pedestalRange) + 0.5, nAdcMax - 0.5), title="HB Pedestal Run  Fiber %d  TS %d;Event number;ADC" % (fib,ts))  

                        elif evt in capIDpedestalRange:        
                            #book.fill((evt, adc), "CapIDpedestal_TS_%d_ADC_vs_EvtNum_2D" % ts, ( len(capIDpedestalRange), nAdcMax), (min(capIDpedestalRange) - 0.5, -0.5), (max(capIDpedestalRange) + 0.5, nAdcMax - 0.5), title="HB CapID%dPedestal Scan  TS %d;Event number;ADC" % (ts%4,ts))  
                            book.fill((evt, adc), "capIDpedestal_TS_%d_ADC_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( len(capIDpedestalRange), nAdcMax), (min(capIDpedestalRange) - 0.5, -0.5), (max(capIDpedestalRange) + 0.5, nAdcMax - 0.5), title="HB CapID%dPedestal Scan  Fiber %d Ch %d  TS %d;Event number;ADC" % (ts%4,fib,fibCh,ts))  

                        elif evt in pedestalScanRange:
                            #if ts == SOI:
                            #book.fill((evt, adc), "pedestalScan_TS_%d_ADC_vs_EvtNum_2D" % ts, ( len(pedestalScanRange), nAdcMax), (min(pedestalScanRange) - 0.5, -0.5), (max(pedestalScanRange) + 0.5, nAdcMax - 0.5), title="HB Pedestal Scan  TS %d;Event number;ADC" % ts)  
                            book.fill((evt, adc), "pedestalScan_TS_%d_ADC_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( len(pedestalScanRange), nAdcMax), (min(pedestalScanRange) - 0.5, -0.5), (max(pedestalScanRange) + 0.5, nAdcMax - 0.5), title="HB Pedestal Scan  Fiber %d Ch %d  TS %d;Event number;ADC" % (fib,fibCh,ts))  

                        elif evt in iqiScanRange: 
                            #book.fill((evt, adc), "iqiScan_TS_%d_ADC_vs_EvtNum_2D" % ts, ( len(iqiScanRange), nAdcMax), (min(iqiScanRange) - 0.5, -0.5), (max(iqiScanRange) + 0.5, nAdcMax - 0.5), title="HB iQi Scan  TS %d;Event number;ADC" % ts)  
                            book.fill((evt, adc), "iqiScan_TS_%d_ADC_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( len(iqiScanRange), nAdcMax), (min(iqiScanRange) - 0.5, -0.5), (max(iqiScanRange) + 0.5, nAdcMax - 0.5), title="HB iQi Scan  Fiber %d Ch %d  TS %d;Event number;ADC" % (fib,fibCh,ts))  
                        elif evt in gselScanRange:  
                            #if ts == SOI:
                            #book.fill((evt, adc), "gselScan_TS_%d_ADC_vs_EvtNum_2D" % ts, ( len(gselScanRange), nAdcMax), (min(gselScanRange) - 0.5, -0.5), (max(gselScanRange) + 0.5, nAdcMax - 0.5), title="HB iQi Gsel Scan  TS %d;Event number;ADC" % ts)  
                            gsel = (evt - min(gselScanRange))/100
                            charge = getADC_charge(GSEL_CODES[gsel], adc)
                            book.fill((evt, adc), "gselScan_TS_%d_ADC_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( len(gselScanRange), nAdcMax), (min(gselScanRange) - 0.5, -0.5), (max(gselScanRange) + 0.5, nAdcMax - 0.5), title="HB iQi Gsel Scan  Fiber %d Ch %d  TS %d;Event number;ADC" % (fib,fibCh,ts))  
                            book.fill((evt, charge), "gselScan_TS_%d_Charge_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( len(gselScanRange), 100), (min(gselScanRange) - 0.5, -0.5), (max(gselScanRange) + 0.5, 15000.0 - 0.5), title="HB iQi Gsel Scan  Fiber %d Ch %d  TS %d;Event number;Charge [fC]" % (fib,fibCh,ts))  

                        elif evt in phaseScanRange:  
                            #if ts == SOI:
                            #book.fill((evt, adc), "phaseScan_TS_%d_ADC_vs_EvtNum_2D" % ts, ( len(phaseScanRange), nAdcMax), (min(phaseScanRange) - 0.5, -0.5), (max(gselScanRange) + 0.5, nAdcMax - 0.5), title="HB iQi Phase Scan  TS %d;Event number;ADC" % ts)  
                            book.fill((evt, adc), "phaseScan_TS_%d_ADC_vs_EvtNum_Fib_%d_Ch_%d_2D" % (ts,fib,fibCh), ( len(phaseScanRange), nAdcMax), (min(phaseScanRange) - 0.5, -0.5), (max(gselScanRange) + 0.5, nAdcMax - 0.5), title="HB iQi Phase Scan  Fiber %d Ch %d  TS %d;Event number;ADC" % (fib,fibCh,ts))  
                #if ts == SOI:
                #book.fill((evt,charge), "TS_%d_Charge_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (SOI, fedId, crate, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=charge,title="Charge vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  

                        continue
                    
                        book.fill((ts, adc), "ADC_vs_TS_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh), (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax-0.5, nAdcMax-0.5), title="ADC vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d;time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh))

                        if ts == SOI: 
                            book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_2D" % SOI, ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="iQi Gsel Scan  TS %d;Event number;ADC" % SOI)  
                            book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (SOI, fedId, crate, slot, fib, fibCh), (TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="ADC vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;ADC;Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  
                            book.fill(evt, "TS_%d_ADC_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_1D" % (SOI, fedId, crate, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=adc,title="ADC vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;ADC;Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  

                        book.fill((evt, charge), "TS_%d_Charge_vs_EvtNum_2D" % SOI, ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, 15000 - 0.5), title="iQi Gsel Scan  TS %d;Event number;Charge [fC]" % SOI)  
                        book.fill((evt, charge), "TS_%d_Charge_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (SOI, fedId, crate, slot, fib, fibCh), (TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, 15000 - 0.5), title="Charge vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  
                        book.fill(evt, "TS_%d_Charge_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_1D" % (SOI, fedId, crate, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=charge,title="Charge vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  


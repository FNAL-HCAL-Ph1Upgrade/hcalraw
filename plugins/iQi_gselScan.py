#####################################################################
#  iqi_gselScan.py						    #
#								    #		
#  hcalraw plugin for analyzing iQi shunt scan data		    #
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

TDC_MAX = 3
ADC_THRESHOLD = 20

SOI = 3	    # Sample (time slice) of interest
EVENTS_PER_SETTING = 100
MAX_SETTINGS = 13
setting_bins = [1 + n * EVENTS_PER_SETTING for n in range(MAX_SETTINGS + 1)]
SKIP_FIRST = 50
TOTAL_EVENTS = MAX_SETTINGS * EVENTS_PER_SETTING
GOOD_EVENTS_EXPECTED = MAX_SETTINGS * (EVENTS_PER_SETTING - SKIP_FIRST)


# Valid Gsel settings
GSEL_CODES = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
              0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]


def iqi_gselScan(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
    # sanity check
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

                        #if slot == 2 and fib not in SLOT2_FIBERS: continue			
                        #if (iEvent % EVENTS_PER_SETTING < SKIP_FIRST): break  # Skip event 		    


                        #print "Event number:", evt

                        # ts: time slice
                        for (ts, adc) in enumerate(channelData["QIE"]):
                            if nTsMax <= ts:
                                break

                            #if channelData.get("TDC"):

                            #print "TS %d channelData['TDC'] = %s" % (i, channelData["TDC"])



                            scan_bin = (evt -1) / EVENTS_PER_SETTING
                            #charge = getADC_charge(GSEL_CODES[scan_bin], adc)
                            charge = getADC_charge(0, adc)

                            #print "Event %d" % (evt)
                            # TS 2

                            if ts == SOI:
                                book.fill((evt,charge), "gselScan_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=charge,title="Charge vs Event Number  TS %d  Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, slot, fib, fibCh))  
                            #book.fill((evt,charge), "TS_%d_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (ts, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=charge,title="Charge vs Event Number  TS %d  Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (ts, slot, fib, fibCh))  
                            book.fill((evt,adc), "TS_%d_ADC_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (ts, slot, fib, fibCh), (TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax-0.5), title="ADC vs Event Number  TS %d  Slot %d Fib %d Ch %d;Event number;ADC;Counts / bin" % (ts, slot, fib, fibCh))  




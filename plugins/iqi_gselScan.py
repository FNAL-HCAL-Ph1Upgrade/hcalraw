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

EVENTS_PER_SETTING = 100
#MAX_SETTINGS = 64
MAX_SETTINGS = 13
setting_bins = [1 + n * EVENTS_PER_SETTING for n in range(MAX_SETTINGS + 1)]

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


                for channelData in block["channelData"].values():
                    #pprint(channelData)
                    #print "Fiber %d Ch %d  errf = %s"%(channelData["Fiber"], channelData["FibCh"], channelData["ErrF"])
                    if channelData["QIE"]:
                        # check error flags
                        errf = "ErrFNZ" if channelData["ErrF"] else "ErrF0"
                        # Clean or problematic error flag
                        eq = "!=" if channelData["ErrF"] else "=="

                        nAdcMax = 256
                                
                        # ts: time slice
                        for (ts, adc) in enumerate(channelData["QIE"]):
                            if nTsMax <= ts:
                                break

                            #if channelData.get("TDC"):
                                #print "TS %d channelData['TDC'] = %s" % (i, channelData["TDC"])

                            fib = channelData["Fiber"]
                            fibCh = channelData["FibCh"]

                            #print "fib %d  fibCh %d" % (fib, fibCh) 
                            #if not (fib == 19 and fibCh == 4): 
                        #	continue 
                            
                            # Determine the setting by which bin the event falls into
                            scan_bin = -1
                            for b, lim in enumerate(setting_bins):
                                if evt < lim:
                                    scan_bin = b - 1
                                    break

                            # Ignore events which fall outside the bin range
                            if scan_bin < 0: continue
                            
                            charge = getADC_charge(GSEL_CODES[scan_bin], adc)
                            

                            # TS 2
                            if ts == 2:
                                book.fill((evt, adc), "TS_2_ADC_vs_EvtNum_%s" % (errf), (1300, nAdcMax), (-0.5, -0.5), (1299.5, nAdcMax - 0.5), title="ADC vs Event Number  TS 2 (ErrF %s 0);Event number;ADC;Counts / bin" % (eq))  	
                                #book.fill((evt, adc), "TS_2_ADC_vs_EvtNum_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_2D" % (errf, fedId, crate, slot, fib), (1300, nAdcMax), (-0.5, -0.5), (1299.5, nAdcMax - 0.5), title="ADC vs Event Number  TS 2 FED %d Crate %d Slot %d Fib %d (ErrF %s 0);Event number;ADC;Counts / bin" % (fedId, crate, slot, fib, eq))  
                                book.fill((evt, adc), "TS_2_ADC_vs_EvtNum_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh), (1300, nAdcMax), (-0.5, -0.5), (1299.5, nAdcMax - 0.5), title="ADC vs Event Number  TS 2 FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Event number;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))  
                                #book.fill(adc, "TS_2_ADC_vs_EvtNum_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh), nAdcMax, -0.5, nAdcMax - 0.5, title="ADC vs Event Number  TS 2 FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Event number;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq)) 
                            
                            
                                #book.fill((ts, charge), "Charge_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
                            #      nTsMax, -0.5, nTsMax-0.5,
                             #     title="Charge vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))

                            if not fewerHistos:
                                book.fill((ts, adc), "ADC_vs_TS_%s_gsel_%d" % (errf, int(GSEL_CODES[scan_bin])),
                                  (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax-0.5, nAdcMax-0.5),
                                  title="ADC vs TS  Gsel %d  (ErrF %s 0);time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], eq))

                                #book.fill((ts, adc), "ADC_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
                                #      nTsMax, -0.5, nTsMax-0.5,
                                 #     title="ADC vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))

                                book.fill((ts, adc), "ADC_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
                                  (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax-0.5, nAdcMax-0.5),
                                  title="ADC vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))
                            
                                book.fill((ts, charge), "Charge_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
                                  (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
                                  title="Charge vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))
                             
                                book.fill((scan_bin, adc),
                                  "ADC_iQi_GselScan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
                                  (MAX_SETTINGS, nAdcMax), (-0.5, -0.5), (MAX_SETTINGS - 0.5, nAdcMax - 0.5),
                                  title="ADC iQi Gsel Scan  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Gsel setting index;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
                               
                            
                                book.fill((scan_bin, adc),
                                  "ADC_iQi_GselScan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
                                  MAX_SETTINGS, -0.5, MAX_SETTINGS - 0.5,
                                  title="ADC iQi Gsel Scan  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Gsel setting index;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
                            
                            
                            
                                book.fill((scan_bin, charge),
                                  "Charge_iQi_GselScan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
                                  (MAX_SETTINGS, 100), (-0.5, -0.5), (MAX_SETTINGS - 0.5, 20000),
                                  title="Charge iQi Gsel Scan  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Gsel setting index;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
                               

                                book.fill((scan_bin, charge),
                                  "Charge_iQi_GselScan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
                                  MAX_SETTINGS, -0.5, MAX_SETTINGS - 0.5,
                                  title="Charge iQi Gsel Scan  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Gsel setting index;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
                               

                                tdc = channelData["TDC"][ts]
                                if adc > ADC_THRESHOLD: 
                                    book.fill((scan_bin, tdc),
                                      "TDC_iQi_GselScan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
                                      (MAX_SETTINGS, TDC_MAX+1), (-0.5, -0.5), (MAX_SETTINGS - 0.5, TDC_MAX + 0.5),
                                      title="TDC iQi Gsel Scan  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Gsel setting index;TDC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
                               
                            
                            
                            
                            """
                            if i > 0:
                            book.fill((i, adc), 
                                                  "NoTS0_ADC_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh), (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
                                                  title="ADC vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))

                            book.fill((i, charge), "NoTS0_Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
                                  nTsMax, -0.5, nTsMax-0.5,
                                  title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))

                            book.fill((i, charge), "NoTS0_Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
                                  (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
                                  title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
                            """

#####################################################################
#  uniqueID.py							                            #
#                               								    #		
#  Plugin to be used with hcalraw to the uniqueID		            #
#  of each QIE card from a linkTestMode run.			            #
#								                                    #
#  Usage:							                                #
#  Select with the --plugins option in oneRun.py or look.py	        #
#								                                    #
#####################################################################

import collections
from configuration import hw, sw
import printer
from pprint import pprint

#EVENTS_PER_SETTING = 100
#MAX_SETTINGS = 64
#ped_bins = [1 + n * EVENTS_PER_SETTING for n in range(MAX_SETTINGS + 1)]


# Other slot 2 links will be ignored
SLOT2_FIBERS = [0, 1, 2, 3, 4, 5, 7, 8]


def uniqueID(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
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
        
            # Initialize uniqueID dictionary
            uniqueID = {}
		
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

                # If slot not in uniqueID, initialize them
                if slot not in uniqueID:
                    uniqueID[slot] = {}

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
                                
                        # ts: time slice
                        for (ts, adc) in enumerate(channelData["QIE"]):
                            if nTsMax <= ts:
                                break
                            
                            fib = channelData["Fiber"]
                            fibCh = channelData["FibCh"]

                            # If fiber and time slice not initialized, initialize them
                            if fib not in uniqueID[slot]:
                                uniqueID[slot][fib] = {}
                            if fibCh not in uniqueID[slot][fib]:
                                uniqueID[slot][fib][ts] = "70"

                            # Check if this is the last loop for this time slice
                            if len(uniqueID[slot][fib][ts]) == 22:
                                hexD = "%0.1X" % adc
                            else:
                                hexD = "%0.2X" % adc

                            uniqueID[slot][fib][ts] = "".join((hexD,uniqueID[slot][fib][ts]))

                            # Format hex codes with 0x
                            if (len(uniqueID[slot][fib][ts]) == 8) or (len(uniqueID[slot][fib][ts]) == 19):
                                uniqueID[slot][fib][ts] = "".join((" 0x",uniqueID[slot][fib][ts]))
                            
                            book.fillGraph((0,0),"UniqueID_Crate_%d_Slot_%d_Fib_%d_TS_%d_%s" % (crate,slot,fib,ts,uniqueID[slot][fib][ts]),title="UniqueID Crate %d Slot %d Fib %d TS %d: %s" % (crate,slot,fib,ts,uniqueID[slot][fib][ts]))
                                
#                            scan_bin = -1
#                            for b, lim in enumerate(ped_bins):
#                                if evt < lim:
#                                    scan_bin = b - 1
#                                    break
#             
#                            if slot == 2 and fib not in SLOT2_FIBERS: continue
#
#                            book.fill((evt, adc),
#                                "ADC_ped_scan_%s" % errf, (6400, nAdcMax), (-0.5, -0.5), (6399.5, nAdcMax - 0.5),
#                                title="Pedestal Scan  ADC vs Evt Num (ErrF %s 0);Event number;ADC;Counts / bin" % eq)
#
#
#                            book.fill((evt, adc),
#                                "ADC_ped_scan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
#                                (6400, nAdcMax), (-0.5, -0.5), (6399.5, nAdcMax - 0.5),
#                                title="Pedestal Scan  Adc vs Evt Num  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);PedestalDAC setting;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#
#                            charge = float(adcCharges[adc])
#                            
#                            book.fill((evt, charge),
#                                  "Charge_ped_scan",
#                                  (6400, 50), (-0.5, -0.5), (6399.5, 299.5),
#                                  title="Pedestal Scan  Charge vs Evt Num;Event number;Charge [fC];Counts / bin")
#
#                            book.fill((evt, charge),
#                                  "Charge_ped_scan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
#                                  (6400, 50), (-0.5, -0.5), (6399.5, 299.5),
#                                  title="Pedestal Scan  Charge vs Evt Num  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);PedestalDAC setting;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#
#                            if fewerHistos: continue
#                            if ts > 0:
#                                book.fill((evt, adc),
#                                    "NoTS0_ADC_ped_scan_%s" % errf, (6400, nAdcMax), (-0.5, -0.5), (6400 - 0.5, nAdcMax - 0.5),
#                                    title="Pedestal Scan  ADC vs Evt Num (ErrF %s 0);Event number;ADC;Counts / bin" % eq)
#
#
#                                #book.fill((evt, adc),
#                                #    "NoTS0_ADC_ped_scan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
#                                #    (6400, nAdcMax), (-0.5, -0.5), (6400 - 0.5, nAdcMax - 0.5),
#                                #    title="Pedestal Scan  Adc vs Evt Num  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Event Number;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#                                book.fill((evt, charge),
#                                     "NoTS0_Charge_ped_scan",
#                                     (6400, 50), (-0.5, -0.5), (6400 - 0.5, 299.5),
#                                     title="Pedestal Scan  Charge vs Evt Num;Event Number;Charge [fC];Counts / bin")
#                                
#                                book.fill((evt, charge),
#                                     "NoTS0_Charge_ped_scan_%s" % errf,
#                                     (6400, 50), (-0.5, -0.5), (6400 - 0.5, 299.5),
#                                     title="Pedestal Scan  Charge vs Evt Num (ErrF %s 0);Event Number;Charge [fC];Counts / bin" % eq)
#
#
#                                book.fill((evt, charge),
#                                     "NoTS0_Charge_ped_scan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
#                                     (6400, 50), (-0.5, -0.5), (6400 - 0.5, 299.5),
#                                     title="Pedestal Scan  Charge vs Evt num  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Event Number;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#                                
#
#                                """
#                                book.fill((scan_bin, adc),
#                                      "ADC_ped_scan_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
#                                      MAX_SETTINGS, -0.5, MAX_SETTINGS - 0.5,
#                                      title="ADC Pedestal Scan  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);PedestalDAC setting;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq)) 
#
#
#                                charge = float(adcCharges[adc])
#                                # Linearized adc (charge vs TS)
#                                book.fill((i, charge), "Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
#                                      nTsMax, -0.5, nTsMax-0.5,
#                                      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#                                book.fill((i, charge), "Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
#                                      (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
#                                      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#                               
#                                if i > 0:
#                                book.fill((i, adc), 
#                                                      "NoTS0_ADC_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh), (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
#                                                      title="ADC vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#                                book.fill((i, charge), "NoTS0_Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
#                                      nTsMax, -0.5, nTsMax-0.5,
#                                      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#
#                                book.fill((i, charge), "NoTS0_Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
#                                      (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
#                                      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
#                                """

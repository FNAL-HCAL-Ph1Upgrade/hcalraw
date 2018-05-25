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



# Other slot 2 links will be ignored
SLOT2_FIBERS = [0, 1, 2, 3, 4, 5, 6, 7]


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
            minor = {}
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

                # initialize minor firmware version byte dictionary
                if slot not in minor:
                    minor[slot] = {}
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
                        #pprint(channelData["TDC"])

                        # ts: time slice
                        for (ts, adc) in enumerate(channelData["QIE"]):
                            if nTsMax <= ts:
                                break
                            tdc = channelData["TDC"][ts]
                            fib = channelData["Fiber"]
                            fibCh = channelData["FibCh"]

                            #if slot == 1: continue

                            #if slot == 2 and fib not in SLOT2_FIBERS: continue

                            # Ignore TS 0
                            if ts == 0:
                                continue
                                                       
                            
                            # If fiber and time slice not initialized, initialize them
                            if fib not in uniqueID[slot]:
                                uniqueID[slot][fib] = {}
                            if ts not in uniqueID[slot][fib]:
                                uniqueID[slot][fib][ts] = "70"

                            # initiialize minor firmware version byte
                            if fib not in minor[slot]:
                                minor[slot][fib] = {}
                            if ts not in minor[slot][fib]:
                                minor[slot][fib][ts] = 0

                            
                            # Compile Byte10 from TDC
                            if fibCh in range(4):
                                minorTS = int("%X" % tdc)
                                minor[slot][fib][ts] = (minor[slot][fib][ts]*(10**(len(str(minor[slot][fib][ts])) - 1))) + minorTS

                            # Check if this is the last loop for this time slice
                            #if len(uniqueID[slot][fib][ts]) == 21:
                            if fibCh == 7:
                                uniqueID[slot][fib][ts] = "".join((uniqueID[slot][fib][ts]," FW:%X.%02d"%(adc,minor[slot][fib][ts])))
                            else:
                                #hexD = "%0.2X" % adc
                                uniqueID[slot][fib][ts] = "".join(("%0.2X" % adc,uniqueID[slot][fib][ts]))

                            # Format hex codes with 0x
                            #if (len(uniqueID[slot][fib][ts]) == 8):
                            if fibCh == 2:
                                uniqueID[slot][fib][ts] = "".join((" 0x",uniqueID[slot][fib][ts]))
                            #if (len(uniqueID[slot][fib][ts]) == 19):
                            if fibCh == 6:
                                uniqueID[slot][fib][ts] = "".join(("0x",uniqueID[slot][fib][ts]))
                            


                            #book.fill((adc),"ADC_vs_FibCh_Slot_%d_fib_%d_ts_%d" % (slot,fib,ts),(nAdcMax),(-0.5),(nAdcMax-0.5),title="ADC vs Fiber Channel Slot %d Fiber %d TS %d;ADC;N_{e}" % (slot,fib,ts))

                            book.fill((fibCh,adc),"ADC_vs_FibCh_Slot_%d_fib_%d_ts_%d" % (slot,fib,ts),(16,nAdcMax),(0,-0.5),(16,nAdcMax-0.5),title="ADC vs Fiber Channel Slot %d Fiber %d TS %d;ADC;N_{e}" % (slot,fib,ts))

#                            pprint(minor[slot][fib])                

                for slot in uniqueID: 
                    for fib in uniqueID[slot]:
                        for ts in uniqueID[slot][fib]:
                            book.fillGraph((0,0),"UniqueID_Slot_%d_Fib_%d_TS_%d_%s" % (slot,fib,ts,uniqueID[slot][fib][ts]),title="%s" % (uniqueID[slot][fib][ts]))

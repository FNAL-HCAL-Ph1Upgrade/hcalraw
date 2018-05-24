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
                                

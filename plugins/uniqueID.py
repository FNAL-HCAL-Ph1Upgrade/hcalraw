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

    # Initialize a dictionary for storing location of a card if an error occurs
    errorLoc = {}

    for r, raw in enumerate([raw1, raw2]):
        if not raw:
            continue

        nTsMax = raw[None]["firstNTs"]

        for fedId, dct in raw.items():
            if fedId is None:
                    continue
                
            h = dct["header"]
            # Event number 
            evt = h["EvN"]

            # get the important chunks of raw data
            blocks = dct["htrBlocks"].values()
        


            
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
                    if channelData["QIE"]:
                        # check error flags
                        errf = "ErrFNZ" if channelData["ErrF"] else "ErrF0"
                        # Clean or problematic error flag
                        eq = "!=" if channelData["ErrF"] else "=="

                        nAdcMax = 256
                        #pprint(channelData["TDC"])
                        
                        
                        fib = channelData["Fiber"]
                        fibCh = channelData["FibCh"]
                        

                        # Only check in slots known to have a card installed
                        if slot == 1: continue
                        if slot == 2 and fib not in SLOT2_FIBERS: continue

                        # ts: time slice
                        for (ts, adc) in enumerate(channelData["QIE"]):
                            if nTsMax <= ts:
                                break
                            tdc = channelData["TDC"][ts]


                            # Ignore TS 0
                            if ts == 0:
                                continue
                            
                            # Fill TProfile with ADC and TDC information, with ADC in bins 0-7 and TDC in bins 8-16
                            book.fill((fibCh,adc),"UniqueID_Slot_%d_Fib_%d" % (slot,fib),16, 0.5, 16.5, title="")
                            book.fill((fibCh+8,tdc),"UniqueID_Slot_%d_Fib_%d" % (slot,fib),16, 0.5, 16.5, title="")
                        
                        ## Construct and set unique ID
                        ## Prints a warning if any bin's rms != 0


                        # Get histogram
                        hist = book.Get("UniqueID_Slot_%d_Fib_%d" % (slot,fib))

                        # inittialize uniqueID string
                        uniqueID = ""
                        
                        # Create a list of bin values
                        binValues = []
                                        
                        # If an error has occurred on current slot and fiber, do not check for error again
                        if slot in errorLoc:
                            if errorLoc[slot] == fib:
                                continue


                        # Check if rms of all bins = 0, if not, print warning and stop checking that link
                        # If rms = 0, put bin value into a list
                        for b in range(hist.GetNbinsX()):
                            if(hist.GetBinError(b) != 0):
                                printer.warning("Slot %d Fiber %d linkTestMode RMS Error" % (slot,fib))
                                errorLoc[slot] = fib
                                break
                            else:
                                binValues.append(int(hist.GetBinContent(b)))

                        

                        # If list of bin values is not full (due to an error), go to next link
                        if(len(binValues)<16):
                            continue
                        minor = 0

                        # Compile Byte 10 from TDC into minor firmware version
                        for tdc in binValues[8:12]:
                            minorDigit = int("%X" % tdc)
                            minor = (minor*(10**(len(str(minor)) - 1))) + minorDigit
                        
                        # Check if first bit TDC 5 is 1
                        if((binValues[13] == 2) or (binValues[13] == 3)):
                            topBot = "Top "
                        else:
                            topBot = "Bot "
                         
                      
                        # Compile uniqueID string
                        uniqueID = "".join(["0x",str("%0.2X"%binValues[6]),str("%0.2X"%binValues[5]),str("%0.2X"%binValues[4]),str("%0.2X"%binValues[3]),"_0x",str("%0.2X"%binValues[2]),str("%0.2X"%binValues[1]),str("%0.2X"%binValues[0]),"70 ",topBot,str("%X"%binValues[7]),"_",str("%01d"%minor)])
                        

                        # Set uniqueID as title of TProfile
                        hist.SetTitle(uniqueID)



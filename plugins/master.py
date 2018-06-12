#####################################################################
#  master.py                                                        #
#								                                    #		
#  hcalraw plugin for analyzing master QC scan data		            #
#                                                                   #
#  Usage:							                                #
#  Select with the --plugins option in oneRun.py or look.py	        #
#								                                    #
#####################################################################

import collections
from configuration import hw, sw
import printer
from pprint import pprint
#from ADC_charge import getADC_charge

# Conversions from ADC to charge [fC] for unshunted case (Gsel = 0) 
adcToCharge=[1.62, 4.86, 8.11, 11.35, 14.59, 17.84, 21.08, 24.32, 27.57, 30.81, 34.05, 37.30, 40.54, 43.78, 47.03, 50.27, 56.75, 63.24, 69.73, 76.21, 82.70, 89.19, 95.67, 102.2, 108.6, 115.1, 121.6, 128.1, 134.6, 141.1, 147.6, 154.0, 160.5, 167.0, 173.5, 180.0, 193.0, 205.9, 218.9, 231.9, 244.9, 257.8, 270.8, 283.8, 296.7, 309.7, 322.7, 335.7, 348.6, 361.6, 374.6, 387.6, 400.5, 413.5, 426.5, 439.4, 452.4, 478.4, 504.3, 530.3, 556.2, 582.1, 608.1, 634.0, 577.6, 603.0, 628.5, 654.0, 679.5, 705.0, 730.5, 756.0, 781.5, 806.9, 832.4, 857.9, 883.4, 908.9, 934.4, 959.9, 1010.9, 1061.8, 1112.8, 1163.8, 1214.8, 1265.7, 1316.7, 1367.7, 1418.7, 1469.6, 1520.6, 1571.6, 1622.6, 1673.5, 1724.5, 1775.5, 1826.5, 1877.5, 1928.4, 1979.4, 2081.4, 2183.3, 2285.3, 2387.2, 2489.2, 2591.1, 2693.1, 2795.0, 2897.0, 2998.9, 3100.9, 3202.8, 3304.8, 3406.8, 3508.7, 3610.7, 3712.6, 3814.6, 3916.5, 4018.5, 4120.4, 4324.3, 4528.2, 4732.1, 4936.1, 5140.0, 5343.9, 5547.8, 5331.9, 5542.5, 5753.1, 5963.7, 6174.3, 6384.9, 6595.5, 6806.1, 7016.7, 7227.3, 7437.9, 7648.4, 7859.0, 8069.6, 8280.2, 8490.8, 8912.0, 9333.2, 9754.3, 10175.5, 10596.7, 11017.9, 11439.1, 11860.3, 12281.4, 12702.6, 13123.8, 13545.0, 13966.2, 14387.3, 14808.5, 15229.7, 15650.9, 16072.1, 16493.2, 16914.4, 17756.8, 18599.1, 19441.5, 20283.9, 21126.2, 21968.6, 22811.0, 23653.3, 24495.7, 25338.0, 26180.4, 27022.8, 27865.1, 28707.5, 29549.9, 30392.2, 31234.6, 32076.9, 32919.3, 33761.7, 34604.0, 36288.8, 37973.5, 39658.2, 41342.9, 43027.6, 44712.4, 46397.1, 43321.6, 44990.1, 46658.6, 48327.1, 49995.7, 51664.2, 53332.7, 55001.2, 56669.7, 58338.2, 60006.7, 61675.2, 63343.7, 65012.3, 66680.8, 68349.3, 71686.3, 75023.3, 78360.3, 81697.4, 85034.4, 88371.4, 91708.4, 95045.4, 98382.5, 101719.5, 105056.5, 108393.5, 111730.6, 115067.6, 118404.6, 121741.6, 125078.6, 128415.7, 131752.7, 135089.7, 141763.8, 148437.8, 155111.8, 161785.9, 168459.9, 175134.0, 181808.0, 188482.1, 195156.1, 201830.1, 208504.2, 215178.2, 221852.3, 228526.3, 235200.4, 241874.4, 248548.4, 255222.5, 261896.5, 268570.6, 275244.6, 288592.7, 301940.8, 315288.9, 328637.0, 341985.1, 355333.1, 368681.2]


uniqueIDRange =      xrange(1,       101)
pedestalRange =      xrange(101,    1101)
capIDpedestalRange = xrange(1101,   2701)
pedestalScanRange =  xrange(2701,   9101)
iQiScanRange =       xrange(9101,   9901)
gselScanRange =      xrange(9901,  11201)
phaseScanRange =     xrange(11201, 21201)


# Compute this stuff once
uniqueIDRange_events = len(uniqueIDRange)
pedestalRange_events = len(pedestalRange)
capIDpedestalRange_events = len(capIDpedestalRange)
pedestalScanRange_events = len(pedestalScanRange)
iQiScanRange_events = len(iQiScanRange)
gselScanRange_events = len(gselScanRange)
phaseScanRange_events = len(phaseScanRange)


uniqueIDRange_min = min(uniqueIDRange)
uniqueIDRange_max = max(uniqueIDRange)
pedestalRange_min = min(pedestalRange)
pedestalRange_max = max(pedestalRange)
capIDpedestalRange_min = min(capIDpedestalRange)
capIDpedestalRange_max = max(capIDpedestalRange)
pedestalScanRange_min = min(pedestalScanRange)
pedestalScanRange_max = max(pedestalScanRange)
iQiScanRange_min = min(iQiScanRange)
iQiScanRange_max = max(iQiScanRange)
gselScanRange_min = min(gselScanRange)
gselScanRange_max = max(gselScanRange)
phaseScanRange_min = min(phaseScanRange)
phaseScanRange_max = max(phaseScanRange)

uniqueIDRange_binMin = uniqueIDRange_min - 0.5
uniqueIDRange_binMax = uniqueIDRange_max + 0.5
pedestalRange_binMin = pedestalRange_min - 0.5
pedestalRange_binMax = pedestalRange_max + 0.5
capIDpedestalRange_binMin = capIDpedestalRange_min - 0.5
capIDpedestalRange_binMax = capIDpedestalRange_max + 0.5
pedestalScanRange_binMin = pedestalScanRange_min - 0.5
pedestalScanRange_binMax = pedestalScanRange_max + 0.5
iQiScanRange_binMin = iQiScanRange_min - 0.5
iQiScanRange_binMax = iQiScanRange_max + 0.5
gselScanRange_binMin = gselScanRange_min - 0.5
gselScanRange_binMax = gselScanRange_max + 0.5
phaseScanRange_binMin = phaseScanRange_min - 0.5
phaseScanRange_binMax = phaseScanRange_max + 0.5


#TDC_MAX = 3
#ADC_THRESHOLD = 20
SOI = 3	    # Sample (time slice) of interest
TOTAL_EVENTS = max(phaseScanRange)
TOTAL_EVENTS_binMax = TOTAL_EVENTS + 0.5

# Other slot 2 links will be ignored
#SLOT2_FIBERS = [0, 1, 2, 3, 4, 5, 6, 7]

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
        for fedId, dct in sorted(raw.iteritems()):
            if fedId is None:
                continue
            h = dct["header"]
            # Event number 
            evt = h["EvN"]
            # get the important chunks of raw data
            blocks = dct["htrBlocks"].values()
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
                    if channelData["QIE"]:
                        # check error flags
                        #errf = "ErrFNZ" if channelData["ErrF"] else "ErrF0"
                        # Clean or problematic error flag
                        #eq = "!=" if channelData["ErrF"] else "=="

                        #nAdcMax = 256
                                
                        fib = channelData["Fiber"]
                        fibCh = channelData["FibCh"]


                        #if slot != 2: continue
                        #if slot == 2 and fib not in SLOT2_FIBERS: continue			
                        if slot == 2 and fib > 7: continue 
                        
                        # ts: time slice
                        for (ts, adc) in enumerate(channelData["QIE"]):
                            if nTsMax <= ts:
                                break

                            tdc = channelData["TDC"][ts]


                            charge = adcToCharge[adc] 
                           
                            if not fewerHistos:
                                book.fill((evt, charge), "TS_%d_Charge_vs_EvtNum" % ts, TOTAL_EVENTS, 0.5, TOTAL_EVENTS_binMax, title="HB QC Scan  TS %d;Event number;Charge[fC]" % ts)  
                                book.fill((evt, charge), "TS_%d_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (ts,slot,fib,fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS_binMax, title="HB QC Scan  Slot %d Fiber %d Ch %d  TS %d;Event number;Charge [fC]" % (slot, fib, fibCh, ts)) 
                            if ts > 0 and evt <= uniqueIDRange_max and evt >= uniqueIDRange_min:
                                book.fill((fibCh,adc),"UniqueID_Slot_%d_Fib_%d" % (slot,fib),16,0.5,16.5,title="")
                                book.fill((fibCh+8,tdc),"UniqueID_Slot_%d_Fib_%d" % (slot,fib),16,0.5,16.5,title="")
                         
                            
                            elif ts > 0 and evt <= pedestalRange_max and evt >= pedestalRange_min:
                                book.fill((evt, charge), "pedestal_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (slot,fib,fibCh), pedestalRange_events, pedestalRange_binMin, pedestalRange_binMax, title="HB Pedestal Run  Slot %d Fiber %d Ch %d  TS 1-7;Event number;Charge [fC]" % (slot, fib, fibCh))  

                            elif evt <= capIDpedestalRange_max and evt >= capIDpedestalRange_min and ts > 0 and ts < 5:       
                                book.fill((evt, charge), "capID%dpedestal_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (ts%4, slot, fib, fibCh), capIDpedestalRange_events, capIDpedestalRange_binMin, capIDpedestalRange_binMax, title="HB CapID%dPedestal Scan  Slot %d Fiber %d Ch %d;Event number;Charge [fC]" % (ts%4, slot, fib, fibCh))  

                            elif ts > 0 and evt <= pedestalScanRange_max and evt >= pedestalScanRange_min:
                                book.fill((evt, charge), "pedestalScan_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (slot, fib, fibCh), pedestalScanRange_events, pedestalScanRange_binMin,  pedestalScanRange_binMax, title="HB Pedestal Scan  Slot %d Fiber %d Ch %d  TS 1-7;Event number;Charge [fC]" % (slot, fib, fibCh))  

                            elif ts == SOI and evt <= iQiScanRange_max and evt >= iQiScanRange_min:
                                book.fill((evt, charge), "iQiScan_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (slot, fib, fibCh), iQiScanRange_events, iQiScanRange_binMin, iQiScanRange_binMax, title="HB iQi Scan  Slot %d Fiber %d Ch %d  TS %d;Event number;Charge [fC]" % (slot, fib, fibCh, ts))  
                            
                            elif ts == SOI and evt <= gselScanRange_max and evt >= gselScanRange_min: 
                                #gsel = (evt - min(gselScanRange))/100
                                #charge = getADC_charge(GSEL_CODES[gsel], adc)
                                book.fill((evt, charge), "gselScan_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (slot, fib, fibCh), gselScanRange_events, gselScanRange_binMin, gselScanRange_binMax, title="HB iQi Gsel Scan  Slot %d Fiber %d Ch %d  TS %d;Event number;Charge [fC]" % (slot, fib, fibCh, ts))  

                            # Phase scan
                            elif ts > 0 and ts < 4: 
                                book.fill((evt, charge), "phaseScan_TS_%d_Charge_vs_EvtNum_Slot_%d_Fib_%d_Ch_%d" % (ts, slot, fib, fibCh), phaseScanRange_events, phaseScanRange_binMin, phaseScanRange_binMax, title="HB iQi Phase Scan  Slot %d Fiber %d Ch %d  TS %d;Event number;Charge [fC]" % (slot, fib, fibCh, ts))  

                       #Compute uniqueID once after all linkTestMode runs have been histogrammed
                            if evt == uniqueIDRange_max + 1 and ts == 0 and fibCh == 0:
                                hist = book.Get("UniqueID_Slot_%d_Fib_%d" % (slot,fib))
                                uniqueID = ""
                                binValues = []
                                isError = False
                                for b in xrange(hist.GetNbinsX()):
                                    if (hist.GetBinError(b) != 0) and not isError:
                                        printer.warning("Slot %d Fiber %d linkTestMode RMS Error" % (slot,fib))
                                        isError = True
                                    binValues.append(int(hist.GetBinContent(b)))

                                minor = 0

                                # Compile Byte 10 from TDC into minor firmware version
                                for tdc in binValues[8:12]:
                                    minorDigit = int("%X" % tdc)
                                    minor = minor*(10**(len(str(minor)) - 1)) + minorDigit

                                # Determine if top or bottom FPGA
                                if (binValues[13] == 2) or (binValues[13] == 3):
                                    topBot = "Top "
                                else:
                                    topBot = "Bot "

                                # Determine uniqueID pass/fail
                                if isError:
                                    passFail = "FAIL "
                                else:
                                    passFail = "PASS "

                                # Compile uniqueID string
                                uniqueID = "".join([passFail,"0x",str("%0.2X"%binValues[6]),str("%0.2X"%binValues[5]),str("%0.2X"%binValues[4]),str("%0.2X"%binValues[3]),"_0x",str("%0.2X"%binValues[2]),str("%0.2X"%binValues[1]),str("%0.2X"%binValues[0]),"70 ",topBot,str("%X"%binValues[7]),"_",str("%01d"%minor)])

                                # Set uniqueID strin as title of TProfile
                                hist.SetTitle(uniqueID)

                                



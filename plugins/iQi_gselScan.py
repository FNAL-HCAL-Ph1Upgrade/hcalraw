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

TDC_MAX = 3
ADC_THRESHOLD = 20
SOI = 3	    # Sample (time slice) of interest
EVENTS_PER_SETTING = 100
MAX_SETTINGS = 13
setting_bins = [1 + n * EVENTS_PER_SETTING for n in range(MAX_SETTINGS + 1)]
SKIP_FIRST = 50
TOTAL_EVENTS = MAX_SETTINGS * EVENTS_PER_SETTING
GOOD_EVENTS_EXPECTED = MAX_SETTINGS * (EVENTS_PER_SETTING - SKIP_FIRST)

global iEvent
iEvent = 0

# Other slot 2 links will be ignored
SLOT2_FIBERS = [0, 1, 2, 3, 4, 5, 6, 7]

# Valid Gsel settings
GSEL_CODES = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
              0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]

def iQi_GselScan(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
    # sanity check
    #print "Entering top of main loop.."
    global iEvent
    iEvent += 1 
    for r, raw in enumerate([raw1, raw2]):
        if not raw:
            continue

	nTsMax = raw[None]["firstNTs"]
        #print "nTsMax = ", nTsMax
	for fedId, dct in sorted(raw.iteritems()):
	    if fedId is None:
                continue
	    h = dct["header"]
	    # Event number 
	    evt = h["EvN"]
            # get the important chunks of raw data
            blocks = dct["htrBlocks"].values()
	    #pprint(blocks)
	    # sanity checks for chunks
	   
	    #print "evt %d\tiEvent %d" % (evt, iEvent)
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
			#if (iEvent % EVENTS_PER_SETTING < SKIP_FIRST): break  # Skip event 		    
			
			
			#print "Event number:", evt
			# ts: time slice
			for (ts, adc) in enumerate(channelData["QIE"]):
			    if nTsMax <= ts:
				break

			    #if channelData.get("TDC"):
		    		#print "TS %d channelData['TDC'] = %s" % (i, channelData["TDC"])

			    
			    # Determine the setting by which bin the event falls into
			    scan_bin = -1
			    for b, lim in enumerate(setting_bins):
				if evt < lim:
				    scan_bin = b - 1
				    break

			    # Ignore events which fall outside the bin range
			    if scan_bin < 0: continue
			    #charge = getADC_charge(GSEL_CODES[scan_bin], adc)
			    charge = getADC_charge(0, adc)
			  
			    #print "Event %d" % (evt)
			    # TS 2
			    savedEventNum = scan_bin * (EVENTS_PER_SETTING - SKIP_FIRST) + (iEvent % EVENTS_PER_SETTING - SKIP_FIRST)
			    
			    if ts == SOI:
				book.fill((evt,charge), "TS_%d_Charge_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (SOI, fedId, crate, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=charge,title="Charge vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  

			    continue
			    
			    book.fill((ts, adc), "ADC_vs_TS_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh), (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax-0.5, nAdcMax-0.5), title="ADC vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d;time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh))
			    
			    if ts == SOI: 
				book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_2D" % SOI, ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="iQi Gsel Scan  TS %d;Event number;ADC" % SOI)  
				book.fill((evt, adc), "TS_%d_ADC_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (SOI, fedId, crate, slot, fib, fibCh), (TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, nAdcMax - 0.5), title="ADC vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;ADC;Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  
				book.fill(evt, "TS_%d_ADC_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_1D" % (SOI, fedId, crate, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=adc,title="ADC vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;ADC;Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  
				
				book.fill((evt, charge), "TS_%d_Charge_vs_EvtNum_2D" % SOI, ( TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, 15000 - 0.5), title="iQi Gsel Scan  TS %d;Event number;Charge [fC]" % SOI)  
				book.fill((evt, charge), "TS_%d_Charge_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (SOI, fedId, crate, slot, fib, fibCh), (TOTAL_EVENTS, nAdcMax), (0.5, -0.5), (TOTAL_EVENTS + 0.5, 15000 - 0.5), title="Charge vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  
				book.fill(evt, "TS_%d_Charge_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_1D" % (SOI, fedId, crate, slot, fib, fibCh), TOTAL_EVENTS, 0.5, TOTAL_EVENTS + 0.5, w=charge,title="Charge vs Event Number  TS %d FED %d Crate %d Slot %d Fib %d Ch %d;Event number;Charge [fC];Counts / bin" % (SOI, fedId, crate, slot, fib, fibCh))  
				
				#if (iEvent % EVENTS_PER_SETTING >= SKIP_FIRST): 		    
				#    book.fill((savedEventNum, adc), "TS_2_ADC_vs_EvtNum_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (fedId, crate, slot, fib, fibCh), ( GOOD_EVENTS_EXPECTED, nAdcMax), (-0.5, -0.5), (GOOD_EVENTS_EXPECTED - 0.5, nAdcMax - 0.5), title="ADC vs Good Event Num (skipping first %d evts per setting)  TS 2 FED %d Crate %d Slot %d Fib %d Ch %d;Good Event number;ADC;Counts / bin" % (SKIP_FIRST, fedId, crate, slot, fib, fibCh))  
				#book.fill((iEvent, adc), "TS_2_ADC_vs_EvtNum_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh), (1300, nAdcMax), (-0.5, -0.5), (1299.5, nAdcMax - 0.5), title="ADC vs Event Number  TS 2 FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Event number;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))  
			    continue

			    #book.fill(adc, "TS_2_ADC_vs_EvtNum_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh), nAdcMax, -0.5, nAdcMax - 0.5, title="ADC vs Event Number  TS 2 FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);Event number;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq)) 
			    
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
			   
			    
			    book.fill((ts, adc), "ADC_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
				      nTsMax, -0.5, nTsMax-0.5,
				      title="ADC vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))

			    book.fill((ts, adc), "ADC_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
				      (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax-0.5, nAdcMax-0.5),
				      title="ADC vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))

			    book.fill((ts, charge), "Charge_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
				      nTsMax, -0.5, nTsMax-0.5,
				      title="Charge vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))

			    book.fill((ts, charge), "Charge_vs_TS_%s_gsel_%d_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, int(GSEL_CODES[scan_bin]), fedId, crate, slot, fib, fibCh),
				      (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
				      title="Charge vs TS  Gsel %d  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (GSEL_CODES[scan_bin], fedId, crate, slot, fib, fibCh, eq))
			  
			    
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

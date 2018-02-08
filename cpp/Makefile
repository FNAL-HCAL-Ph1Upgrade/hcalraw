CC=g++
CFLAGS=-Wall -Wextra
ROOTCC=$(shell root-config --cflags)
SO=-shared -fPIC
ROOTLIBS=-L$(shell root-config --libdir) -lCore -lTree -lRIO

# NOTE! LinkDefs must come last
HS1=CDFChunk.h CDFEventInfo.h CDFRunInfo.h cdf.h CDFLinkDef.h
TMP1=tmp1.cpp

HS2=FEDRawData.h FEDRawDataCollection.h cms.h CMSLinkDef.h
CXXS2=FEDRawData.cc
TMP2=tmp2.cpp

RV=$(shell root-config --version | cut -c 1)
ifeq ($(RV), 6)
        RC1=rootcling -f $(TMP1) $(HS1)
        RC2=rootcling -f $(TMP2) $(HS2)
endif
ifeq ($(RV), 5)
        RC1=rootcint -f $(TMP1) -c $(HS1)
        RC2=rootcint -f $(TMP2) -c $(HS2)
        ROOTLIBS=$(ROOTLIBS) -lCint -lNet -lMathCore -lThread
endif

all: mol deadbeef badcoffee cdf.so cms.so

mol: mol.cpp rooter.cpp
	$(CC) $(CFLAGS) $(ROOTCC) $< -o $@ $(ROOTLIBS)

deadbeef: deadbeef.cpp rooter.cpp
	$(CC) $(CFLAGS) $(ROOTCC) $< -o $@ $(ROOTLIBS)

badcoffee: badcoffee.cpp rooter.cpp
	$(CC) $(CFLAGS) $(ROOTCC) $< -o $@ $(ROOTLIBS)

cdf.so: $(HS1)
	$(RC1)
	$(CC) $(CFLAGS) $(SO) $(ROOTCC) $(TMP1) -o $@ $(ROOTLIBS)

cms.so: $(HS2) $(CXXS2)
	$(RC2)
	$(CC) $(CFLAGS) $(SO) $(ROOTCC) $(CXXS2) $(TMP2) -o $@ $(ROOTLIBS)

clean:
	$(shell rm -f `cat .gitignore`)

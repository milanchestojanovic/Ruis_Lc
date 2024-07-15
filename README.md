To setup the code:
=====

```
cmsrel CMSSW_13_2_4
cd CMSSW_13_2_4/src
cmsenv
git clone --branch CMSSW_13X_2023data git@github.com:your-username/LambdaC.git
scram b -j4
cd dfinder
```

To run data:
=====

```
cmsRun forest_miniAOD_112X_DATA_wDfinder.py 
```

To run MC:
=====

```
cmsRun forest_miniAOD_112X_MC_wDfinder.py
```

Note, to run full event selection you may need to checkout HeavyIon package. You can see more here:
https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideHeavyIonCentrality#PbPb_Data_2023


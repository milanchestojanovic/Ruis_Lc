### HiForest Configuration
# Input: miniAOD
# Type: mc

import FWCore.ParameterSet.Config as cms
process = cms.Process('HiForest')

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool( True ),
)

###############################################################################

# HiForest info
#process.load("HeavyIonsAnalysis.EventAnalysis.HiForestInfo_cfi")
#process.HiForestInfo.info = cms.vstring("HiForest, miniAOD, 112X, mc")

# import subprocess, os
# version = subprocess.check_output(
#     ['git', '-C', os.path.expandvars('$CMSSW_BASE/src'), 'describe', '--tags'])
# if version == '':
#     version = 'no git info'
# process.HiForestInfo.HiForestVersion = cms.string(version)

###############################################################################

# input files
process.source = cms.Source("PoolSource",
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck"),
    fileNames = cms.untracked.vstring(
        "/store/relval/CMSSW_11_2_0/RelValPyquen_DiJet_pt80to120_2760GeV_2021/MINIAODSIM/PU_112X_mcRun3_2021_realistic_HI_v13-v1/10000/192f6a7f-b549-49e2-b353-fde88b9b78ce.root"
        ),
    )

# number of events to process, set to -1 to process all events
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10)
    )

###############################################################################

# load Global Tag, geometry, etc.
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
#process.load("CondCore.CondDB.CondDB_cfi")


from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '132X_dataRun3_Prompt_v4', '')
#process.HiForestInfo.GlobalTagLabel = process.GlobalTag.globaltag

###############################################################################

# Define centrality binning
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '132X_dataRun3_Express_v4', '')
process.GlobalTag.snapshotTime = cms.string("9999-12-31 23:59:59.000")
process.GlobalTag.toGet.extend([
    cms.PSet(record = cms.string("HeavyIonRcd"),
        tag = cms.string("CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run3v1302x04_offline_Nominal"),
        connect = cms.string("sqlite_file:CentralityTable_HFtowers200_DataPbPb_periHYDJETshape_run3v1302x04_offline_Nominal.db"),
        label = cms.untracked.string("HFtowers")
        ),
    ])

process.load("RecoHI.HiCentralityAlgos.CentralityBin_cfi")
process.centralityBin.Centrality = cms.InputTag("hiCentrality")
process.centralityBin.centralityVariable = cms.string("HFtowers")

###############################################################################

# root output
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("HiForestMiniAOD.root")
)

# # edm output for debugging purposes
# process.output = cms.OutputModule(
#     "PoolOutputModule",
#     fileName = cms.untracked.string('HiForestEDM.root'),
#     outputCommands = cms.untracked.vstring('keep *',)
#     )
# process.output_path = cms.EndPath(process.output)

###############################################################################


# event analysis
process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')

process.load('HeavyIonsAnalysis.EventAnalysis.collisionEventSelection_cff')
process.load('HeavyIonsAnalysis.EventAnalysis.hffilter_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.clusterCompatibilityFilter_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hievtanalyzer_data_cfi')
process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')


process.eventFilter = cms.Sequence(
    process.phfCoincFilter2Th4 *
    process.primaryVertexFilter *
    process.clusterCompatibilityFilter
)

from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel
process.hltfilter = hltHighLevel.clone(
    HLTPaths = [
        #"HLT_HIZeroBias_v4",
        "HLT_HIMinimumBias*",
    ]
)


# process.load('HeavyIonsAnalysis.EventAnalysis.hltanalysis_cfi')
# process.load('HeavyIonsAnalysis.EventAnalysis.particleFlowAnalyser_cfi')
# process.load('HeavyIonsAnalysis.EventAnalysis.hievtanalyzer_mc_cfi')
# process.load('HeavyIonsAnalysis.EventAnalysis.skimanalysis_cfi')
################################
# electrons, photons, muons
#process.load('HeavyIonsAnalysis.EGMAnalysis.ggHiNtuplizer_cfi')
#process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")
################################
# jets
#process.load('HeavyIonsAnalysis.JetAnalysis.akCs4PFJetSequence_pponPbPb_mc_cff')
################################
# tracks
#process.load("HeavyIonsAnalysis.TrackAnalysis.TrackAnalyzers_cff")

#process.load("HeavyIonsAnalysis.MuonAnalysis.unpackedMuons_cfi")
#process.load("HeavyIonsAnalysis.MuonAnalysis.hltMuTree_cfi")


# main forest sequence
"""
process.forest = cms.Path(
    process.HiForestInfo +
    # process.hltanalysis +
    process.trackSequencePbPb +
    # process.particleFlowAnalyser +
    process.hiEvtAnalyzer +
    process.ggHiNtuplizer +
    process.akCs4PFJetAnalyzer +
    process.unpackedMuons +
    process.hltMuTree
    )
"""


addCandidateTagging = False

if addCandidateTagging:
    process.load("HeavyIonsAnalysis.JetAnalysis.candidateBtaggingMiniAOD_cff")
    
    from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
    updateJetCollection(
        process,
        jetSource = cms.InputTag('slimmedJets'),
        jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'None'),
        btagDiscriminators = ['pfCombinedSecondaryVertexV2BJetTags', 'pfDeepCSVDiscriminatorsJetTags:BvsAll', 'pfDeepCSVDiscriminatorsJetTags:CvsB', 'pfDeepCSVDiscriminatorsJetTags:CvsL'], ## to add discriminators,
        btagPrefix = 'TEST',
    )
    
    process.updatedPatJets.addJetCorrFactors = False
    process.updatedPatJets.discriminatorSources = cms.VInputTag(
        cms.InputTag('pfDeepCSVJetTags:probb'),
        cms.InputTag('pfDeepCSVJetTags:probc'),
        cms.InputTag('pfDeepCSVJetTags:probudsg'),
        cms.InputTag('pfDeepCSVJetTags:probbb'),
    )
    
    process.akCs4PFJetAnalyzer.jetTag = "updatedPatJets"

    #process.forest.insert(1,process.candidateBtagging*process.updatedPatJets)

    process.akCs4PFJetAnalyzer.addDeepCSV = True

#customisation
#process.akCs4PFJetAnalyzer.doLifeTimeTagging = False

#########################
# Event Selection -> add the needed filters here
#########################

#process.load('HeavyIonsAnalysis.EventAnalysis.collisionEventSelection_cff')
#process.pclusterCompatibilityFilter = cms.Path(process.clusterCompatibilityFilter)
#process.pprimaryVertexFilter = cms.Path(process.primaryVertexFilter)
#process.pAna = cms.EndPath(process.skimanalysis)

# Add PbPb event plane
process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.load("RecoHI.HiEvtPlaneAlgos.hiEvtPlaneFlat_cfi")


process.hiEvtPlane.trackTag = cms.InputTag("packedPFCandidates")
process.hiEvtPlane.vertexTag = cms.InputTag("offlineSlimmedPrimaryVertices")
process.hiEvtPlaneFlat.vertexTag = cms.InputTag("offlineSlimmedPrimaryVertices")

process.hiEvtPlane.loadDB = cms.bool(True)
process.hiEvtPlaneFlat.centralityVariable=process.hiEvtPlane.centralityVariable
process.hiEvtPlaneFlat.vertexTag=process.hiEvtPlane.vertexTag
process.hiEvtPlaneFlat.flatminvtx=process.hiEvtPlane.flatminvtx
process.hiEvtPlaneFlat.flatnvtxbins=process.hiEvtPlane.flatnvtxbins
process.hiEvtPlaneFlat.flatdelvtx=process.hiEvtPlane.flatdelvtx
process.hiEvtPlaneFlat.FlatOrder=process.hiEvtPlane.FlatOrder
process.hiEvtPlaneFlat.CentBinCompression=process.hiEvtPlane.CentBinCompression
process.hiEvtPlaneFlat.caloCentRef=process.hiEvtPlane.caloCentRef
process.hiEvtPlaneFlat.caloCentRefWidth=process.hiEvtPlane.caloCentRefWidth


process.CondDB.connect = "sqlite_file:HeavyIonRPRcd_offline.db"
process.PoolDBESSource = cms.ESSource("PoolDBESSource",
                                       process.CondDB,
                                       toGet = cms.VPSet(cms.PSet(record = cms.string('HeavyIonRPRcd'),
                                                                  tag = cms.string('HeavyIonRPRcd')
                                                                  )
                                                         )
                                      )
process.es_prefer_flatparms = cms.ESPrefer('PoolDBESSource','')
process.evtplane_seq = cms.Sequence(process.hiEvtPlane * process.hiEvtPlaneFlat)
##################



#################### D/B finder ################# 
AddCaloMuon = False 
runOnMC = False ## !!
HIFormat = False 
UseGenPlusSim = False 
# VtxLabel = "unpackedTracksAndVertices"
VtxLabel = "offlineSlimmedPrimaryVertices"
TrkLabel = "packedPFCandidates"
GenLabel = "prunedGenParticles"
useL1Stage2 = True
HLTProName = "HLT"
from Bfinder.finderMaker.finderMaker_75X_cff import finderMaker_75X 
finderMaker_75X(process, AddCaloMuon, runOnMC, HIFormat, UseGenPlusSim, VtxLabel, TrkLabel, GenLabel, useL1Stage2, HLTProName)
process.Dfinder.MVAMapLabel = cms.InputTag(TrkLabel, "MVAValues")
process.Dfinder.makeDntuple = cms.bool(True)
process.Dfinder.tkPtCut = cms.double(1.0) # before fit
process.Dfinder.tkEtaCut = cms.double(3.0) # before fit
process.Dfinder.dPtCut = cms.vdouble(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0) # before fit
process.Dfinder.VtxChiProbCut = cms.vdouble(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.05)
process.Dfinder.dCutSeparating_PtVal = cms.vdouble(5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 5., 8., 8.)
process.Dfinder.alphaCut = cms.vdouble(999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 999.0, 0.2, 0.2)
#process.Dfinder.tktkRes_svpvDistanceCut_lowptD = cms.vdouble(0., 0., 0., 0., 0., 0., 0., 0., 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2., 2.)
#process.Dfinder.tktkRes_svpvDistanceCut_highptD = cms.vdouble(0., 0., 0., 0., 0., 0., 0., 0., 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.,2.)
process.Dfinder.svpvDistanceCut_lowptD = cms.vdouble(2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0., 0., 0., 0., 0., 0., 2., 2.)
process.Dfinder.svpvDistanceCut_highptD = cms.vdouble(2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0., 0., 0., 0., 0., 0., 2., 2.)
process.Dfinder.Dchannel = cms.vint32(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1)
process.Dfinder.dropUnusedTracks = cms.bool(True)
process.Dfinder.detailMode = cms.bool(False)

process.dfinder = cms.Path(process.hltfilter * process.eventFilter*process.centralityBin * process.hiEvtPlane * process.hiEvtPlaneFlat * process.DfinderSequence)
#process.dfinder = cms.Path(process.centralityBin * process.DfinderSequence)



###############################
import FWCore.ParameterSet.VarParsing as VarParsing
ivars = VarParsing.VarParsing('analysis')

ivars.maxEvents = -1 
ivars.outputFile='HiForestMiniAOD.root'
#ivars.inputFiles='file:/afs/cern.ch/work/w/wangj/public/PrmtD0_TuneCP5_HydjetDrumMB_5p02TeV_pythia8/reMiniAOD_MC_PAT_PrmtD0_1120pre9.root'
#ivars.inputFiles='/store/himc/HINPbPbSpring21MiniAOD/LambdaCtoPiLambda1520_pThat-4_TuneCP5_HydjetDrumMB_PtGT10_5p02TeV_Pythia8/MINIAODSIM/mva98_112X_upgrade2018_realistic_HI_v9-v1/240000/107faed7-19cb-495b-9b79-0bb33154e01f.root'
#ivars.inputFiles='/store/himc/HINPbPbSpring21MiniAOD/LambdaCtoPKaonPi_pThat-4_TuneCP5_HydjetDrumMB_PtGT10_5p02TeV_Pythia8/MINIAODSIM/mva98_112X_upgrade2018_realistic_HI_v9-v1/100000/01e174ed-3e85-43fd-915a-38a82b6c9795.root'
#ivars.inputFiles='/store/hidata/HIRun2023A/HIPhysicsRawPrime9/MINIAOD/PromptReco-v2/000/374/668/00000/1a08dcbd-1bf7-41a2-beca-96f91d086d77.root'
#ivars.inputFiles='file:/depot/cms/users/mstojano/files/PbPb2023/miniAOD/reco_run374778_ls0099_streamPhysicsHIPhysicsRawPrime0_StorageManager.root'
ivars.inputFiles='file:/depot/cms/users/mstojano/files/PbPb2023/miniAOD/cd44e980-d445-4a15-9ec1-22b1b7b85253.root'
ivars.parseArguments() # get and parse the command line arguments

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(ivars.inputFiles)
    #fileNames = cms.untracked.vstring(
    #        '/store/hidata/HIRun2023A/HIPhysicsRawPrime1/MINIAOD/PromptReco-v2/000/374/681/00000/cd44e980-d445-4a15-9ec1-22b1b7b85253.root',
    #        '/store/hidata/HIRun2023A/HIPhysicsRawPrime1/MINIAOD/PromptReco-v2/000/374/681/00000/242f4adb-00f3-4ebc-b246-17c130885ef3.root',
    #        '/store/hidata/HIRun2023A/HIPhysicsRawPrime1/MINIAOD/PromptReco-v2/000/374/681/00000/aae1767a-2a77-4430-a403-cb255101d84a.root',
    #        '/store/hidata/HIRun2023A/HIPhysicsRawPrime1/MINIAOD/PromptReco-v2/000/374/681/00000/65cc7197-0c69-4109-8edd-f6a2dec7e6e4.root'
    #)
    # eventsToProcess = cms.untracked.VEventRange('1:236:29748033-1:236:29748033')
    #lumisToProcess = cms.untracked.VLuminosityBlockRange('1:3001-1:3004')
    #eventsToProcess = cms.untracked.VEventRange("1:236:29748218")
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(ivars.maxEvents)
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(ivars.outputFile))


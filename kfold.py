import os 
import time
from sklearn.model_selection import KFold
from EcoNameTranslator import EcoNameTranslator
from Medeina import Web, WebStore 
from Medeina.dataFormatReaders import * 
from inspect import getmembers, isfunction
import specStrings
import msgpack
import pickle
IDTRACKER = 'numericCounter-b2ca94aee362f455a41493a0d28b98bc5074065b0f96cbb95028ead20b1c72ea'
from dfts import parseAll

def constructPhysicalFileMapping():
    mapping = {}
    ultra = []
    for dcts in [getattr(specStrings, o[0])() for o in getmembers(specStrings) if isfunction(o[1])]:
        for dct in dcts:
            ultra.append(dct)
    
    for item in ultra:
        fKey,uId = (item['encoding']['path'].split("/")[-2:])
        uId = uId.split(".")[0]
        name = fKey+"#"+uId
        mapping[name] = item
    
    return mapping

def applyIndividual(fname,include=False):
    if fname == "production#freshwater": return
    usableFiles = set(findAllFoodWebFiles())
    if not include: usableFiles = list(usableFiles - set([fname]))
    path = "C:/Users/davie/Desktop/folds/"
    resultsPath = "C:/Users/davie/Desktop/results/leaveoutfamily/"
    done = set(os.listdir(resultsPath))
    if fname in done: return
    foldPath = path + fname
    # os.mkdir(foldPath)
    # addGivenInteractionsToPath(foldPath,usableFiles)
    fileMapping = constructPhysicalFileMapping()

    dct = fileMapping[fname]
    results = []
    struct = getResultsForSingleApp(dct,foldPath)
    results.append(struct)
    with open(resultsPath+fname,'wb') as f:
        pickle.dump(results,f)

def applyKFold():
    fileMapping = constructPhysicalFileMapping()
    # addGivenInteractionsToPath("C:/Users/davie/Desktop/folds/1",findAllFoodWebFiles())
    usableFiles = list(set(findAllFoodWebFiles()) - set(exceptedFiles()))
    kf = KFold(n_splits=50,shuffle=True)
    path = "C:/Users/davie/Desktop/folds/"
    resultsPath = "C:/Users/davie/Desktop/results/"
    foldNum = 1
    for train_index, test_index in kf.split(usableFiles):
        foldPath = path + str(foldNum)
        os.mkdir(foldPath)
        trainFolders = [usableFiles[n] for n in train_index]
        trainFolders = [*trainFolders,*exceptedFiles()]
        addGivenInteractionsToPath(foldPath,trainFolders)
        testFolders = [fileMapping[usableFiles[n]] for n in test_index]
        results = []
        for dct in testFolders:
            generated,actual,allPossible = getResultsForSingleApp(dct,foldPath)
            results.append((generated,actual,allPossible))

        with open(resultsPath+str(foldNum),'wb') as f:
            pickle.dump(results,f)
        break
        
def processFoldResults(results):
    return len(results)

def getResultsForSingleApp(dct,foldPath):
    fileLoc = dct['encoding']['path']
    w = Web(foldPath)
    actual = list(map(lambda x: (x[0],x[1]),parseSpeciesInteractionCells(dct)))
    start_time = time.time()
    result = w.apply(list(set(itertools.chain(*actual))),'family')
    finalTime = (time.time() - start_time)
    allInteractions = parseAll(dct)
    done = result.done 
    notDone = result.notDone 
    translatedTime = result.endTime
    return result.to_list_with_original(),actual,allInteractions,finalTime,translatedTime,done,notDone

def addGivenInteractionsToPath(path,trainFolders):
    all_datasets = {}
    all_web = {}
    all_links = {}
    all_taxaExceptions = {}
    all_stringNames = {}
    all_taxaIndex = {}
    counter = 0
    all_web[IDTRACKER] = 1
    for item in trainFolders:
        datasets,web,links,taxaExceptions,stringNames,taxaIndex = loadFromFile(item)

        orgDatasetLen = len(all_datasets)
        orgLinkLen = len(all_links)
        orgStringNameLen = len(all_stringNames)

        mergeDatasets(all_datasets,datasets)
        mergeLinks(all_links,links,orgDatasetLen)
        mappingOldIdToNew = mergeStringNames(all_stringNames,stringNames,all_taxaIndex,taxaIndex)
        mergeWeb(all_web,web,mappingOldIdToNew,orgLinkLen)
        mergeExceptions(all_taxaExceptions,taxaExceptions)
    
    writeObjToDateStore(path,'datasets',all_datasets)
    writeObjToDateStore(path,'interactionWeb',all_web)
    writeObjToDateStore(path,'links',all_links)
    writeObjToDateStore(path,'reorderedTaxaInteractions',all_taxaExceptions)
    writeObjToDateStore(path,'speciesStringNames',all_stringNames)
    writeObjToDateStore(path,'taxonomicIndex',all_taxaIndex)

def addExceptedDataStores(foldPath,filenames):
    addGivenInteractionsToPath(foldPath,filenames)

def mergeDatasets(allDatasets,new):
    oLen = len(allDatasets)
    for key,val in new.items():
        if key+oLen in allDatasets: 
            print("Dataset error!")
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            raise ValueError("TAKEN ID!!!!!!!!")
        allDatasets[key+oLen] = val 
    
def mergeWeb(all_,new,mappingOldIdToNew,orgLinkLen):
    for pred in new:
        if isinstance(new[pred],int): continue
        for prey in new[pred]:
            adjustedPredID = mappingOldIdToNew[pred]
            adjustedPreyID = mappingOldIdToNew[prey]
            adjustedLinks = list(map(lambda x: x+orgLinkLen,new[pred][prey]))

            if adjustedPredID not in all_:
                all_[adjustedPredID] = {}
            
            if adjustedPreyID not in all_[adjustedPredID]:
                all_[adjustedPredID][adjustedPreyID] = []
            
            all_[adjustedPredID][adjustedPreyID].extend(adjustedLinks)
    

def mergeLinks(allLinks,new,offsetDid):
    oLen = len(allLinks)
    for key,val in new.items():
        if key+oLen in allLinks:
            print("Link error!")
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            raise ValueError("TAKEN ID!!!!!!!!")
        allLinks[key+oLen] = val 
        if 'dId' in allLinks[key+oLen]: 
            allLinks[key+oLen]['dId'] += offsetDid

def mergeExceptions(all_,new):
    return {}

def mergeStringNames(allStringNames,new,allTaxa,newTaxa):
    mappingOldIdToNew = {}
    # oLen = len(allStringNames)
    vs = allStringNames.values()
    lastTakenStringId = 0
    if len(vs) > 0: 
        lastTakenStringId = max(allStringNames.values()) 
    counter = 1
    for key,val in new.items():
        if key in allStringNames: 
            mappingOldIdToNew[val] = allStringNames[key]
            continue
        allStringNames[key] = lastTakenStringId+counter 
        allTaxa[lastTakenStringId+counter] = newTaxa[val]
        mappingOldIdToNew[val] = lastTakenStringId+counter 
        counter += 1
    return mappingOldIdToNew

def loadFromFile(filename):
    base = "C:/Users/davie/Desktop/validation"
    datasets = retrieveObjFromStore(base+"/"+filename,'datasets')
    web = retrieveObjFromStore(base+"/"+filename,'interactionWeb')
    links = retrieveObjFromStore(base+"/"+filename,'links')
    exceptions = retrieveObjFromStore(base+"/"+filename,'reorderedTaxaInteractions')
    stringNames = retrieveObjFromStore(base+"/"+filename,'speciesStringNames')
    taxaIndex = retrieveObjFromStore(base+"/"+filename,'taxonomicIndex')

    return datasets,web,links,exceptions,stringNames,taxaIndex

def findAllFoodWebFiles():
    return os.listdir("C:/Users/davie/Desktop/validation")

def exceptedFiles():
    return ['InsightPending#ATLANTIC_frugivory','production#2018GlobAL']

def applySingleFold():
    pass

def writeObjToDateStore(directory,name,obj):
    with open(f'{directory}/{name}','wb') as fh:
        packed = msgpack.packb(obj)
        fh.write(packed)

def retrieveObjFromStore(directory,name):
    with open(f'{directory}/{name}','rb') as fh:
        byteData = fh.read()
        existing = msgpack.unpackb(byteData,strict_map_key=False)
    
    return existing

# applyIndividual('validation#Coweeta17')
# applyIndividual('validation#reef_spnames')
# applyIndividual('validation#leatherBritain')
# applyKFold()
usableFiles = list(set(findAllFoodWebFiles()) - set(exceptedFiles()))

for item in usableFiles:
    applyIndividual(item)


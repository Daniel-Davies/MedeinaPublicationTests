
import pathlib
import pandas as pd
import re
import itertools

def parseAll(parsedSpecificationString):
    graphType = parsedSpecificationString['encoding']
    stringPairs = collectFromAppropriateHandlerMethod(graphType)
    return stringPairs

def collectFromAppropriateHandlerMethod(graphType):
    interactionFormat = graphType['interactionFormat']
    dataPath = graphType['path']
    stringPairs = []
    if interactionFormat == "pair":
        stringPairs = formatPairData(graphType)
    elif interactionFormat == "matrix":
        stringPairs = formatMatrixData(graphType)
    
    return stringPairs
    
def formatPairData(graphType):
    try:
        df = readContentAsDataFrame(graphType['path'])
        predators = df[graphType['head']].values.tolist()
        prey = df[graphType['tail']].values.tolist()
        consumableData = list(zip(predators,prey))
        return consumableData
    except Exception as e:
        print(str(e))
        return []

def formatMatrixData(graphType):
    df = readContentAsDataFrame(graphType['path'],header=None)
    nameDepth = graphType.get('nameDepth',100)  
    headingCoord = parseStringToTuple(graphType.get('headingCorner','(1,1)'))
    dataCoord = parseStringToTuple(graphType.get('dataCorner','(2,2)'))
    dataMatrix = handleData(dataCoord, df).values.tolist()
    predators = extractPredatorsFromFile(dataCoord,headingCoord,df,nameDepth)
    prey = extractPreyFromFile(dataCoord,headingCoord,df,nameDepth)
    return createPairDataFromMatrix(dataMatrix,predators,prey)

def extractPredatorsFromFile(dataCoord,headingCoord,df,nameDepth):
    predators = handlePredatorData(dataCoord,headingCoord,df).values.tolist()
    predators = list(map(lambda x: x[:nameDepth], predators))
    predators = list(map(safeJoin,predators))
    return predators

def extractPreyFromFile(dataCoord,headingCoord,df,nameDepth):
    prey = handlePreyData(dataCoord,headingCoord,df).values.tolist()
    prey = crushMultiRow(prey)
    prey = list(map(lambda x: x[:nameDepth], prey))
    prey = list(map(safeJoin,prey))
    return prey

def crushMultiRow(multiHeadings):
    return list(zip(*multiHeadings))

def safeJoin(listOfNames):
    filterNone = list(filter(lambda x: isinstance(x,str), listOfNames))
    return " ".join(filterNone)

def handleData(dataCoord,df):
    x,y = dataCoord
    return df.iloc[y:,x:]

def handlePredatorData(dataCoord, headingCoord, df):
    start = headingCoord[0]
    length = dataCoord[0] - headingCoord[0]

    offsetY = dataCoord[1] - headingCoord[1]
    return df.iloc[headingCoord[1]+offsetY:,start:start+length]

def handlePreyData(dataCoord, headingCoord, df):
    start = headingCoord[1]
    length = dataCoord[1] - headingCoord[1]

    offsetX = dataCoord[0] - headingCoord[0]
    return df.iloc[start:start+length,headingCoord[0]+offsetX:]

def parseStringToTuple(coord):
    if not bool(re.match('^\([\d]+,[\d]+\)$',coord)):
        raise ValueError("Incorrectly formatted index rows!")
    
    coord = coord.strip(")").strip("(")
    x,y = coord.split(",")
    return (int(x)-1,int(y)-1)

def createPairDataFromMatrix(dataMatrix,predators,prey):
    assert len(predators) == len(dataMatrix)
    assert len(prey) == len(dataMatrix[0])
    consumableData = []
    for i in range(len(predators)):
        for j in range(len(prey)):
            consumableData.append((predators[i],prey[j]))
    return consumableData

def readContentAsDataFrame(dataPath,header='infer'):
    fileType = (pathlib.Path(dataPath).suffix[1:]) 
    data = []
    if fileType == 'csv':
        data = pd.read_csv(dataPath,engine='python',header=header)
    elif 'xls' in fileType:
        data = pd.read_excel(dataPath,header=header)
        data = data.dropna(axis=1, how='all')

    data = data.dropna(axis=1, how='all')
    data = data.dropna(axis=0, how='all')
    return data

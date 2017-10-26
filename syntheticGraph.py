#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:41:47 2017

@author: fubao
"""

import os
import networkx as nx

from collections import defaultdict
from random import randint
from random import choice
import sys
sys.path.append("../")

from hierarchicalQueryPython.CommonFiles.commons import writeListRowToFileWriterTsv
from hierarchicalQueryPython.CommonFiles.commons import writeListToFileWriterTsv


#from hierarchicalQueryPython.graphCommon import readCiscoDataGraph


#generate a random graph;  synthetic graph
#number of nodes . |V|
#number of edge |E|
#numer of hierarchical level node types  ;
#number of  nodes inherited among nodes
#

from enum import Enum

class GRAPHNODETYPE(Enum):
    TYPE0HIER = 0             #hierarchical nodes with subcategory, category     30%
    TYPE1HIER = TYPE0HIER+1   #hierarchical nodes with subcategory, category      30%
    TYPE0INHERIT = TYPE0HIER + 2   #node that inheritance among hierarchical nodes 10%
    TYPE1INHERIT = TYPE0HIER + 3   #node that inheritance among hierarchical nodes 10%                               
    TYPE0GENERIC = TYPE0HIER + 4   #5%
    TYPE1GENERIC = TYPE0HIER + 5   #10%
    TYPE2GENERIC = TYPE0HIER + 6   #10%
    
    
class syntheticGraph(object):
    
    def __init__(self):
        self.totalNodeNumber  = 1000000   #1000    #10000000      #10million
       # self.totalEdgeNumber  = 50000000      #50million;  node number decided by edge number
        self.nodeIdToTypeMap = defaultdict()         #node Id to node type Id
        self.nodeIdToNameMap = defaultdict()         #node Id to node name

        self.nodeTypeNumberPartioLst = [0.3, 0.3, 0.1, 0.1, 0.1, 0.05, 0.05]

    def judgeEdgeHierLevel(self, nodeIdSrc, nodeIdDst):
        '''
        judge whether two nodes are possibly to hierarchical node
        '''
        
        if (self.nodeIdToTypeMap[nodeIdSrc] == GRAPHNODETYPE.TYPE0HIER.value and self.nodeIdToTypeMap[nodeIdDst] ==  GRAPHNODETYPE.TYPE0HIER.value) or \
           (self.nodeIdToTypeMap[nodeIdSrc] == GRAPHNODETYPE.TYPE1HIER.value and self.nodeIdToTypeMap[nodeIdDst] ==  GRAPHNODETYPE.TYPE1HIER.value):
            return True
        else:
            return False
        
    
    def generateHierNode(self, startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo):
        '''
        generate node Info
        Input:
        startNodeId: the start Id for node,  including it
        nodeTypeNameLst: the node type name
        nodeNumberLst: the node number for each type in nodeTypeNameLst
        '''
       
        for i, nodeNumber in enumerate(nodesNumberLst):
            for j in range(0, nodeNumber):
                nodeId = startNodeId + j
                nodeName = nodeTypeLst[i].name +"_" + str(nodeId) + "_+++" + str(nodeTypeLst[i].value)
                
                if nodeId <= self.totalNodeNumber:
                    #write into list
                    listNodeInfo.append([nodeName, nodeId])
                    self.nodeIdToTypeMap[nodeId] = nodeTypeLst[i].value 
                    self.nodeIdToNameMap[nodeId] = nodeName
                
            startNodeId = startNodeId + nodeNumber
        return startNodeId, listNodeInfo


    def generateEdgeListVersion1(self, maximumDegree):
        '''
        version 1: total random of hierarchical level 
        generate edge for nodes in the graph
        '''
        #edge hierarchical level same, higher, lower
        
        edgeList = []
        hierarchiLevelList = ['same', 'higher', 'lower']
        listNodes = list(self.nodeIdToTypeMap.keys())
        pairEdgeMap = defaultdict()               #used for checking whether pair edge is created before
        for nodeId in listNodes:
            #generate edge
            number = randint(0, maximumDegree)
            for i in range(0, number):
                #randomly select a node
                selectNodeId = choice(listNodes)
                if selectNodeId != nodeId:
                    #construct edge
                    if nodeId != selectNodeId:
                        if self.judgeEdgeHierLevel(nodeId, selectNodeId):     #hierarchical node
                            #print ("enter here: ", self.nodeIdToTypeMap[nodeId], self.nodeIdToTypeMap[selectNodeId])
                            #select hierarchical node level 
                            hierLevel = choice(hierarchiLevelList)
                            if (nodeId, selectNodeId) not in pairEdgeMap:
                                edgeList.append([nodeId, selectNodeId, hierLevel])
                                if hierLevel == "higher":
                                    edgeList.append([selectNodeId, nodeId, "lower"])
                                elif hierLevel == "lower":
                                    edgeList.append([selectNodeId, nodeId, "higher"])
                                else:
                                    edgeList.append([selectNodeId, nodeId, hierLevel])

                                pairEdgeMap[(nodeId, selectNodeId)] = 1
                                pairEdgeMap[(selectNodeId, nodeId)] = 1
                        else:
                            #print ("enter here2 : ", self.nodeIdToTypeMap[nodeId], self.nodeIdToTypeMap[selectNodeId])
                            hierLevel = hierarchiLevelList[0]
                            if (nodeId, selectNodeId) not in pairEdgeMap:
                                edgeList.append([nodeId, selectNodeId, hierLevel])
                                edgeList.append([selectNodeId, nodeId, hierLevel])
                                pairEdgeMap[(nodeId, selectNodeId)] = 1
                                pairEdgeMap[(selectNodeId, nodeId)] = 1
                                
        return edgeList
        
    
    
    def generateEdgeListVersion2(self, maximumDegree):
        '''
        version 2: select part of  hierarchical level nodes constructed as hierarchical nodes; 
        other nodes are constructed randomly
        generate edge for nodes in the graph
        '''
        #edge hierarchical level same, higher, lower
        
        edgeList = []
        hierarchiLevelList = ['same', 'higher', 'lower']
        listNodes = list(self.nodeIdToTypeMap.keys())
        pairEdgeMap = defaultdict()               #used for checking whether pair edge is created before
        
        ratioPart = [0.01]*10    #ratio of hierarchical node
        nodeLst0HierarchiLevel = []         #nodes with GRAPHNODETYPE.TYPE0HIER type
        nodeLst1HierarLevel = []            # nodes with GRAPHNODETYPE.TYPE1HIER type
        otherNodeLst = []              #except from nodeLst0HierarchiLevel and nodeLst1HierarLevel
        for node, nodetype in nodeIdToTypeMap.items():
            if nodeType == GRAPHNODETYPE.TYPE0HIER.value:
                nodeLst0HierarchiLevel.append(node)
            if nodeType == GRAPHNODETYPE.TYPE1HIER.value:
                nodeLst1HierarLevel.append(node)
                
        #get first part hiearchical node
        for i in ratioPart:
            nodeLst = nodeLst0HierarchiLevel[0: int(ratioPart[0]*len(nodeLst0HierarchiLevel))]
            
            tmp = nodeLst
            
            for i, ndId in enumerate(nodeLst):
                #random select node from nodeLst
                if i < len(nodeLst)-1:
                    selectNd = nodeLst[i]         #choice(nodeLst)
                    edgeList.append([selectNodeId, ndId, "lower"])
                    edgeList.append([ndId, selectNodeId, "higher"])
                
                #remove from nodeLst
                number = randint(0, maximumDegree-1)
                    for i in range(0, number):
                                
        return edgeList
        
    
    def generateAllNodeInfo(self, outFileNodeInfo, outFileEdgeList):
        '''
        generate all node info file
        '''
        
        listNodeInfo = []
        #generate hierarchical node info, label + ID
        startNodeId = 1
        nodeTypeLst = [GRAPHNODETYPE.TYPE0HIER, GRAPHNODETYPE.TYPE1HIER]
        nodesNumberLst = [int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[0]), int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[1])]                        #30%
        startNodeId, listNodeInfo = self.generateHierNode(startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo)
        print ("generateAllNodeInfo listNodeInfo 1:  ", len(listNodeInfo))
        
        # generate info of node that inherited 
        nodeTypeLst = [GRAPHNODETYPE.TYPE0INHERIT, GRAPHNODETYPE.TYPE1INHERIT]
        nodesNumberLst = [int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[2]), int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[3])]                        #20%
        startNodeId, listNodeInfo = self.generateHierNode(startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo)        
        print ("generateAllNodeInfo listNodeInfo  2: ", len(listNodeInfo))

                
        # generate info of node that inherited 
        nodeTypeLst = [GRAPHNODETYPE.TYPE0GENERIC, GRAPHNODETYPE.TYPE1GENERIC, GRAPHNODETYPE.TYPE2GENERIC]
        nodesNumberLst = [int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[4]), int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[5]), int(self.totalNodeNumber * self.nodeTypeNumberPartioLst[6])]                        #20%
        startNodeId, listNodeInfo = self.generateHierNode(startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo)
        print ("generateAllNodeInfo listNodeInfo  3: ", len(listNodeInfo))
          
        #get edge list file
        maximumDegree = 10
        edgeList = self.generateEdgeListVersion1(maximumDegree)
        
        print ("generateAllNodeInfo edgeList  : ", len(edgeList))
        
        #write into file
        os.remove(outFileNodeInfo) if os.path.exists(outFileNodeInfo) else None
        os.remove(outFileEdgeList) if os.path.exists(outFileEdgeList) else None
        writeListToFileWriterTsv(outFileNodeInfo, listNodeInfo, "\t")
        writeListToFileWriterTsv(outFileEdgeList, edgeList, "\t")
                
        
        
          
if __name__ == "__main__":
    syntheticGraphObj = syntheticGraph()
    outFileNodeInfo = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraphNodeInfo.tsv"
    outFileEdgeList = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraphEdgeListInfo.tsv"
    syntheticGraphObj.generateAllNodeInfo(outFileNodeInfo, outFileEdgeList)
    

        
    
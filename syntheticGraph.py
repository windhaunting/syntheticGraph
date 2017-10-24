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
    TYPE0HIER = 0             #hierarchical nodes with subcategory, category     20%
    TYPE1HIER = TYPE0HIER+1   #hierarchical nodes with subcategory, category      20%
    TYPE0INHERIT = TYPE0HIER + 2   #node that inheritance among hierarchical nodes 10%
    TYPE1INHERIT = TYPE0HIER + 3   #node that inheritance among hierarchical nodes 10%                               
    TYPE0GENERIC = TYPE0HIER + 4   # 10%
    TYPE1GENERIC = TYPE0HIER + 5   #10%
    TYPE2GENERIC = TYPE0HIER + 6   #20%
    
    
class syntheticGraph(object):
    
    def __init__(self):
        self.totalNodeNumber  = 1000    #10000000      #10million
       # self.totalEdgeNumber  = 50000000      #50million;  node number decided by edge number
        self.nodeIdToTypeMap = defaultdict()         #node Id to node type Id
        self.nodeIdToNameMap = defaultdict()         #node Id to node name


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
                
                #write into list
                listNodeInfo.append([nodeName, nodeId])
                self.nodeIdToTypeMap[nodeId] = nodeName
                self.nodeIdToNameMap[nodeId] = nodeTypeLst[i].value
                
                
            startNodeId = startNodeId + nodeNumber
        return startNodeId, listNodeInfo


    def generateEdgeList(self, maximumDegree):
        '''
        generate edge for nodes in the graph
        '''
        #edge hierarchical level same, higher, lower
        
        edgeList = []
        hierarchiLevelList = ['same', 'higher', 'lower']
        listNodes = self.nodeIdToTypeMap.keys()
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
                            #select hierarchical node level 
                            hierLevel = choice(hierarchiLevelList)
                            edgeList.append([nodeId, selectNodeId, hierLevel])
                        else:
                            hierLevel = hierarchiLevelList[0]
                            edgeList.append([nodeId, selectNodeId, hierLevel])
        return edgeList
        
    def generateAllNodeInfo(self, outFileNodeInfo, outFileEdgeList):
        '''
        generate all node info file
        '''
        
        listNodeInfo = []
        #generate hierarchical node info, label + ID
        startNodeId = 1
        nodeTypeLst = [GRAPHNODETYPE.TYPE0HIER, GRAPHNODETYPE.TYPE1HIER]
        nodesNumberLst = [int(self.totalNodeNumber * 0.2), int(self.totalNodeNumber * 0.2)]                        #20%
        startNodeId, listNodeInfo = self.generateHierNode(startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo)
        print ("generateAllNodeInfo listNodeInfo 1:  ", len(listNodeInfo))
        
        # generate info of node that inherited 
        nodeTypeLst = [GRAPHNODETYPE.TYPE0INHERIT, GRAPHNODETYPE.TYPE1INHERIT]
        nodesNumberLst = [int(self.totalNodeNumber * 0.1), int(self.totalNodeNumber * 0.1)]                        #20%
        startNodeId, listNodeInfo = self.generateHierNode(startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo)        
        print ("generateAllNodeInfo listNodeInfo  2: ", len(listNodeInfo))

                
        # generate info of node that inherited 
        nodeTypeLst = [GRAPHNODETYPE.TYPE0GENERIC, GRAPHNODETYPE.TYPE1GENERIC, GRAPHNODETYPE.TYPE2GENERIC]
        nodesNumberLst = [int(self.totalNodeNumber * 0.1), int(self.totalNodeNumber * 0.1), int(self.totalNodeNumber * 0.2)]                        #20%
        startNodeId, listNodeInfo = self.generateHierNode(startNodeId, nodeTypeLst, nodesNumberLst, listNodeInfo)
        print ("generateAllNodeInfo listNodeInfo  3: ", len(listNodeInfo))
          
        #get edge list file
        edgeList = generateEdgeList(outFileNodeInfo, outFileEdgeList)
        
        #write into file
        os.remove(outFile) if os.path.exists(outFile) else None

        writeListToFileWriterTsv(outFile, listNodeInfo, "\t")
        
                

        
          
if __name__ == "__main__":
    syntheticGraphObj = syntheticGraph()
    outFileNodeInfo = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraphNodeInfo.tsv"
    outFileEdgeList = "../../GraphQuerySearchRelatedPractice/Data/syntheticGraph/syntheticGraphEdgeListInfo.tsv"
    syntheticGraphObj.generateAllNodeInfo(outFileNodeInfo, outFileEdgeList)
    

        
    
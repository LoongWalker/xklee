//===-- CallPathManager.cpp -----------------------------------------------===//
//
//                     The KLEE Symbolic Virtual Machine
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#include "CallPathManager.h"

#include "klee/Statistics.h"
#include "CoreStats.h"

#include <map>
#include <vector>
#if LLVM_VERSION_CODE >= LLVM_VERSION(3, 3)
#include "llvm/IR/Function.h"
#else
#include "llvm/Function.h"
#endif

#include "llvm/Support/raw_ostream.h"

#include <iostream>
#include <sstream>
#include <fstream>

using namespace llvm;
using namespace klee;

///

CallPathNode::CallPathNode(CallPathNode *_parent, 
                           Instruction *_callSite,
                           Function *_function)
  : parent(_parent),
    callSite(_callSite),
    function(_function),
    count(0) {
}

void CallPathNode::print() {
  llvm::errs() << "  (Function: " << this->function->getName() << ", "
               << "Callsite: " << callSite << ", "
               << "Count: " << this->count << ")";
  if (parent && parent->callSite) {
    llvm::errs() << ";\n";
    parent->print();
  }
  else llvm::errs() << "\n";
}

///

CallPathManager::CallPathManager() : root(0, 0, 0) {
}

CallPathManager::~CallPathManager() {
  for (std::vector<CallPathNode*>::iterator it = paths.begin(),
         ie = paths.end(); it != ie; ++it)
    delete *it;
}

void CallPathManager::getSummaryStatistics(CallSiteSummaryTable &results) {
  results.clear();

  for (std::vector<CallPathNode*>::iterator it = paths.begin(),
         ie = paths.end(); it != ie; ++it)
    (*it)->summaryStatistics = (*it)->statistics;

  // compute summary bottom up, while building result table
  for (std::vector<CallPathNode*>::reverse_iterator it = paths.rbegin(),
         ie = paths.rend(); it != ie; ++it) {
    CallPathNode *cp = *it;
    cp->parent->summaryStatistics += cp->summaryStatistics;

    CallSiteInfo &csi = results[cp->callSite][cp->function];
    csi.count += cp->count;
    csi.statistics += cp->summaryStatistics;
  }
}


CallPathNode *CallPathManager::computeCallPath(CallPathNode *parent, 
                                               Instruction *cs,
                                               Function *f) {
  //return the exist node, if in recursion
  for (CallPathNode *p=parent; p; p=p->parent)
    if (cs==p->callSite && f==p->function)
      return p;
  
  CallPathNode *cp = new CallPathNode(parent, cs, f);
  paths.push_back(cp);
  return cp;
}

CallPathNode *CallPathManager::getCallPath(CallPathNode *parent, 
                                           Instruction *cs,
                                           Function *f) {
  std::pair<Instruction*,Function*> key(cs, f);
  if (!parent)
    parent = &root;
  
  CallPathNode::children_ty::iterator it = parent->children.find(key);
  if (it==parent->children.end()) {
    CallPathNode *cp = computeCallPath(parent, cs, f);
    parent->children.insert(std::make_pair(key, cp));
    return cp;
  } else {
    return it->second;
  }
}


/*
 *--------------------------------------------------------------------------------------
 *       Class:  CallPathManager
 *      Method:  CallPathManager :: genCallPathNodeGraph
 * Description:  
 *--------------------------------------------------------------------------------------
 */
void CallPathManager::genCallPathNodeGraph(std::ostream *dotFile)
{
    *dotFile <<  "digraph \"CallGrpah\" {\n";
    *dotFile <<  "label = \"CallGraph\";\n" ;

    std::stringstream str;
    for (std::vector<CallPathNode*>::iterator it = paths.begin(),
            ie = paths.end(); it != ie; ++it)
    {
        CallPathNode *cp = *it;
        uint64_t allTime = cp->summaryStatistics.getValue(stats::instructionRealTime) ;
        uint64_t runTime = cp->statistics.getValue(stats::instructionRealTime) ;
        str << "\tNODE" << cp << " [shape=record, label=\"{" << cp->function->getNameStr().c_str()
            << "\n(" << allTime/1000000. << ")" 
            << "\n(" << runTime/1000000. << ")" 
            << "}\"];\n";

        for( CallPathNode::children_ty::iterator cit=cp->children.begin(), cie=cp->children.end(); 
                cit!=cie; cit++ ) {
            //str << "\tNODE" << cp->callSite << " -> " << "NODE" << cit->first.first << "\n";
            //use cp as the mark to keep unique.  
            //cp->callSite could be repeat because of fork
            str << "\tNODE" << cp << " -> " << "NODE" << cit->second << "\n";
        }
#if 0
        cp->print();
        std::cerr << "realtime=" << cp->statistics.getValue(stats::instructionRealTime) 
            << " usertime=" << cp->statistics.getValue(stats::instructionTime) << "\n" ;
        std::cerr << "realtime=" << cp->summaryStatistics.getValue(stats::instructionRealTime) 
            << " usertime=" << cp->summaryStatistics.getValue(stats::instructionTime) << "\n" ;
        std::cerr << "---------------------------------\n\n";
#endif    
    }
    *dotFile << str.str();

    *dotFile <<  "}\n";
    dotFile->flush();
}




/*
 * =====================================================================================
 *
 *       Filename:  xCallGraph.cpp
 *
 *    Description:  get call graph from module, and gen it in dot. it would mark the nodes 
 *                  with different color for focused, covered and uncovered.
 *
 *        Version:  1.0
 *        Created:  12/26/2015 10:17:11 AM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  XiaoQixue (xqx), xiaoqixue_1@163.com
 *   Organization:  
 *
 * =====================================================================================
 */


#include "klee/Common.h"
#include "klee/xPath.h"

#if LLVM_VERSION_CODE > LLVM_VERSION(3, 2)
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#else
#include "llvm/LLVMContext.h"
#include "llvm/Module.h"
#endif

#include "llvm/Pass.h"
#include "llvm/Analysis/CallGraph.h"
#include "llvm/PassAnalysisSupport.h"
#include <llvm/Support/Path.h>

#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>

#include "llvm/Function.h"
#include "llvm/PassManager.h" 

using namespace klee;
using namespace llvm;



/*
 * =====================================================================================
 *        Class:  CGAnalysis: Call Graph Analysis
 *  Description:  Analysis callgraph 
 * =====================================================================================
 */
void CGAnalysis::test()
{
    std::cerr << "CGAnalysis test\n" ;
}

void CGAnalysis::genCallGraph()
{
    PassManager PM;
    //PM.add(new CallGraphPass());
    PM.add(CGPass);
    PM.run(*M);

}



/*
 * =====================================================================================
 *        Class:  CallGraphPass
 *  Description: get callgraph use llvm pass 
 * =====================================================================================
 */
char CallGraphPass::ID;

CallGraphPass::CallGraphPass(std::set<std::string> *fNames) : ModulePass(ID)
{
    llvm::PassRegistry &Registry = *llvm::PassRegistry::getPassRegistry();
    llvm::initializeBasicCallGraphPass(Registry);
    llvm::initializeCallGraphAnalysisGroup(Registry);
    llvm::initializeDominatorTreePass(Registry);

    //focusedFuncs = fNames;
}

bool CallGraphPass::runOnModule(Module &M)
{
    module = &M;
    setFuncNames(&focusedFuncs);

    std::cerr << "CGAnalysis test\n" ;
    CallGraph &CG = getAnalysis<CallGraph>();
    CallGraphNode *cgNode = CG.getRoot();
    //CG.dump();

    Function *fUserMain = NULL;
    for( FuncNameMapTy::iterator i=funcNames.begin(),e=funcNames.end();
            i!=e; i++ ) {
        std::string fn = i->second;
        if( fn == "__user_main" ){
            fUserMain = i->first;
            break;
        }
    }
    if( !fUserMain ) return false;


    *dotFile <<  "digraph \"CallGrpah\" {\n";
    *dotFile <<  "label = \"CallGraph\";\n" ;

    writeNodesFromRoot(CG[fUserMain]);

    *dotFile <<  "}\n";
    dotFile->flush();


}

void CallGraphPass::importFocusedFuncs(std::set<std::string> fFuncs)
{
    //focusedFuncs = fFuncs;
    for( std::set<std::string>::iterator i=fFuncs.begin(), e=fFuncs.end();
            i!=e; i++) {
        focusedFuncs.insert(*i);
    }
}

void CallGraphPass::setFuncNames(std::set<std::string> *fNames)
{
    fNames->insert("__user_main");
    if( fNames==NULL ) return;
    std::cerr << "we have fname szie =" <<  fNames->size();

    for( Module::iterator i = module->begin(), e=module->end();
            i!=e; i++) {
        Function *f = i;
        if( !f ) {
			std::cerr << "***NULL Function***\n";
			continue;
        }
        std::string fname = f->getNameStr();
        //std::cerr << "func: " << fname << "\n";
        std::set<std::string>::iterator it = fNames->find(fname);
        if( it == fNames->end() )
            continue;

        //std::cerr << "focus : " << fname << "\n";
        funcNames[f] = fname;

    }

    std::cerr << "\nwe have fnames map size=" <<  funcNames.size() << "\n";
}

void CallGraphPass::writeNode(CallGraphNode *cgNode)
{
    std::stringstream str;
    Function *cgFunc = cgNode->getFunction();
    //str.format("NODE%x [shape=record, lable={%s}]", cgFunc, cgFunc->getNameStr().c_str());
    if(!cgFunc||!cgFunc->hasName()) return;
    str << "\tNODE" << cgFunc << " [shape=record, label=\"{" << cgFunc->getNameStr().c_str() 
        << "}\"];\n";

    for( CallGraphNode::iterator i = cgNode->begin(), e = cgNode->end();
            i!=e; i++)  {
        CallGraphNode::CallRecord *cr = &*i;
        Function *f = cr->second->getFunction();
        if( funcNames.find(f) != funcNames.end() ) {
            str << "\tNODE" << cgFunc << " -> " << "NODE" << f << "\n";
        }
    }

    writtenFuncs.insert(cgFunc);

    //std::cerr << str.str();
    *dotFile << str.str();
}

void CallGraphPass::writeNodesFromRoot(CallGraphNode *cgRoot)
{
    if( !cgRoot ) {
        std::cerr << "root is NULL";
        return;
    }
    writeNode(cgRoot);

    for( CallGraphNode::iterator i = cgRoot->begin(), e = cgRoot->end();
            i!=e; i++)  {
        CallGraphNode::CallRecord *cr = &*i;
        CallGraphNode *calledNode = cr->second;
        Function *f = calledNode->getFunction();
        if( !f ) continue;
        //std::cerr << f->getNameStr().c_str() << "\n";
        if( funcNames.find(f) != funcNames.end() &&
              writtenFuncs.find(f) == writtenFuncs.end())  {
            writeNodesFromRoot(calledNode);
        } 
    }

}



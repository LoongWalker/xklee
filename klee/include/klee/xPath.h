/*
 * =====================================================================================
 *
 *       Filename:  xPath.h
 *
 *    Description:   path analysis before Symbolic Execution
 *
 *        Version:  1.0
 *        Created:  2014年03月03日 14时49分03秒
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Xiao Qixue (XQX), xiaoqixue_1@163.com
 *   Organization:  Tsinghua University
 *
 * =====================================================================================
 */

#ifndef KLEE_XPATH_H
#define KLEE_XPATH_H

#if LLVM_VERSION_CODE >= LLVM_VERSION(3, 3)
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Module.h"
#else
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Module.h"
#endif

#include "llvm/Analysis/CallGraph.h"
#include "llvm/PassAnalysisSupport.h"
#include "llvm/Support/DataTypes.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Pass.h"


#include "../lib/Core/Common.h"
#include "klee/Config/Version.h"
#include <string>
#include <fstream>
#include <iostream>

#include <vector>

namespace llvm {
class Function;
class Module;
class Instruction;
}

using namespace llvm;

#ifdef __cplusplus
extern "C" {
#endif

	void xPathAnalysisPrint();
    //std::vector<BasicBlock*> getSuccs(BasicBlock *bb) ;

#ifdef __cplusplus
}
#endif
//
namespace klee {

    class FunctionAnalysis {
        sys::Path m_outputDirectory;

        public: 
            FunctionAnalysis();
            void setOutputDir(std::string &OutputDir, const std::string InputFile);
            std::string getOutputFilename(const std::string &filename) ;
            std::ostream *openOutputFile(const std::string &filename) ;

            void getFuncsInModule( llvm::Module *module, std::ostream *of, bool focused=false);
            void getFuncsInModule( const llvm::Module *module, std::ostream *of, bool focused=false);
            void getFuncsInModule( llvm::Module *module, const std::string &outFile, 
                    bool focused=false);
            void getFuncsInModule( const llvm::Module *module, const std::string &outFile, 
                    bool focused=false);
            void getFuncsInModule( const std::string &mFile, const std::string &outFile, 
                    bool focused=false);
            void getFuncsInArchive( llvm::sys::Path &arFile, const std::string &outFile, 
                    bool focused=false);

            void logFocusedFuncs(const std::string &outFile);
            std::set<std::string> getFocusedFuncs() { return focusedFuncNames; }

        private:
            std::set<std::string> focusedFuncNames;
            std::set<std::string> noFocusedFuncNames;

            bool isFocusedFunc(Function *f);
            bool isFocusedFunc(const Function *f);

    };


    class CallGraphPass : public llvm::ModulePass {
        static char ID;
        llvm::Module *module;
        typedef std::map<Function *, std::string> FuncNameMapTy;
        FuncNameMapTy  funcNames;
        std::ostream *dotFile;

        std::set<std::string> focusedFuncs;
        std::set<Function *>  writtenFuncs;

        public:
        CallGraphPass(): ModulePass(ID) {
			llvm::PassRegistry &Registry = *llvm::PassRegistry::getPassRegistry();
			llvm::initializeBasicCallGraphPass(Registry);
			llvm::initializeCallGraphAnalysisGroup(Registry);
			llvm::initializeDominatorTreePass(Registry);
        }
        CallGraphPass(std::set<std::string> *fNames);
		virtual void getAnalysisUsage(llvm::AnalysisUsage &AU) const {
			AU.setPreservesAll();
			AU.addRequired<llvm::CallGraph>();
		}
        virtual bool runOnModule(llvm::Module &M);

        public:
            //import focus function from external of the class
            void importFocusedFuncs(std::set<std::string> fFuncs);
            //set focused funcs to funcNames map
            void setFuncNames(std::set<std::string> *fNames);
            void writeNode(CallGraphNode *cgNode);
            void writeNodesFromRoot(CallGraphNode *cgRoot);
            void setFileStream(std::ostream *of) { dotFile = of; }
    };

    class CGAnalysis {
        static char ID;
        llvm::Module *M;
        CallGraphPass *CGPass;

        public: 
            CGAnalysis(llvm::Module *_m) : M(_m) { CGPass = new CallGraphPass(); };
            void importFocusedFuncs(std::set<std::string> fFuncs) { 
                if(CGPass) CGPass->importFocusedFuncs(fFuncs) ;
            };
            void setFS2CGPass(std::ostream *of) { 
                if(CGPass) CGPass->setFileStream(of);
            };

        public:
            void genCallGraph();
            void test();

    };
}


#endif


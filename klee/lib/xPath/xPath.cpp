
/*
 * =====================================================================================
 *
 *       Filename:  xPath.cpp
 *
 *    Description:  path analysis before symbolic Execution
 *
 *        Version:  1.0
 *        Created:  2014年03月03日 14时52分36秒
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Xiao Qixue (XQX), xiaoqixue_1@163.com
 *   Organization:  Tsinghua University
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


#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/Path.h"
#include <llvm/Support/InstIterator.h>
#include <llvm/Instructions.h>
#include "llvm/Analysis/CallGraph.h"
#include <llvm/Analysis/Interval.h>
#include "llvm/Support/MemoryBuffer.h"
#include <llvm/Bitcode/Archive.h>
//#include <llvm/Support/CFG.h>
//#include <llvm/Support/InstVisitor.h>



#include <sys/stat.h>
#include <unistd.h>

#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>


#include <cerrno>
#include <iomanip>
#include <iterator>




using namespace klee;
using namespace llvm;

#if 0
std::vector<BasicBlock*> getSuccs(BasicBlock *bb) {
  std::vector<BasicBlock*> res;

  for (succ_iterator it = succ_begin(bb), ie = succ_end(bb); it != ie; ++it)
  {
      BasicBlock *bb = it;
      res.push_back(bb);
  }

  return res;
}
#endif


void xPathAnalysisPrint()
{
	//klee_message("---------this is a test in klee lib--------");
	std::cerr << "---------this is a test in klee lib--------\n" ;
    //CGAnalysis *cg = new CGAnalysis(NULL);
    //cg->genCallGraph();

}

FunctionAnalysis::FunctionAnalysis()
{
	std::cerr << "---------FunctisonAnalysis NEW--------\n" ;
}

void FunctionAnalysis::getFuncsInArchive( llvm::sys::Path &arFile, const std::string &outFile, 
        bool focused)
{
    std::string ErrorMsg;
    std::vector<Module *> modules;
    llvm::Archive *ar = llvm::Archive::OpenAndLoad(arFile, getGlobalContext(),&ErrorMsg);
    if( ar == NULL) {
        klee_error("error loading program xPath '%s': %s", arFile.c_str(),
                ErrorMsg.c_str());
    }
    bool bRet = ar->getAllModules(modules, &ErrorMsg);
    if( bRet ) {
        klee_error("error get All module in Archive '%s': %s", arFile.c_str(),
                ErrorMsg.c_str());
    }

    unsigned mcount, fcount, bbcount;
    mcount=fcount=bbcount=0;
    std::ostream *of = openOutputFile(outFile);
    for( std::vector<Module *>::iterator it=modules.begin(); it!=modules.end(); it++)
    {
        Module* m = *it;
        mcount++;
        //std::cerr << "\n" << m->getModuleIdentifier().c_str() ;
        getFuncsInModule(m, of, focused);
    } 

    *of << mcount << " moudles in " << arFile.c_str() << "-----\n";
    delete of;

}

void FunctionAnalysis::getFuncsInModule( const std::string &mFile, const std::string &outFile, 
        bool focused)
{
    std::string ErrorMsg;
    Module *module = NULL;
    OwningPtr<MemoryBuffer> BufferPtr;
    error_code ec=MemoryBuffer::getFileOrSTDIN(mFile.c_str(), BufferPtr);
    if (ec) {
        klee_error("error loading program xPath '%s': %s", mFile.c_str(),
                ec.message().c_str());
    }
    module = getLazyBitcodeModule(BufferPtr.get(), getGlobalContext(), &ErrorMsg);
    if (module) {
        if (module->MaterializeAllPermanently(&ErrorMsg)) {
            delete module;
            module = 0;
        }
    }
    if (!module)
        klee_error("error loading program '%s': %s", mFile.c_str(),
                ErrorMsg.c_str());

    return getFuncsInModule(module, outFile, focused);
}

void FunctionAnalysis::getFuncsInModule(const llvm::Module *module, const std::string &outFile, 
        bool focused)
{
    std::ostream *of = openOutputFile(outFile);
    getFuncsInModule(module, of, focused);
    delete of;
}

void FunctionAnalysis::getFuncsInModule( llvm::Module *module, const std::string &outFile, bool focused)
{
    std::ostream *of = openOutputFile(outFile);
    getFuncsInModule(module, of, focused);
    delete of;
}

void FunctionAnalysis::logFocusedFuncs(const std::string &outFile)
{
    std::cerr << "logFocusedFuncs\n";
    std::ostream *of = openOutputFile(outFile);
    unsigned count = 0;
    for( std::set<std::string>::iterator it=focusedFuncNames.begin(),ie=focusedFuncNames.end();
            it!=ie; it++)
    {
        *of << *it << "\n";
        count++;
    }

    *of << "\n\ntotal number = " << count << "\n";
    delete of;
}

void FunctionAnalysis::getFuncsInModule( llvm::Module *module, std::ostream *of, bool focused)
{
    //std::cerr << "=======getFuncsInModule=======\n";
    unsigned fcount = 0;
    unsigned bbcount = 0;
    unsigned brcount = 0;
    unsigned cicount = 0;
    *of << "======" << module->getModuleIdentifier().c_str() << "=================\n";
    *of <<  std::setiosflags(std::ios::left) << std::setw(50) << "FUNC-NAME" << "\t" 
        << std::setw(10) << "INST-NUM\t" << std::setw(10)<< "BB-NUM\t" << std::setw(10)<< "BR-NUM\n" ;
    for (Module::iterator fit = module->begin(), ie = module->end();
            fit != ie; ++fit) {
        Function *func = fit;
        fcount++;
        std::string name = func->getNameStr();
        if( focused && isFocusedFunc(func)) 
            focusedFuncNames.insert(name);

        name += "(";
        for( int i=0; i<func->arg_size(); i++)
            name+="x,";
        name+=")";

        int bbnum=0;
        int instnum=0;
        int brnum=0;
        for( Function::iterator bbit=func->begin(); bbit != func->end(); ++bbit)
        {
            bbnum++;
            bbcount++;
            BasicBlock *bb = bbit;
            //std::vector<BasicBlock*> bbSuccs = getSuccs(bb);
            llvm::TerminatorInst *ti = bb->getTerminator();
            if( ti->getNumSuccessors() > 1){ brnum++;brcount++; }


            for( llvm::BasicBlock::iterator it = bbit->begin(); it!=bbit->end(); ++it) {
                instnum++;
                if( isa<CallInst>(&*it) ) {
                    cicount++;
                }
            }
        }
        *of << std::setw(30) << name.c_str() << "\t" << std::setw(10) << instnum 
            << "\t" << std::setw(10) << bbnum << "\t" << std::setw(10)<< brnum << "\n";
    }

    *of << "\n\nFunction Number = " << fcount << "\nBasic Block Number = " << bbcount 
        << "\n callinst number = " << cicount 
        << "\nBranch Number = " << brcount << "\n\n\n";

}

void FunctionAnalysis::getFuncsInModule( const llvm::Module *module, std::ostream *of, 
        bool focused)
{
    //std::cerr << "=======getFuncsInModule=======\n";
    unsigned fcount = 0;
    unsigned bbcount = 0;
    unsigned brcount = 0;
    unsigned icount = 0;
    unsigned cicount = 0;
    *of << "======" << module->getModuleIdentifier().c_str() << "=================\n";
    *of <<  std::setiosflags(std::ios::left) << std::setw(50) << "FUNC-NAME" << "\t" 
        << std::setw(10) << "INST-NUM\t" << std::setw(10)<< "BB-NUM\t" << std::setw(10)<< "BR-NUM\n" ;
    for (Module::const_iterator fit = module->begin(), ie = module->end();
            fit != ie; ++fit) {
        const Function *func = fit;
        fcount++;

        std::string name = func->getNameStr();
        if( focused && isFocusedFunc(func)) 
            focusedFuncNames.insert(name);

        name += "(";
        for( int i=0; i<func->arg_size(); i++)
            name+="x,";
        name+=")";

        int bbnum=0;
        int instnum=0;
        int brnum=0;
        for( Function::const_iterator bbit=func->begin(); bbit != func->end(); ++bbit)
        {
            bbnum++;
            bbcount++;
            const BasicBlock *bb = bbit;
            //std::vector<BasicBlock*> bbSuccs = getSuccs(bb);
            const llvm::TerminatorInst *ti = bb->getTerminator();
            if( ti->getNumSuccessors() > 1){ brnum++;brcount++; }


            for( llvm::BasicBlock::const_iterator it = bbit->begin(); it!=bbit->end(); ++it) {
                instnum++;
                icount++;
                if( isa<CallInst>(&*it) ) {
                    cicount++;
                }
            }
        }
        *of << std::setw(30) << name.c_str() << "\t" << std::setw(10) << instnum 
            << "\t" << std::setw(10) << bbnum << "\t" << std::setw(10)<< brnum << "\n";
    }

    *of << "\n\nFunction Numer = " << fcount << "\nBasic Block Numer = " << bbcount 
        << "\n callinst number = " << cicount 
        << "\nBranch Number = " << brcount << "\nInstruction Number = " << icount <<  "\n\n\n";

}

bool FunctionAnalysis::isFocusedFunc(Function *f)
{
    if( f->isDeclaration() )
        return false;

    std::string fName = f->getNameStr();
    if(fName.find("llvm.")!=std::string::npos)
        return false;

    return true;
}
bool FunctionAnalysis::isFocusedFunc(const Function *f)
{
    if( f->isDeclaration() )
        return false;

    std::string fName = f->getNameStr();
    if(fName.find("llvm.")!=std::string::npos)
        return false;

    return true;
}


std::string FunctionAnalysis::getOutputFilename(const std::string &filename) {
    sys::Path path(m_outputDirectory);
    if(!path.appendComponent(filename)) {
        klee_error("cannot create path name for \"%s\"", filename.c_str());
    }

    return path.str();
}

std::ostream *FunctionAnalysis::openOutputFile(const std::string &filename) {
    std::ios::openmode io_mode = std::ios::out | std::ios::trunc 
        | std::ios::binary;
    std::ostream *f;
    std::string path = getOutputFilename(filename);
    f = new std::ofstream(path.c_str(), io_mode);
    if (!f) {
        klee_error("error opening file \"%s\" (out of memory)", filename.c_str());
    } else if (!f->good()) {
        klee_error("error opening file \"%s\".  KLEE may have run out of file descriptors: try to increase the maximum number of open file descriptors by using ulimit.", filename.c_str());
        delete f;
        f = NULL;
    }

    return f;
}



void FunctionAnalysis::setOutputDir(std::string &OutputDir, const std::string InputFile)
{
    if (OutputDir=="") {
        llvm::sys::Path directory(InputFile);
        std::stringstream dirname;
        directory.eraseComponent();

        if (directory.isEmpty())
            directory.set(".");

        for (int i = 0; i< INT_MAX ; i++) {
            dirname << "klee-out-";
            dirname << i;

            m_outputDirectory = llvm::sys::Path(directory); // Copy
            if (!m_outputDirectory.appendComponent(dirname.str()))
                klee_error("Failed to append \"%s\" to \"%s\"", dirname.str().c_str(), directory.c_str());

            bool isDir = true;
            llvm::error_code e = llvm::sys::fs::exists(m_outputDirectory.str(), isDir);
            if ( e != llvm::errc::success )
                klee_error("Failed to check if \"%s\" exists.", m_outputDirectory.str().c_str());

            if (!isDir)
            {
                break; // Found an available directory name
            }

            // Warn the user if the klee-out-* exists but is not a directory
            e = llvm::sys::fs::is_directory(m_outputDirectory.str(), isDir);
            if ( e == llvm::errc::success && !isDir )
                klee_warning("A file \"%s\" exists, but it is not a directory",
                        m_outputDirectory.str().c_str());

            dirname.str(""); // Clear
            m_outputDirectory.clear();
        }    

        if (m_outputDirectory.empty())
            klee_error("Failed to find available output directory in %s", dirname.str().c_str());

        std::cerr << "set outdir:  = \"" << dirname.str() << "\"\n";

        llvm::sys::Path klee_last(directory);
        if(!klee_last.appendComponent("klee-last"))
            klee_error("cannot create path name for klee-last");

        if ((unlink(klee_last.c_str()) < 0) && (errno != ENOENT))
            klee_error("cannot unlink klee-last: %s", strerror(errno));

        if (symlink(dirname.str().c_str(), klee_last.c_str()) < 0)
            klee_error("cannot create klee-last symlink: %s", strerror(errno));



    } else {
        if (!m_outputDirectory.set(OutputDir))
            klee_error("cannot use klee output directory: %s", OutputDir.c_str());
    }
#if 1
    if (!sys::path::is_absolute(m_outputDirectory.c_str())) {
        llvm::sys::Path cwd = llvm::sys::Path::GetCurrentDirectory();
        if(!cwd.appendComponent( m_outputDirectory.c_str()))
            klee_error("cannot create absolute path name for output directory");

        m_outputDirectory = cwd;
    }
#endif

    bool isDir = true;
    llvm::error_code e = llvm::sys::fs::exists(m_outputDirectory.str(), isDir);
    if ( !isDir )
        if (mkdir(m_outputDirectory.c_str(), 0775) < 0)
            klee_error("cannot create directory \"%s\": %s", m_outputDirectory.c_str(), strerror(errno));

    OutputDir = m_outputDirectory.str();

}









//===-- StatsTracker.h ------------------------------------------*- C++ -*-===//
//
//                     The KLEE Symbolic Virtual Machine
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef KLEE_STATSTRACKER_H
#define KLEE_STATSTRACKER_H

#include "CallPathManager.h"

#include <iostream>
#include <set>

namespace llvm {
  class BranchInst;
  class Function;
  class Instruction;
}

namespace klee {
  class ExecutionState;
  class Executor;  
  class InstructionInfoTable;
  class InterpreterHandler;
  struct KInstruction;
  struct StackFrame;

  class StatsTracker {
    friend class WriteStatsTimer;
    friend class WriteIStatsTimer;
    friend class LogFuncCallTimer;

    Executor &executor;
    std::string objectFilename;

    std::ostream *statsFile, *istatsFile;
    std::ostream *fistatsFile; // for focus inst track, addbyxqx2015
    std::ostream *flogFile;    //log funcs called in a timeinterval
    std::ostream *cilogFile;
    std::ostream *bblogFile;
    std::ostream *bbcovFile;
    std::ostream *bbvFile;
    std::map<unsigned, unsigned> fCallsMap;  //<func id, call times>
    std::map<uint64_t, unsigned> callInstMap; //<callinst id, call times>
    std::map<unsigned, unsigned> bbCallsMap;
    std::map<unsigned, unsigned> gbbCallsMap; //<bb-id, call times>

    unsigned lastFID;
    double startWallTime;
    
    unsigned numBranches;
    unsigned fullBranches, partialBranches;

    CallPathManager callPathManager;    

    bool updateMinDistToUncovered;

  public:
    static bool useStatistics();

  private:
    void updateStateStatistics(uint64_t addend);
    void writeStatsHeader();
    void writeStatsLine();
    void writeIStats();
    void writeAllIStats();
    void writeFocusIStats();
    void logFuncCallHead();
    void logFuncCallLine();
    void logCallInstHead();
    void logBBCallHead();
    void reportBBCoverage();
    //void logCallInstLine();

  public:
    StatsTracker(Executor &_executor, std::string _objectFilename,
                 bool _updateMinDistToUncovered);
    ~StatsTracker();

    // called after a new StackFrame has been pushed (for callpath tracing)
    void framePushed(ExecutionState &es, StackFrame *parentFrame);

    // called after a StackFrame has been popped 
    void framePopped(ExecutionState &es);

    // called when some side of a branch has been visited. it is
    // imperative that this be called when the statistics index is at
    // the index for the branch itself.
    void markBranchVisited(ExecutionState *visitedTrue, 
                           ExecutionState *visitedFalse);
    
    // called when execution is done and stats files should be flushed
    void done();

    // process stats for a single instruction step, es is the state
    // about to be stepped
    void stepInstruction(ExecutionState &es);

    /// Return time in seconds since execution start.
    double elapsed();

    void computeReachableUncovered();

	//print stats info
	void printStatsInfo(const Statistic &s);
	//print forks time when > 10
	uint64_t printForksStatInfo(KInstruction *ki);
	uint64_t printForksStatInfo(ExecutionState *state) ;
  };

  uint64_t computeMinDistToUncovered(const KInstruction *ki,
                                     uint64_t minDistAtRA);

}

#endif

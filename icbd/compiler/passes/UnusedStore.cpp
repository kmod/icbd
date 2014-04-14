#define DEBUG_TYPE "unusedstore"

#include <deque>
#include <set>

#include "llvm/ADT/Statistic.h"
#include "llvm/Analysis/AliasAnalysis.h"
#include "llvm/Analysis/Passes.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/Function.h"
#include "llvm/GlobalAlias.h"
#include "llvm/GlobalVariable.h"
#include "llvm/Instructions.h"
#include "llvm/IntrinsicInst.h"
#include "llvm/LLVMContext.h"
#include "llvm/Operator.h"
#include "llvm/Pass.h"
#include "llvm/Analysis/CaptureTracking.h"
#include "llvm/Analysis/MemoryBuiltins.h"
#include "llvm/Analysis/InstructionSimplify.h"
#include "llvm/Analysis/ValueTracking.h"
#include "llvm/Target/TargetData.h"
#include "llvm/Target/TargetLibraryInfo.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/Support/Debug.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Support/GetElementPtrTypeIterator.h"
#include "llvm/Support/InstVisitor.h"
#include "llvm/Support/raw_ostream.h"
#include <algorithm>

STATISTIC(NumRemoved, "Number of stores removed");

using namespace llvm;
using namespace std;

namespace {

    static bool isMallocCall(const CallInst *CI) {
        if (!CI)
            return false;

        Function *Callee = CI->getCalledFunction();
        if (Callee == 0 || !Callee->isDeclaration())
            return false;
        if (Callee->getName() != "malloc" &&
                Callee->getName() != "my_malloc" &&
                Callee->getName() != "_Znwj" && // operator new(unsigned int)
                Callee->getName() != "_Znwm" && // operator new(unsigned long)
                Callee->getName() != "_Znaj" && // operator new[](unsigned int)
                Callee->getName() != "_Znam")   // operator new[](unsigned long)
                return false;

        // Check malloc prototype.
        // FIXME: workaround for PR5130, this will be obsolete when a nobuiltin 
        // attribute will exist.
        FunctionType *FTy = Callee->getFunctionType();
        return FTy->getReturnType() == Type::getInt8PtrTy(FTy->getContext()) &&
            FTy->getNumParams() == 1 &&
            (FTy->getParamType(0)->isIntegerTy(32) ||
             FTy->getParamType(0)->isIntegerTy(64));
    }

    /// isFreeCall - Returns non-null if the value is a call to the builtin free()
    static const CallInst *isFreeCall(const Value *I) {
        const CallInst *CI = dyn_cast<CallInst>(I);
        if (!CI)
            return 0;
        Function *Callee = CI->getCalledFunction();
        if (Callee == 0 || !Callee->isDeclaration())
            return 0;

        if (Callee->getName() != "free" &&
                Callee->getName() != "my_free" &&
                Callee->getName() != "_ZdlPv" && // operator delete(void*)
                Callee->getName() != "_ZdaPv")   // operator delete[](void*)
                return 0;

        // Check free prototype.
        // FIXME: workaround for PR5130, this will be obsolete when a nobuiltin 
        // attribute will exist.
        FunctionType *FTy = Callee->getFunctionType();
        if (!FTy->getReturnType()->isVoidTy())
            return 0;
        if (FTy->getNumParams() != 1)
            return 0;
        if (FTy->getParamType(0) != Type::getInt8PtrTy(Callee->getContext()))
            return 0;

        return CI;
    }

    class DefChainFinder : public InstVisitor<DefChainFinder, bool> {
        private:
        StoreInst *SI;
        set<Instruction*> found;
        deque<Instruction*> q;

        bool addDependency(Value* v) {
            if (isa<Argument>(v))
                return false;
            if (isa<GlobalValue>(v))
                return false;

            Instruction *i = dyn_cast<Instruction>(v);
            if (!i)
                return false;

            if (found.find(i) == found.end()) {
                found.insert(i);
                q.push_back(i);
                //delete_order.push_front(i);
            }
            return true;
        }

        public:
        DefChainFinder(StoreInst *SI) : SI(SI) {
        }

        set<Instruction*> getDefChain() {
            addDependency(SI->getPointerOperand());
            while (q.size()) {
                Instruction *next = q.front();
                q.pop_front();

                bool good = visit(next);
                if (!good)
                    return set<Instruction*>();
            }
            return found;
        }

        bool visitGetElementPtrInst(GetElementPtrInst &inst) {
            //if (!inst.hasAllConstantIndices())
                //return false;
            return addDependency(inst.getPointerOperand());
        }

        bool visitBitCastInst(BitCastInst &inst) {
            assert(inst.getNumOperands() == 1);
            return addDependency(inst.getOperand(0));
        }

        bool visitCallInst(CallInst &inst) {
            if (!isMallocCall(&inst))
                return false;
            return true;
        }

        bool visitAllocaInst(AllocaInst &inst) {
            return true;
        }

        bool visitLoadInst(LoadInst &inst) {
            return false;
        }

        bool visitPHINode(PHINode &inst) {
            bool good = true;
            for (PHINode::block_iterator bb_it = inst.block_begin(), bb_end = inst.block_end(); bb_it != bb_end; ++bb_it) {
                good = good && addDependency(inst.getIncomingValueForBlock(*bb_it));
            }
            return good;
        }

        bool visitIntToPtrInst(IntToPtrInst &inst) {
            return false;
        }

        bool visitInstruction(Instruction &inst) {
            errs() << "Don't know how to handle this\n" << inst << '\n';
            assert(false);
            return false;
        }
    };

    class ChainDeadnessAnalyzer : public InstVisitor<ChainDeadnessAnalyzer, bool> {
        private:
        AliasAnalysis &AA;
        AliasAnalysis::Location loc;
        set<Instruction*> processed;
        deque<Instruction*> q;

        void addDependency(Instruction* i) {
            assert(i->getType()->isPointerTy());
            if (AA.isNoAlias(loc, AliasAnalysis::Location(i))) {
                DEBUG(errs() << "ignoring because noalias: " << *i << '\n');
                return;
            }

            if (processed.find(i) == processed.end()) {
                DEBUG(errs() << "adding to queue: " << *i << '\n');
                processed.insert(i);
                q.push_back(i);
            }
        }

        public:
        ChainDeadnessAnalyzer(StoreInst *SI, AliasAnalysis &AA) : AA(AA) {
            loc = AA.getLocation(SI);
        }

        bool isUnread(set<Instruction*> &defchain) {
            for (set<Instruction*>::iterator i = defchain.begin(), e = defchain.end(); i != e; ++i) {
                addDependency(*i);
            }
            while (q.size()) {
                Instruction *next = q.front();
                q.pop_front();
                for (Value::use_iterator use_it = next->use_begin(), use_end = next->use_end(); use_it != use_end; ++use_it) {
                    bool ok = visit(cast<Instruction>(*use_it));
                    if (!ok) {
                        DEBUG(errs() << "failed at " << **use_it << '\n');
                        return false;
                    }
                }
            }
            return true;
        }

        bool visitCallInst(CallInst &inst) {
            if (isFreeCall(&inst))
                return true;
            return false;
        }

        bool visitGetElementPtrInst(GetElementPtrInst &inst) {
            addDependency(&inst);
            return true;
        }

        bool visitBitCastInst(BitCastInst &inst) {
            addDependency(&inst);
            return true;
        }

        bool visitStoreInst(StoreInst &inst) {
            if (!inst.getValueOperand()->getType()->isPointerTy() || AA.isNoAlias(AliasAnalysis::Location(inst.getValueOperand()), loc))
                return true;
            return false;
        }

        bool visitLoadInst(LoadInst &inst) {
            if (AA.isNoAlias(AA.getLocation(&inst), loc))
                return true;
            return false;
        }

        bool visitReturnInst(ReturnInst &inst) {
            return false;
        }

        bool visitPHINode(PHINode &inst) {
            addDependency(&inst);
            return true;
        }

        bool visitPtrToIntInst(PtrToIntInst &inst) {
            return false;
        }

        bool visitICmpInst(ICmpInst &inst) {
            // TODO is this actually bad?
            return false;
        }

        bool visitInstruction(Instruction &inst) {
            errs() << "Don't know how to handle this\n" << inst << '\n';
            assert(false);
            return false;
        }
    };

    class UnusedStorePass : public FunctionPass {
        public:
        static char ID;
        UnusedStorePass() : FunctionPass(ID) {}

        virtual void getAnalysisUsage(AnalysisUsage &info) const {
            info.addRequired<AliasAnalysis>();
            info.setPreservesCFG();
        }

        virtual bool runOnFunction(Function &F) {
            AliasAnalysis &AA = getAnalysis<AliasAnalysis>();
            bool any_changed = false;
            for (Function::iterator bb_it = F.begin(), bb_end = F.end(); bb_it != bb_end; ++bb_it) {
                bool changed = true;
                while (changed) {
                    changed = false;

                    for (BasicBlock::iterator inst_it = bb_it->begin(), inst_end = bb_it->end(); inst_it != inst_end; ++inst_it) {
                        StoreInst *SI = dyn_cast<StoreInst>(inst_it);
                        if (SI == NULL)
                            continue;

                        DEBUG(errs() << "\nlooking at:\n");
                        DEBUG(errs() << *SI << '\n');

                        DefChainFinder dcf(SI);
                        // Probably don't have to use the whole chain, though there's not any downside to doing so (I think?)
                        set<Instruction*> defchain = dcf.getDefChain();
                        if (defchain.size() == 0) {
                            DEBUG(errs() << "not a valid defchain; can't tell where this pointer comes from\n");
                            continue;
                        }

                        DEBUG(errs() << "found these in the def chain:\n");
                        for (set<Instruction*>::iterator i = defchain.begin(), e = defchain.end(); i != e; ++i) {
                            DEBUG(errs() << **i << '\n');
                        }
                        DEBUG(errs() << '\n');

                        ChainDeadnessAnalyzer CDA(SI, AA);
                        bool okToDelete = CDA.isUnread(defchain);
                        if (!okToDelete) {
                            DEBUG(errs() << "not ok to delete, used\n");
                        } else {
                            DEBUG(errs() << "deleting!\n");
                            SI->eraseFromParent();
                            NumRemoved++;
                            changed = true;
                            any_changed = true;
                            break;
                        }
                    }
                }
            }
            return any_changed;
        }

    };
}

char UnusedStorePass::ID = 0;
static RegisterPass<UnusedStorePass> X("unusedstore", "Remove unused stores", true, false);


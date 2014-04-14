#define DEBUG_TYPE "deadmallocs"

#include <map>
#include <queue>
#include <set>

#include "llvm/ADT/Statistic.h"
#include "llvm/Analysis/Dominators.h"
#include "llvm/Analysis/PostDominators.h"
#include "llvm/Assembly/Writer.h"
#include "llvm/Constants.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Module.h"
#include "llvm/Operator.h"
#include "llvm/Pass.h"
#include "llvm/Support/Debug.h"
#include "llvm/Support/InstIterator.h"
#include "llvm/Support/InstVisitor.h"
#include "llvm/Support/raw_ostream.h"

STATISTIC(NumChains, "Number of dead chains found");
STATISTIC(NumDeleted, "Number of instructions deleted");

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

    class ChainEvaluator : public InstVisitor<ChainEvaluator, bool> {
        private:
            deque<Instruction*> &q;
            set<Instruction*> processed;
            deque<Instruction*> &delete_order;
            bool &found_free;
            DominatorTree &DT;
            PostDominatorTree &PDT;
            CallInst *malloc_call;

            Instruction *cur_inst;

            ChainEvaluator(deque<Instruction*> &q, set<Instruction*> &processed, deque<Instruction*> &delete_order, bool &found_free, DominatorTree &DT, PostDominatorTree &PDT, CallInst *malloc_call) :
                q(q), processed(processed), delete_order(delete_order), found_free(found_free), DT(DT), PDT(PDT), malloc_call(malloc_call) {
            }

            void addDependency(Instruction* i) {
                if (processed.find(i) == processed.end()) {
                    processed.insert(i);
                    q.push_back(i);
                    delete_order.push_front(i);
                }
            }

        public:
        static deque<Instruction*> evaluateChain(CallInst* malloc_call, DominatorTree &DT, PostDominatorTree &PDT) {
            assert(isMallocCall(malloc_call));

            deque<Instruction*> q;
            set<Instruction*> processed;
            deque<Instruction*> delete_order;
            bool found_free = false;

            ChainEvaluator ce(q, processed, delete_order, found_free, DT, PDT, malloc_call);
            ce.addDependency(malloc_call);

            while (q.size()) {
                Instruction *next = q.front();
                q.pop_front();
                ce.cur_inst = next;
                DEBUG(errs() << "processing: " << *next << '\n');
                DEBUG(errs() << "things that use it:" << '\n');
                for (Value::use_iterator use_it = next->use_begin(), use_end = next->use_end(); use_it != use_end; ++use_it) {
                    DEBUG(errs() << **use_it << '\n');
                    bool this_deleteable = ce.visit(cast<Instruction>(*use_it));
                    if (!this_deleteable)
                        return deque<Instruction*>();
                }
            }
            return delete_order;
        }

        bool visitStoreInst(StoreInst &inst) {
            if (inst.getValueOperand() != cur_inst) {
                assert(inst.getPointerOperand() == cur_inst);
                addDependency(&inst);
                return true;
            } else {
                return false;
            }
        }

        bool visitCallInst(CallInst &inst) {
            if (found_free || !isFreeCall(&inst))
                return false;

            assert(inst.getCalledFunction()->getFunctionType()->getReturnType()->isVoidTy());

            if (inst.getArgOperand(0) != malloc_call) {
                DEBUG(errs() << "freeing something thats based on this malloc but isnt the malloc...?\n");
                return false;
            }
            assert(DT.dominates(malloc_call->getParent(), inst.getParent()));
            // Not really going to care if it post-dominates or not; if it's never used we still optimize it away.
            addDependency(&inst);
            // assume that the memory management discipline is correct and that we never double-free anything
            //found_free = true;
            return true;

            //if (!DT.dominates(malloc_call->getParent(), inst.getParent()) || !PDT.dominates(inst.getParent(), malloc_call->getParent())) {
                //DEBUG(errs() << "not a single region\n");
                //return false;
            //} else {
                //DEBUG(errs() << "Yep it checks out\n");
                //found_free = true;
                //addDependency(&inst);
                //return true;
            //}
        }

        bool visitBitCast(BitCastInst &inst) {
            addDependency(&inst);
            return true;
        }

        bool visitGetElementPtrInst(GetElementPtrInst &inst) {
            assert(inst.getPointerOperand() == cur_inst);
            addDependency(&inst);
            return true;
        }

        bool visitPHINode(PHINode &inst) {
            // Assuming that this is a non-degenerate phi node (which codegen / other optimization passes should enforce),
            // one of the other inputs is something different and we don't want to free it.
            // This case probably doesn't happen that much for the stuff that this
            // pass should work on.
            return false;
            /*
            bool found = false;
            for (PHINode::block_iterator it = inst.block_begin(), end = inst.block_end(); it != end; ++it) {
                //if (*it == cur_inst)
                    //return false;
                Value *v = inst.getIncomingValueForBlock(*it);
                if (v == cur_inst)
                    found = true;
            }
            assert(found);
            addDependency(&inst);
            return true;
            */
        }

        bool visitLoadInst(LoadInst &inst) {
            return false;
        }

        bool visitReturnInst(ReturnInst &inst) {
            return false;
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

    class DeadMallocPass : public FunctionPass {
        public:
        static char ID;
        DeadMallocPass() : FunctionPass(ID) {}

        virtual void getAnalysisUsage(AnalysisUsage &info) const {
            info.setPreservesCFG();
            info.addRequired<PostDominatorTree>();
            info.addRequired<DominatorTree>();
        }

        virtual bool runOnFunction(Function &F) {
            DominatorTree &DT = getAnalysis<DominatorTree>();
            assert(&DT != NULL);
            DEBUG(DT.print(errs()));

            PostDominatorTree &PDT = getAnalysis<PostDominatorTree>();
            assert(&PDT != NULL);
            DEBUG(PDT.DT->print(errs()));

            bool any_changed = false;
            bool this_changed = true;
            set<Instruction*> seen;
            while (this_changed) {
                this_changed = false;
                for (inst_iterator inst_it = inst_begin(F), _inst_end = inst_end(F); inst_it != _inst_end; ++inst_it) {
                    if (!isMallocCall(dyn_cast<CallInst>(&*inst_it)) || seen.find(&*inst_it) != seen.end())
                        continue;

                    // I guess it's possible that by deleting one chain we may make another deletable
                    //seen.insert(&*inst_it);

                    DEBUG(errs() << "Found malloc call:\n" << *inst_it << '\n');
                    deque<Instruction*> to_delete = ChainEvaluator::evaluateChain(cast<CallInst>(&*inst_it), DT, PDT);

                    if (to_delete.size()) {
                        DEBUG(errs() << "found a dead chain!\n");
                        NumChains++;
                        for (deque<Instruction*>::iterator proc_it = to_delete.begin(), proc_end = to_delete.end(); proc_it != proc_end; ++proc_it) {
                            DEBUG(errs() << "deleting: " << **proc_it << '\n');
                            NumDeleted++;
                            (*proc_it)->eraseFromParent();
                        }
                        this_changed = true;
                        break;
                    } else {
                        DEBUG(errs() << "not a valid chain\n");
                    }
                }

                if (this_changed)
                    any_changed = true;
            }

            DEBUG(errs() << '\n');

            return any_changed;
        }

    };
}

char DeadMallocPass::ID = 0;
static RegisterPass<DeadMallocPass> X("deadmalloc", "Remove dead mallocs", true, false);


#define DEBUG_TYPE "myaa"

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
#include "llvm/Support/raw_ostream.h"
#include <algorithm>
using namespace llvm;

STATISTIC(NumImproved, "Number of queries that were improved");

namespace llvm {
    void initializeMyAAPass(PassRegistry&);
    //ImmutablePass* createMyAAPass();
}

namespace {

    namespace {
        struct MyAA : public ImmutablePass, public AliasAnalysis {
            static char ID; // Class identification, replacement for typeinfo
            MyAA() : ImmutablePass(ID) {
                initializeMyAAPass(*PassRegistry::getPassRegistry());
            }

            virtual void initializePass() {
                AliasAnalysis::InitializeAliasAnalysis(this);
            }

            virtual void getAnalysisUsage(AnalysisUsage &AU) const {
                AliasAnalysis::getAnalysisUsage(AU);
                AU.addRequired<AliasAnalysis>();
                AU.setPreservesAll();
            }

            virtual ModRefResult getModRefInfo(ImmutableCallSite CS,
                    const Location &Loc) {
                ModRefResult base = AliasAnalysis::getModRefInfo(CS, Loc);
                if (!CS.getCalledFunction())
                    return base;

                ModRefResult mask = ModRef;

                DEBUG(errs() << *CS.getInstruction() <<'\n');
                StringRef name = CS.getCalledFunction()->getName();
                if (name == "printf" || name == "my_realloc" || name == "print_space_if_necessary" || name == "write") {
                    mask = Ref;
                    bool found_alias = false;
                    for (User::const_op_iterator op_it = CS.arg_begin(), op_end = CS.arg_end(); op_it != op_end; ++op_it) {
                        if (alias(Loc, Location(op_it->get())) != NoAlias) {
                            found_alias = true;
                            break;
                        }
                    }
                    if (!found_alias)
                        mask = NoModRef;
                } else if (name == "snprintf" || name == "str_decref" || name == "read" || name == "file_write") {
                    mask = ModRef;
                    bool found_alias = false;
                    for (User::const_op_iterator op_it = CS.arg_begin(), op_end = CS.arg_end(); op_it != op_end; ++op_it) {
                        if (alias(Loc, Location(op_it->get())) != NoAlias) {
                            //errs() << '\n';
                            //errs() << *CS.getInstruction() << '\n';
                            //errs() << **op_it << '\n';
                            found_alias = true;
                            break;
                        }
                    }
                    if (!found_alias) {
                        mask = NoModRef;
                    }
                } else if (name == "my_free" || name == "my_malloc" || name == "close" || name == "int_repr") {
                    mask = NoModRef;
                }

                if ((mask & base) != base)
                    NumImproved++;
                return ModRefResult(mask & base);
            }

            /// getAdjustedAnalysisPointer - This method is used when a pass implements
            /// an analysis interface through multiple inheritance.  If needed, it
            /// should override this to adjust the this pointer as needed for the
            /// specified pass info.
            virtual void *getAdjustedAnalysisPointer(const void *ID) {
              if (ID == &AliasAnalysis::ID)
                return (AliasAnalysis*)this;
              return this;
            }

        };
    }  // End of anonymous namespace

}

char MyAA::ID = 0;
INITIALIZE_AG_PASS(MyAA, AliasAnalysis, "myaa",
        "My AA (a few special cases)",
        false, true, false)
//static RegisterPass<MyAA> P("myaa", "My AA (a few special cases)", true, true);
//static RegisterAnalysisGroup<AliasAnalysis> G(P);

//ImmutablePass *llvm::createMyAAPass() {
    //return new MyAA();
//}
//MyAA *_p = new MyAA();

namespace {
    struct Foo {
        Foo() {
            initializeMyAAPass(*PassRegistry::getPassRegistry());
        }
    } _f;
}



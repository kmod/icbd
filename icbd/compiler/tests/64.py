"""
Regression test, from the pystone benchmark
"""

class Record(object):
    def __init__(self, PtrComp):
        self.PtrComp = PtrComp

    def copy(self):
        return Record(self.PtrComp)


def Proc1(PtrParIn):
    NextRecord = PtrGlb.copy()
    PtrParIn.PtrComp = NextRecord
    if True:
        NextRecord.PtrComp = PtrGlb.PtrComp
    else:
        PtrParIn = NextRecord.copy()
    return PtrParIn

PtrGlb = Record(None)
PtrGlb = Proc1(PtrGlb)
PtrGlb = Proc1(PtrGlb)



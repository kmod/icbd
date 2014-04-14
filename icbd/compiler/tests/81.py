def call_common_funcs(o):
    print len(o), bool(o), str(o), repr(o)

call_common_funcs("hello world")
call_common_funcs([1, 2, 3])
if "true":
    o = {1:2}
else:
    o = ["hello world"]
call_common_funcs(o)

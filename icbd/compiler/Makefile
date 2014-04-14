OPTLEVEL=
CFLAGS=$(OPTLEVEL) -std=c99 -Wall -Werror
CLANGFLAGS=$(OPTLEVEL) -Wall -emit-llvm -Werror
CXXFLAGS=$(OPTLEVEL) -Werror
LINKFLAGS=$(OPTLEVEL) -lm
PYTHON=python

LLVM_SRC=/home/kmod/icbd_deps/llvm-3.1.src
LLVM_PASS_DIR=$(LLVM_SRC)/lib/Transforms/icbd
LLVM_TEST_DIR=$(LLVM_SRC)/test/Transforms/icbd
LLVM_PASS_LIB=$(LLVM_SRC)/Release+Asserts/lib/icbd_passes.so

LLVM_BIN=$(LLVM_SRC)/Release+Asserts/bin
OPT=$(LLVM_BIN)/opt
LLC=$(LLVM_BIN)/llc
LLVM_DIS=$(LLVM_BIN)/llvm-dis
CLANG=$(LLVM_BIN)/clang
LLVM_LINK=$(LLVM_BIN)/llvm-link
LLVM_LIT=$(LLVM_BIN)/llvm-lit

OPT_DEPS = $(OPT) $(LLVM_PASS_LIB)

CC=/usr/lib/gcc-snapshot/bin/gcc
CXX=/usr/lib/gcc-snapshot/bin/g++
OPTARGS=OPT=$(OPT) LOAD=$(LLVM_PASS_LIB) OPTLEVEL="-inline-threshold=255 -basicaa -myaa $(OPTLEVEL) -deadmalloc -unusedstore -mallocs_nonnull"

TESTS = $(wildcard tests/*.py)
BENCHES = $(wildcard benchmarks/*/*.py)
HEADERS = $(wildcard runtime/*.h)
RUNTIME_SRCS = $(patsubst %.c,runtime/%.c,bool.c file.c nums.c string.c misc.c math.c slice.c)
RUNTIME_OBJS = $(patsubst %.c,%.o,$(RUNTIME_SRCS))
RUNTIME_OBJS_BC = $(patsubst %.c,%.gen.bc,$(RUNTIME_SRCS))
COMPILER_SRCS = $(filter-out tester.py,$(wildcard *.py) $(wildcard templates/*.tll) $(wildcard templates/*.tc) Makefile $(wildcard ../util/*.py) $(wildcard ../type_checker/*.py)) $(wildcard ../../stdlib/compiler/*)

# Put this first to make it the default target
.PHONY: compiler
compiler: $(RUNTIME_OBJS) $(RUNTIME_OBJS_BC) $(OPT_DEPS) runtime/alloc.o runtime/alloc.gen.bc runtime/alloc.nodebug.gen.bc

.PHONY: dist
dist: compiler
	[ ! -e ../../build ] || (echo "root build directory shouldn't exist" ; false)
	[ ! -e ../../dist ] || (echo "root dist directory shouldn't exist" ; false)
	[ ! -e ../../icbd.egg-info ] || (echo "root icbd.egg-info directory shouldn't exist" ; false)
	rm -rfv dist
	mkdir dist
	$(LLVM_LINK) $(RUNTIME_OBJS_BC) runtime/alloc.gen.bc -S -o dist/runtime_debug.bc
	$(LLVM_LINK) $(RUNTIME_OBJS_BC) runtime/alloc.nodebug.gen.bc -S -o dist/runtime_nodebug.bc
	cp dist_compile.sh dist/icbc
	(cd ../..; $(PYTHON) setup.py bdist_egg) || (rm -rf ../../build ../../dist ../../icbd.egg-info; false)
	cp ../../dist/*.egg dist/icbd.egg
	rm -rf ../../build ../../dist ../../icbd.egg-info

	cp -rv templates dist/
	cp $(CLANG) dist/clang
	cp $(LLVM_LINK) dist/llvm-link
	cp $(LLC) dist/llc
	mkdir dist/runtime_includes
	cp -rv runtime/*.h dist/runtime_includes/
	cp -rv ../../stdlib dist/stdlib/


-include $(TESTS:.py=.d)

.PHONY: all, all23
all23:  $(patsubst tests/%.py,%.out2,$(TESTS)) $(patsubst tests/%.py,%.out3,$(TESTS)) $(RUNTIME_OBJS) runtime/alloc.o $(RUNTIME_OBJS_BC) runtime/alloc.gen.bc
all: $(patsubst tests/%.py,%.out,$(TESTS)) all23

# I don't know why a rule exists to convert % to %.out...
%.out: %

%.out: tests/%.out
	cp "$<" "$@"
%.out2: tests/%.out2
	cp "$<" "$@"
%.out3: tests/%.out3
	cp "$<" "$@"

%.shed: %.py
	./shedder.py "$<" "$@"

.PHONY: shedskins
shedskins: $(patsubst %.py,%.shed,$(TESTS))

.PHONY: benchmarks
benchmarks: $(patsubst %.py,%.out3,$(BENCHES))

# Compiling the tools:

.PHONY: patch, unpatch
patch: $(LLVM_SRC)/_patched
unpatch:
	[ ! -f $(LLVM_SRC)/_patched ] || (patch -R -d $(LLVM_SRC) -p0 < $(LLVM_SRC)/_patched && rm $(LLVM_SRC)/_patched)

$(LLVM_SRC)/_patched: llvm-3.1/llvm.patch
	[ ! -f $(LLVM_SRC)/_patched ] || (patch -R -d $(LLVM_SRC) -p0 < $(LLVM_SRC)/_patched && rm $(LLVM_SRC)/_patched)
	patch -d $(LLVM_SRC) -p0 < "$<"
	cp "$<" $(LLVM_SRC)/_patched

$(OPT): $(LLVM_SRC)/_patched
	make -C $(LLVM_SRC) -j4


# Compiling my passes:

PASS_FILES = passes/Makefile $(wildcard passes/*.cpp)
PASS_TARGETS = $(patsubst passes/%,$(LLVM_PASS_DIR)/%,$(PASS_FILES))
PASS_TEST_DIRS = $(patsubst %,$(LLVM_TEST_DIR)/%,aa deadmalloc deadstore)
PASS_TESTS = $(patsubst passes/test/%,$(LLVM_TEST_DIR)/%,passes/test/lit.local.cfg $(wildcard passes/test/*/*))

$(LLVM_PASS_DIR):
	mkdir $(LLVM_PASS_DIR)
$(LLVM_TEST_DIR):
	mkdir $(LLVM_TEST_DIR)

.PRECIOUS: $(LLVM_PASS_DIR)/% $(LLVM_TEST_DIR)
$(LLVM_PASS_DIR)/%: passes/% | $(LLVM_PASS_DIR)
	cp "$<" "$@"
$(LLVM_TEST_DIR)/%: passes/test/% | $(LLVM_TEST_DIR)
	mkdir -p `dirname "$@"`
	cp "$<" "$@"

$(LLVM_PASS_LIB): $(PASS_TARGETS)
	rm -f $(LLVM_PASS_LIB)
	make -C $(LLVM_PASS_DIR)

.PHONY: pass_test pass_tests pass_lib
pass_lib: $(LLVM_PASS_LIB)

pass_%: passes/test/%.ll $(LLVM_PASS_LIB) $(OPT)
	# $(OPT) -load $(LLVM_PASS_LIB) tests/pass_test.ll -S -O3 -deadmalloc --debug-pass=Structure
	# $(OPT) -load $(LLVM_PASS_LIB) passes/test/loop.ll -S -deadmalloc --debug-pass=Structure -stats
	$(OPT) -load $(LLVM_PASS_LIB) "$<" -S -deadmalloc -debug

aa_test: $(LLVM_PASS_LIB) $(OPT)
	make -C $(LLVM_SRC)/lib/Transforms/Scalar -j4 && make -C $(LLVM_SRC)/tools/opt -j4
	$(OPT) -load $(LLVM_PASS_LIB) passes/test/aa/printf_prestore.ll -S -disable-output -stats --debug-pass=Structure -basicaa -myaa -count-aa -dse -gvn --unusedstore

aa_test_show: $(LLVM_PASS_LIB) $(OPT)
	make -C $(LLVM_SRC)/lib/Transforms/Scalar -j4 && make -C $(LLVM_SRC)/tools/opt -j4
	$(OPT) -load $(LLVM_PASS_LIB) passes/test/aa/printf_prestore.ll -S -stats --debug-pass=Structure -basicaa -myaa -dse -gvn -unusedstore

pass_tests: $(LLVM_PASS_LIB) $(PASS_TESTS) $(OPT)
	$(LLVM_LIT) -v $(LLVM_TEST_DIR)

# Compiling the runtime files:

.PRECIOUS: %.o
%.o: %.c Makefile $(HEADERS)
	$(CC) $(CFLAGS) -c "$<" -o "$@"

.PRECIOUS: %.gen.bc
%.gen.bc: %.c Makefile $(HEADERS)
	$(CLANG) $(CLANGFLAGS) "$<" -o "$@" -c
	$(LLVM_DIS) "$@"

.PRECIOUS: %.nodebug.gen.bc
%.nodebug.gen.bc: %.c Makefile $(HEADERS)
	$(CLANG) -DREALMALLOC $(CLANGFLAGS) "$<" -o "$@" -c
	$(LLVM_DIS) "$@"


# Compiling + optimizing the llvm files:

.PRECIOUS: %.gen.ll
%.gen.ll: %.py $(COMPILER_SRCS)
	PYTHONPATH=../.. $(PYTHON) compile.py -p ../../stdlib/compiler -t ../../stdlib/type_mocks "$<" "$@" "$(patsubst %.gen.ll,%.gen.c,$@)" "$(patsubst %.gen.ll,%.d,$@)"

# not exactly sure why i need this rule...
.PRECIOUS: %.gen.c
%.gen.c: %.gen.ll
	true

.PRECIOUS: %.c.gen.bc
%.c.gen.bc: %.gen.c Makefile $(HEADERS)
	$(CLANG) $(CLANGFLAGS) -iquote runtime "$<" -o "$@" -c
	$(LLVM_DIS) "$@" || (rm "$@" && false)

.PRECIOUS: %.opt.ll
%.opt.ll: %.gen.ll %.c.gen.bc Makefile superopt.py $(OPT_DEPS)
	$(LLVM_LINK) "$<" "$(patsubst %.opt.ll,%.c.gen.bc,$@)" -S -o "$(patsubst %.opt.ll,%.comb.ll,$@)"
ifeq ($(OPTLEVEL),)
	cp "$(patsubst %.opt.ll,%.comb.ll,$@)" "$@"
else
	$(OPTARGS) $(PYTHON) superopt.py "$(patsubst %.opt.ll,%.comb.ll,$@)" | sponge "$@"
endif

.PRECIOUS: %.gen.s
%.gen.s: %.opt.ll Makefile
	$(LLC) "$<" -o "$@" $(OPTLEVEL)

.PRECIOUS: %.out
%.out: %.gen.s $(RUNTIME_OBJS) runtime/alloc.o Makefile
	$(CC) $(LINKFLAGS) $(RUNTIME_OBJS) runtime/alloc.o "$<" -o "$@"

.PRECIOUS: %.link.gen.ll
%.link.gen.ll: %.opt.ll $(RUNTIME_OBJS_BC) Makefile
	$(LLVM_LINK) "$<" $(RUNTIME_OBJS_BC) -S -o "$@"

# Yes, I know this is the same exact rule as %.gen.ll -> %.opt.ll
# Make has a constraint that you can only use an implicit rule once in a chain
# Also it seems to choke when there is too much of a common suffix (ex a %.link.opt.ll rule doesn't work)
.PRECIOUS: %.linkopt.ll
%.linkopt.ll: %.link.gen.ll Makefile superopt.py $(OPT_DEPS)
ifeq ($(OPTLEVEL),)
	cp "$<" "$@"
else
	$(OPTARGS) $(PYTHON) superopt.py "$<" | sponge "$@"
endif

.PRECIOUS: %.mem.gen.ll
%.mem.gen.ll: %.linkopt.ll runtime/alloc.gen.bc Makefile
	$(LLVM_LINK) "$<" runtime/alloc.gen.bc -S -o "$@"

.PRECIOUS: %.memopt.ll
%.memopt.ll: %.mem.gen.ll Makefile superopt.py $(OPT_DEPS)
ifeq ($(OPTLEVEL),)
	cp "$<" "$@"
else
	$(OPTARGS) $(PYTHON) superopt.py "$<" | sponge "$@"
endif

.PRECIOUS: %.mem3.gen.ll
%.mem3.gen.ll: %.linkopt.ll runtime/alloc.nodebug.gen.bc Makefile
	$(LLVM_LINK) "$<" runtime/alloc.nodebug.gen.bc -S -o "$@"

.PRECIOUS: %.mem3opt.ll
%.mem3opt.ll: %.mem3.gen.ll Makefile superopt.py $(OPT_DEPS)
ifeq ($(OPTLEVEL),)
	cp "$<" "$@"
else
	$(OPTARGS) $(PYTHON) superopt.py "$<" | sponge "$@"
endif

.PRECIOUS: %.gen2.s
%.gen2.s: %.memopt.ll Makefile
	$(LLC) "$<" -o "$@" $(OPTLEVEL) || (rm -f "$@"; false)

.PRECIOUS: %.gen3.s
%.gen3.s: %.mem3opt.ll Makefile
	$(LLC) "$<" -o "$@" $(OPTLEVEL) || (rm -f "$@"; false)

.PRECIOUS: %.out2
%.out2: %.gen2.s Makefile
	$(CC) $(LINKFLAGS) "$<" -o "$@" || (rm -f "$@"; false)

.PRECIOUS: %.out3
%.out3: %.gen3.s Makefile
	$(CC) $(LINKFLAGS) "$<" -o "$@" || (rm -f "$@"; false)


# Misc:

.PHONY: %.run
%.run: %.out
	"./$<"

.PHONY: %.run2
%.run2: %.out2
	"./$<"

.PHONY: %.run3
%.run3: %.out3
	"./$<"

.PHONY: clean, allclean, clean%
clean:
	find . \( -name '*.comb.ll' -o -name '*.gen.c' -o -name '*.gen.bc' -o -name '*.o' -o -name '*.gen.ll' -o -name '*opt.ll' -o -name '*opt[0-9].ll' -o -name '*.gen.s' -o -name '*.gen[0-9].s' -o -name '*.out' -o -name '*.out[0-9]' -o -name '*.pyc' -o -name '*.d' -o -name '*.pyicbd' -o -name '*.pyd' \) -print0 | xargs -0 rm -fv
	rm -vf *.ll
	rm -rfv dist

clean%:
	rm -f $(patsubst clean%, tests/%.gen.ll, $@)
	rm -f $(patsubst clean%, tests/%.opt.ll, $@)
	rm -f $(patsubst clean%, tests/%.gen.s, $@)
	rm -f $(patsubst clean%, tests/%.out, $@)
	rm -f $(patsubst clean%, %.out, $@)
	rm -f $(patsubst clean%, tests/%.link.gen.ll, $@)
	rm -f $(patsubst clean%, tests/%.linkopt.ll, $@)
	rm -f $(patsubst clean%, tests/%.mem.gen.ll, $@)
	rm -f $(patsubst clean%, tests/%.memopt.ll, $@)
	rm -f $(patsubst clean%, tests/%.gen2.s, $@)
	rm -f $(patsubst clean%, tests/%.out2, $@)
	rm -f $(patsubst clean%, %.out2, $@)
	rm -f $(patsubst clean%, tests/%.mem3.gen.ll, $@)
	rm -f $(patsubst clean%, tests/%.mem3opt.ll, $@)
	rm -f $(patsubst clean%, tests/%.gen3.s, $@)
	rm -f $(patsubst clean%, tests/%.out3, $@)
	rm -f $(patsubst clean%, %.out3, $@)

allclean: clean
	rm -fv $(LLVM_PASS_LIB)
	rm -rfv $(LLVM_PASS_DIR)
	rm -rfv $(LLVM_TEST_DIR)
	find -name '*.shed' | xargs rm -fv

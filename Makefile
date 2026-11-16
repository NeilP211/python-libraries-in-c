# Builds the two C libraries that the Python experiments use.
#   make        build everything into build/
#   make test   build, then run the test suite
#   make bench  build, then run the full benchmark (about a minute)
#   make clean  delete build/

PYTHON ?= python3
CC ?= cc
CFLAGS ?= -O2 -Wall -Wextra -Werror

UNAME := $(shell uname)
ifeq ($(UNAME),Darwin)
  SHLIB := build/libmymath.dylib
  # Extension modules resolve Python's symbols from the running interpreter.
  EXT_LDFLAGS := -undefined dynamic_lookup
else
  SHLIB := build/libmymath.so
  EXT_LDFLAGS :=
endif

PY_INCLUDE := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_paths()['include'])")
EXT_SUFFIX := $(shell $(PYTHON) -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
EXT := build/fastmath$(EXT_SUFFIX)

.PHONY: all test bench clean

all: $(SHLIB) $(EXT)

# Plain C to shared library, loaded later with ctypes.
$(SHLIB): c/mymath.c | build
	$(CC) $(CFLAGS) -fPIC -shared -o $@ $<

# CPython extension module, loaded later with a normal `import fastmath`.
$(EXT): c/fastmath_module.c | build
	$(CC) $(CFLAGS) -fPIC -shared -I$(PY_INCLUDE) $(EXT_LDFLAGS) -o $@ $<

build:
	mkdir -p build

test: all
	$(PYTHON) -m pytest -q tests

bench: all
	$(PYTHON) python/04_benchmark.py

clean:
	rm -rf build

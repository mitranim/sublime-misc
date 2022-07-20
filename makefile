MAKEFLAGS := --silent --always-make
WATCH := watchexec -r -c -d=0 -n

test_w:
	$(WATCH) -- $(MAKE) test

test:
	python3 sublime_misc_test.py

# Assumes MacOS and Homebrew.
deps:
	brew install -q watchexec

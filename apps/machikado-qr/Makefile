PYTHON ?= python3
PORT ?= 8000

.PHONY: setup build verify demo

setup:
	$(PYTHON) -m pip install -r requirements.txt

build:
	$(PYTHON) scripts/build_points.py
	$(PYTHON) scripts/build_prototype.py

verify: build
	$(PYTHON) scripts/verify.py

demo:
	@echo "Open http://localhost:$(PORT)/demo.html"
	$(PYTHON) -m http.server $(PORT) --directory prototype

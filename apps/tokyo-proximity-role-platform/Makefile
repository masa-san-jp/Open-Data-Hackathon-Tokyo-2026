.PHONY: doctor demo serve-demo verify-demo fetch-m1 build-m1 verify-m1 test-role verify screenshot build-real-map verify-real-map real-map screenshot-real-map

doctor:
	python3 --version
	node --version || true

demo:
	python3 scripts/build_demo.py
	python3 scripts/build_prototype.py

serve-demo:
	python3 -m http.server 8000 --directory prototype

verify-demo:
	python3 scripts/verify.py --phase demo

fetch-m1:
	python3 scripts/audit_sources.py --phase m1

build-m1:
	python3 scripts/normalize_sources.py
	python3 scripts/build_network.py
	python3 scripts/attach_elevation.py
	python3 scripts/calculate_accessibility.py
	python3 scripts/build_map_dataset.py

verify-m1:
	pytest -q tests/test_accessibility.py
	python3 scripts/verify.py --phase m1

test-role:
	pytest -q tests/test_role_cards.py tests/test_routing.py

verify: verify-demo

screenshot:
	python3 scripts/screenshot.py

build-real-map:
	python3 scripts/normalize_ome_sources.py
	python3 scripts/build_real_map.py

verify-real-map:
	python3 scripts/verify_real_map.py

real-map: build-real-map verify-real-map

screenshot-real-map: real-map
	python3 scripts/screenshot_real_map.py

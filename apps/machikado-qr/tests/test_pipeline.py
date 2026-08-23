from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build_points = load_module("machikado_build_points", BASE / "scripts" / "build_points.py")
build_prototype = load_module(
    "machikado_build_prototype", BASE / "scripts" / "build_prototype.py"
)


class MunicipalityTests(unittest.TestCase):
    def test_longest_municipality_match(self):
        self.assertEqual(
            build_points.municipality_from("武蔵村山市大南1-131"), "武蔵村山市"
        )
        self.assertEqual(build_points.municipality_from("羽村市五ノ神4-13-7"), "羽村市")
        self.assertEqual(
            build_points.municipality_from("東京都東村山市本町1-1"), "東村山市"
        )

    def test_known_prefix_collision_is_removed(self):
        self.assertNotEqual(
            build_points.code_for("武蔵野市", 1),
            build_points.code_for("武蔵村山市", 1),
        )


class GeneratedDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((BASE / "data" / "points.json").read_text(encoding="utf-8"))
        cls.report = json.loads(
            (BASE / "data" / "build-report.json").read_text(encoding="utf-8")
        )
        cls.config = json.loads((BASE / "config.json").read_text(encoding="utf-8"))

    def test_place_codes_are_unique(self):
        codes = [point["c"] for point in self.data["points"]]
        self.assertEqual(len(codes), len(set(codes)))

    def test_every_point_is_an_explicit_candidate(self):
        self.assertTrue(self.data["points"])
        self.assertEqual({point["status"] for point in self.data["points"]}, {"candidate"})
        self.assertEqual(self.data["data_mode"], "candidate-demo")

    def test_only_enabled_destination_kinds_are_published(self):
        allowed = set(self.config["data_quality"]["allowed_destination_kinds"])
        self.assertEqual({item["k"] for item in self.data["dest"]}, allowed)

    def test_transport_dataset_is_quarantined(self):
        sources = {source["id"]: source for source in self.data["sources"]}
        self.assertEqual(sources["daredemo-tokyo-transport"]["runtime_status"], "quarantined")
        self.assertGreaterEqual(
            self.report["destinations"]["transport"]["largest_coordinate_cluster"], 100
        )

    def test_demo_route_has_a_next_candidate(self):
        points = {point["c"]: point for point in self.data["points"]}
        current = points[self.config["demo"]["current_place_code"]]
        home = points[self.config["demo"]["home_place_code"]]
        route = self.config["wayfinding"]
        home_distance = build_points.meters(
            current["lat"], current["lon"], home["lat"], home["lon"]
        )
        candidates = []
        for point in points.values():
            if point["c"] == current["c"]:
                continue
            leg = build_points.meters(
                current["lat"], current["lon"], point["lat"], point["lon"]
            )
            remaining = build_points.meters(
                point["lat"], point["lon"], home["lat"], home["lon"]
            )
            if (
                route["minimum_leg_m"] <= leg <= route["maximum_leg_m"]
                and home_distance - remaining >= route["minimum_progress_m"]
            ):
                candidates.append(point)
        self.assertTrue(candidates)

    def test_destination_coordinate_clusters_respect_gate(self):
        counts = Counter((item["lat"], item["lon"]) for item in self.data["dest"])
        maximum = self.config["data_quality"]["max_duplicate_destination_coordinate_cluster"]
        self.assertLessEqual(max(counts.values(), default=0), maximum)


class PrototypeTests(unittest.TestCase):
    def test_inline_json_escapes_script_breakout(self):
        encoded = build_prototype.script_safe_json({"value": "</script><script>bad()</script>"})
        self.assertNotIn("</script>", encoded.lower())

    def test_generated_html_is_complete_and_offline_first(self):
        html = (BASE / "prototype" / "index.html").read_text(encoding="utf-8")
        for marker in ("__DATA__", "__CONFIG__", "__STYLES__", "__APP_JS__"):
            self.assertNotIn(marker, html)
        self.assertIn("connect-src 'none'", html)
        self.assertNotIn("<script src=", html.lower())
        self.assertNotIn("<link rel=\"stylesheet\"", html.lower())

    def test_demo_entry_exists(self):
        demo = (BASE / "prototype" / "demo.html").read_text(encoding="utf-8")
        self.assertIn("index.html?demo=1", demo)


if __name__ == "__main__":
    unittest.main()

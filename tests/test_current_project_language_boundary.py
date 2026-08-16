from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CurrentProjectLanguageBoundaryTests(unittest.TestCase):
    def test_current_scope_binds_technical_field_and_evidence_limits(self) -> None:
        scope = (ROOT / "docs" / "AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "technikbasiertes MCM-Wahrnehmungsfeld",
            "Lauf 198 ist ausschliesslich eine reale Fixed-Adapter-Gegenbaseline",
            "S1-HG beendet den Frozen-E1-Probezweig",
            "Memory` bezeichnet ausschliesslich eine offene Forschungsrichtung",
            "eigene technische Gegenprognose",
        ):
            self.assertIn(required, scope)

    def test_entry_documents_show_s1lp_as_current_state(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "AKTUELLER_FORSCHUNGSWEG.md").read_text(encoding="utf-8")
        self.assertIn("# MCM-Wahrnehmungsfeld", readme)
        self.assertIn("## Aktueller Stand S1-LP", readme)
        self.assertIn("Der verbindliche Stand ist S1-LP", roadmap)
        self.assertNotIn("**Kurzstand S1-FC:**", readme)
        self.assertNotIn("Der technische Stand ist W7-BP", roadmap)

    def test_legacy_plans_are_explicitly_non_operational(self) -> None:
        plan = (ROOT / "PRIO_UMSETZUNGSPLAN.md").read_text(encoding="utf-8")
        blueprint = (ROOT / "BAUPLAN_UND_ANWEISUNG.md").read_text(
            encoding="utf-8"
        )
        self.assertTrue(plan.startswith("# Historischer priorisierter Umsetzungsplan"))
        self.assertIn("**Nicht operativ:**", plan[:800])
        self.assertTrue(blueprint.startswith("# Historischer Bauplan"))
        self.assertIn("**Nicht operativ:**", blueprint[:900])
        self.assertNotIn(
            "Dieses Dokument ist die verbindliche Arbeits- und Entwicklungsordnung",
            blueprint,
        )


if __name__ == "__main__":
    unittest.main()

# S2-NY: neutrale Quellen-/Freeze-Bindungsqualifikation

Status: **S2NY_SOURCE_BINDING_QUALIFIED**, 24/24, Exit-Code 0.
ID: `s2ny-source-binding-qualification-20260909-01`.
Genau ein Qualifikationsaufruf, genau ein `unittest -v -f`; kein Retry.

## Auftrag und tatsaechlicher Umfang

Qualifiziert wurde ausschliesslich der private rezeptorfreie NY-Anschluss.
Der unveraenderte NX-Renderer und die reinen NU-Partial-/Phasenfunktionen
werden wiederverwendet; keine historischen Haupteinstiege oder Lernmodule.
Die Funktionsformeln sind nur Metadaten, kein ausfuehrbarer Empfehlungsweg.

Alle 24 vorab inventarisierten Testgruppen wurden erreicht. Siehe
[Vorbindung](../QUALIFIKATIONSBINDUNG.md), [Preregistration](preregistration.json),
[vollstaendiges Testprotokoll](stderr.txt) und [Ergebnis](result.json).
Die sechs neutralen Samples in zwei kleinen Payloads wurden nur zum
Generatorvergleich erzeugt. Keine NY-Payloads, Rezeptoren, NJ-Projektionen,
Empfehlungen, LOCAL-Schaetzungen, Prognosefehler oder Systemaufrufe.

Abgedeckt sind Quellenidentitaet, literale Reihenfolge, native Zeitindizes,
Exaktrezepte mit getrennten Bindungen, Phasen-/Nullpartialpositionen,
lokale Synthesezeit und einmalige Float32-Rundung nach dem Gesamtgain.
Die 18 Prognose- und zwoelf LOCAL-Stellen, Vorstellenbindung der Fehler,
frische Praefixe, getrennte Evaluationswurzel und 20 Kriterien sind als
Metadaten geprueft. Die acht W-Bedingungen bleiben offene Verlustprognosen.

Neutrale Freeze-Belege pruefen Ergebnis-/Pruefbindung, falsche Phase/Profile,
vertauschte Historien, manipulierte State-Digests und die CLOSED-Nachfolge.
Zusaetzlich wurden die zwei realen historischen NX-Freeze-Payloads read-only
importiert und an die bereits vorliegenden Ergebnis-/Verifikationsdigests
gebunden. Keine NX-Lernkettenrechnung, erneute historische Funktionspruefung
oder Wiedereroeffnung geschlossener Owner.

## Integritaet und Grenzen

Alle 17 beobachteten Datei-SHA-256 sind vor/nach dem Test identisch.
Vollstaendige Liste in `result.json`; zentrale neue Bindungen:

| Datei | SHA-256 |
| --- | --- |
| NY-Quellenanschluss | `2d29d9005876c01215133a5a60f4dd2b7dfbeea848d956791814301186d8642d` |
| NY-Bindungspruefer | `2b8fcd5ef8e818c3b6ad2a888e6b5736dc3e4e1298cfb8d5e3531f1dc1bf5796` |
| Testdatei | `a2ee9eef84fd6f600737404741b9d978569c31e327e15e018bf0ad9c31c98a77` |
| Qualifikationseinstieg | `82b758203e1e45cb389e69f85abc16ace356faa10d9515ce9a1cb8eef2b68cf1` |
| Vorversiegelungseinstieg | `9bfd17667a8f8021a664a0e1eabfb923839cbd048f85ead3750c8c4842c1f005` |
| Qualifikationsvorbindung | `f3b13942cef95c197283ba6556fb58e680826a06626cc22a0f564d885866b7a1` |

Ergebnisdigest:
`61f80c33f30574bd5c38c0c19e73fa6be9ba3dfd60f14ccadee6926b0fcb9f91`.
CPython 3.14.4, Windows x64; Built-in-`math` durch `origin == built-in`
und `sys.builtin_module_names` gebunden, keine erfundene Moduldatei.
Interpreter-/DLL-/NumPy-Dateiidentitaeten sind Metadaten; NumPy nicht importiert.

Vollstaendige neutrale Ausfuehrungs-/Evaluations-/Vorregistrierungsformen
bleiben unter 65.536 Byte. Profil-/Ressourcen- und Quellenmanipulationen
werden abgewiesen. Der lesende Pruefer rekonstruiert Quellen und Stellen
unabhaengig; feste Formel-/Budgetmetadaten werden gemeinsam verwendet.

**Nicht qualifiziert:** reale Rezeptorgueltigkeit, kausale Zielzugriffssperre,
Empfehlung, LOCAL-Arithmetik oder spaeterer Funktionsnutzen. Beide Methoden
betreffen dieselbe skalare Struktur: absolute MAE und Gewinndifferenzen sind
spaeter erforderlich; strikte Binary64-Vorteile allein bedeuten keine
allgemeine Robustheit. Keine Toleranz oder positive W-Startbedingung.

Hauptgate durchgehend `False`, ME/MI gesperrt. Historische Belege, fremde
Aenderungen und Bootstrap unveraendert. Diese 24/24 trugen die separat
beauftragte einmalige rezeptorfreie Vorversiegelung, keinen Funktionslauf.

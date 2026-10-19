# Entscheidungsvorlage: kleinster Abhaengigkeitsabbau fuer S2-UC

**Ergebnis: Keine kleine, durch die drei Startstellen begruendete Modultrennung erreicht beide Grenzen.** Ein begrenzter Quellenplan-Reader und das Entfernen eines unbenutzten Imports sind umsetzbar, reichen aber nicht zur Zulassung. Selbst eine idealisierte vollstaendige Entfernung der Exporttabelle reicht nicht. Empfehlung: keinen scheinbar lauffaehigen Minimalumbau freigeben; die Budgetsperre erhalten.

Dies ist ein neuer statischer Entscheidungsbeleg, keine Implementierung und keine Qualifikation. Keine Projektmodule importiert/ausgefuehrt, keine Tests, Quellen, Rezeptoren oder Memorygeschichten ausgefuehrt. Nur Text/AST, Dateigroessen, Hashes und ein ausdrueckliches JSON-Groessenmodell ausgewertet. Die unabhaengige Abnahme des vorherigen Zulassungspakets bleibt offen.

## 1. Belegte Kopplungen und tatsaechlicher Bedarf

| Stelle | Benoetigt / unnoetige Kopplung | Konsequenz |
|---|---|---|
| `mcm_field_organism/__init__.py:11-15,18-29` | Laedt ROOT_ALL und ROOT_LAZY_EXPORTS; Initialisierer wird auch fuer direkte Submodulimporte ausgefuehrt. | Tabelle 258911 Byte bleibt erreichbar. Nur `__getattr__`-Verzoegerung hilft dem vollstaendigen Scanner nicht. |
| `root_lazy_exports.py` | ROOT_ALL allein 42179 LF-Textbytes; ROOT_LAZY_EXPORTS 145680; zusaetzlich ROOT_SURFACE_CLASSES 68478. | Aufteilen in eine weiterhin importierte Root-Namen-/Dispatchtabelle spart nicht genug; diese beiden Zuweisungen allein >131072. Keine Names-/Exportkuerzung zulassen. |
| `_s2uc_source_binding.py:7,60-61` und `_s2uc_run_binding.py:10,40,47` | Nur source_rows sowie Quellenplanpfad/-Digest aus historischem TS-Runner benoetigt. | Reader mit denselben Pinpruefungen abtrennen. TS-Ausfuehrung nicht benoetigt. |
| `_s2ts_temporal_trace_run.py:10-15,41-45` | Runner importiert NU und TS; source_rows braucht davon weder Generator noch Traceklasse. | Runner 10468 + nur dort benoetigtes TS-Modul 5001 Byte entfallen aus S2-UC, wenn beide Verbraucher auf den Reader zeigen. |
| `s2uc_run_bound_once.py:9-13` | Verzoegerter NU-Import fuer WindowSpec und pcm_window bleibt erforderlich. | NU 13635, NP 15138 und seal_inventory 17470 Byte bleiben durch NU -> NP -> seal_inventory erreichbar. Diese 46243 Byte NICHT nochmals als Runnerersparnis abziehen. |
| `_s2uc_resource_ledger.py:4` | `base` wird importiert, aber AST enthaelt 0 Load-Verwendungen. Alle Funktionen nutzen lokale LIMITS/RESERVES. | Importzeile entfernen: 5207 Byte S2-TY-Ledger und 49 Byte Importzeile entfallen; Konstanten/Branches unveraendert. |
| `_s2ty_audio_materialization.py:9-11,65-80`, `_s2nj_private_auditory_output_projection.py:11-12,125-135` | Rezeptor, AuditoryReceptorState/Contact und NJ sind tatsaechlich erforderlich. | Spektral-/Broadbandmodule, relative Baseline-/Audiovertraege sowie NumPy weiter mitrechnen. |
| `_s2nj_private_auditory_output_projection.py:133-134` | SHA-256 der tatsaechlichen `spectral.__file__` wird gegen festes RECEPTOR_SHA256 geprueft. | Eine naive Rezeptorverschiebung mit geaenderten Importzeilen scheitert; keine stille Anpassung von Profil-/Codepins. |

## 2. Konkreter kleiner Vorschlag A (nicht ausreichend fuer Budgetfreigabe)

1. Neues `tools/_s2uc_source_plan.py`: exakt ROOT, SOURCE_PLAN, SOURCE_PLAN_SHA256, source_rows und die beiden vorhandenen Pinpruefungen isolieren; nur hashlib/json/pathlib/typing. In `source-reader-extraction.txt` ist die reine Textauswahl dokumentiert (kein importiertes Modul).
2. `_s2uc_source_binding.py` und `_s2uc_run_binding.py` importieren den neuen Reader weiterhin als `source`. `build`, `manifest`, source_rows-Rueckgabe (rows, plan), Planpfad, Plandigest und Execution-Digest bleiben erhalten. Der Starterzugriff `binding.source.source_rows()` bleibt damit gleich. Keine Aenderung an schedule, IDS, TARGETS oder Planinhalt.
3. Den unbenutzten base-Import in `_s2uc_resource_ledger.py` entfernen. Sonst keine Ledgeraenderung.
4. Historischen TS-Runner und historische Belege unveraendert lassen. Der Reader behaelt Fehlercode und ValueError-Vertrag. Eine Identitaet seiner Fehlerklasse mit der historischen S2TSRunError-Klasse darf ohne zusaetzliche Kompatibilitaetsarbeit nicht behauptet werden; ein Rueckimport zur historischen Klasse wuerde die Einsparung aufheben.

Bilanz A: 477802 - 10468 - 5001 - 5207 - 49 + 976 LF-Textbytes Reader + 256 geschätzte Byte Import-/Kommentarreserve = **458309 Quellbytes (Schaetzung)**. Aktive Reserve um 327237 Byte ueberschritten; allein Quellbytes ueber Shared um 196165 Byte. Pflichtartefakte kommen noch hinzu. Alle anderen 26 bisherigen Projektdateien bleiben erreichbar; neuer Reader kommt hinzu (27 Dateien).

## 3. Warum eine kleine Root-Aenderung nicht genuegt

Die Vorpruefung folgt absichtlich auch verzögerten Imports (`_s2uc_dependencies.py:49 ff.`). `from .root_lazy_exports ...` in eine Funktion zu schieben, spart daher keine gebundenen Quellbytes. Diese Kante im Scanner zu ignorieren waere keine Modultrennung, sondern eine Aufweichung der Vollstaendigkeitspruefung.

Eine echte Trennung waere ein eigenstaendiger kleiner Rezeptorkern ausserhalb des grossen Paketinitialisierers. Betroffen waeren mindestens Materialisierung, NJ, die vier Rezeptor-/Vertragsdateien, neue Paketinitialisierung und Kompatibilitaets-Reexports an den alten Stellen. Klassenidentitaeten, Root-Exports, __all__/dir, Fehlertypen und der spektrale Dateihash muessten erhalten bleiben. Eine reine Reexport-Huelle im neuen Paket, die alte Paketmodule importiert, entfernt die Kante nicht. Dies ist kein belegter kleiner Austausch und wird hier nicht als Umsetzung empfohlen.

Die folgende optimistische Untergrenze schenkt sogar die vollstaendige Entfernung der Tabelle, ohne diesen Umbau bereits als moeglich zu behaupten. Damit ist das Hindernis staerker als eine unsichere Schaetzung der Root-Trennung.

## 4. Vollstaendige Groessenbilanz des optimistischen Modells

477802 - 258911 Exporttabelle - 10468 TS-Runner - 5001 TS-Trace - 5207 TY-Ledger = **198215 Byte** verbleibende 25 Bestandsdateien. Nach Entfernen der 49-Byte-Importzeile mindestens **198166 Byte**, also **67094 Byte** ueber der aktiven Reserve, noch OHNE neue Hilfsmodule.

Dazu Reader 976 LF-Textbytes und pauschal 2048 Byte geschaetzte neue Paket-/Kompatibilitaets-/Scanneranpassungen: **201190 Byte**, aktive Ueberschreitung **70118 Byte**. Die 2048 Byte sind eine explizite Schaetzannahme, kein implementierter/verifizierter Bestand. Vollstaendige Liste jedes verbleibenden Dateipostens und aller externen Laufzeiten: `analysis.json`.

| Shared-Pflichtposten | Byte im Modell |
|---|---:|
| active_dependency_sources | 201190 |
| frozen_source_binding | 19210 |
| dependency_inventory | 5082 |
| qualification_summary | 4265 |
| qualification_protocol | 12538 |
| qualification_budget | 1060 |
| qualification_result | 640 |
| budget_ledger | 1318 |
| terminal_reserve | 16384 |
| **Shared gesamt** | **261687** |

Shared-Modell: **457 Byte unter 262144**, also nur eine knappe, nicht garantierte Modellpassung. Die aktive Grenze wird dennoch um 70118 Byte verfehlt. Metadaten separat: Manifest 24440 + modellierte finale Groesse 4319 = 28759 Byte unter 65536. Die finale Groesse ist weiterhin exakt zu binden, nicht als Reserveobergrenze zu interpretieren.

Die Shared-Zahlen beruhen auf statischer kanonischer JSON-Textlaenge mit 64-stelligen Platzhalterhashes und MODEL_ONLY-Pfaden; keine dieser Bindungen wurde als Datei erzeugt. Summary/Protokoll enthalten 57 deklarierte Test-IDs und Code-/Testreferenzen. Source-Binding 19210 stammt aus der bestehenden historischen Referenz, nicht aus einer neu erzeugten Bindung. Laengere echte Pfade, weitere Tests oder mehr Kompatibilitaetscode koennen die 457 Byte sofort aufbrauchen. Testquellen werden referenziert; ihre Quellbytes sind nach dem bestehenden Schema keine zusaetzlichen aktiven Laufzeitquellbytes. Die bereits eingefrorene NU-Planreferenz folgt der bestehenden Bilanzsemantik; keine neue Anrechnung oder RAM-Aussage wird eingefuehrt.

Diese Untergrenze gilt fuer die untersuchten lokalen Entkopplungen, NICHT fuer beliebige globale Umstrukturierungen. Es ist keine bewiesene Unmoeglichkeit einer kuenftigen kompakteren Implementierung. Eine weitere Einsparung von mindestens 67094 Byte aus dem verbleibenden Bestand (plus Hilfsmodulkosten) ist jedoch unvermeidbar.

## 5. Konkreter neutraler Testplan fuer spaetere Umsetzung

- `test_source_plan_reader_matches_existing_rows_and_pins`: identische rows/plan, SOURCE_PLAN und beide Digests aus dem vorhandenen Plan; keine pcm_window-Aufrufe. Manipulierte neutrale Planfixture prueft SOURCE_PLAN_CHANGED und SOURCE_EXECUTION_INVALID.
- `test_s2uc_binding_unchanged_after_reader_split`: kanonische Manifestbytes, Ereignisse (69), Endpunktverwendungen (58), IDS/TARGETS und erwartete Hintzeitpunkte identisch. Bei build sind die absichtlich geaenderten Codehashfelder separat auszuweisen, nicht durch blindes Gesamtdigest-Gleichsetzen zu verdecken.
- `test_uc_ledger_equal_without_unused_import`: success/failure-Beitraege, absolute Grenzfaelle und Reserveueberschreitungen fuer feste neutrale Zahlen identisch; unveraenderte LIMITS/RESERVES.
- `test_dependency_closure_after_reader_split`: aktualisierten kompletten Importbestand neu messen; TS-Runner/TS-Trace/TY-Ledger fehlen, NU/NP/seal_inventory bleiben. Gegenprobe bei Wiedereinfuegen einer verzögerten Kante muss diese wieder zaehlen.
- Falls spaeter ein Rezeptorkern vorgeschlagen wird: neutrale PCM-Fixtures nur nach gesondertem Umsetzungsauftrag; exakte Binary64-Werte, Profile, Rezeptorhash, NJ-Unterlaufmarkierungen, State/Contact-Klassenidentitaet und Fehlervertraege vor/nachher gleich. Keine realen NU-Fenster fuer diesen Nachweis erzeugen.
- Root-Kompatibilitaet nur bei entsprechender Aenderung: bestehende tests.test_s1pv_lazy_root_manifest und tests.test_s1pv_lazy_root_subprocess einschliesslich __all__, dir und verwendeter Lazy-Exports; Bytehash von spectral.__file__ darf nicht stillschweigend geaendert werden.
- Anschliessend beide S2-UC-Dateien regressiv; Zulassungsgegenproben (synthetisch, unvollstaendig, uebergross) bleiben aktiv. Neuer Abhaengigkeitsbestand UND saemtliche Pflichtartefakte vor jeder spaeteren Zulassungsbehauptung nachmessen. Keine Tests wurden in diesem Analysepaket ausgefuehrt.

## 6. Entscheidung und naechster sinnvoller Auftrag

Kein kleiner tragfaehiger Gesamtumbau ist anhand der drei belegten Stellen nachgewiesen. Vorschlag A ist konkret umsetzbar, bringt aber keine Budgetzulassung; ihn allein als naechsten Laufvorbereitungsschritt freizugeben waere irrefuehrend.

Mein naechster Vorschlag an den Projektanalysten: zuerst ein weiteres enges statisches Paket fuer die noch 67094+ Byte erforderliche Einsparung: Trennung der tatsaechlich gebrauchten NU-Generatorprimitive (WindowSpec/pcm_window samt Funktionen) vom Versiegelungsapparat sowie V6-spezifischer Bindungskern getrennt von historischen Lesepfaden. Beide Risiken und neuen Hilfsmodule vor Umsetzung beziffern. Die 46243 Byte NU/NP/seal_inventory duerfen nur abgezogen werden, wenn kein aktiver Importpfad dorthin verbleibt und die neu benoetigten Generatorbytes hinzugerechnet sind. Keine neue Quellenregel, keine reduzierte Verifikation, keine veränderte Erinnerungsregel als Sparmassnahme.

Der Quellenvergleich bleibt gesperrt. Sein fachliches Ziel und der historische NOT_EVALUABLE-Befund bleiben unveraendert. Alle 29 inventarisierten Produktdateien nach Abschluss erneut gegen die Ausgangshashes geprueft: unveraendert.

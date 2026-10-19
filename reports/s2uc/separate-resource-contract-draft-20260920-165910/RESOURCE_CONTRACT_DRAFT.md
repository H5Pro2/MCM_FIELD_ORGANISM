# Entwurf: getrennte Ressourcenbindung fuer den naechsten S2-UC-Entwicklungsstand

**Status: ENTWURF, NICHT AUSFUEHRUNGSFREIGEBEND.** Nur Vorschlag fuer einen neuen Vertrag/Formatstand V7. Kein neuer Lauf, keine neue finale Laufbindung, keine formale Qualifikation. V6 und alle historischen Vertragsgrenzen bleiben unveraendert; der bestehende reale Einstieg bleibt gesperrt. Unabhaengige Abnahme des bisherigen Zulassungspakets offen. Historischer Lauf unveraendert NOT_EVALUABLE.

## 1. Zweck, Belege und Messstatus

Unveraendert bleibt der Quellenvergleich: unmittelbares Sequenzspeichern versus Behalten nach wiederholter Bestaetigung, einschliesslich beider Erinnerungsgewinne und -verluste. Weder Quellen, Profile, Memoryregeln, Arme, Ereignisfolge noch Erwartungen werden geaendert.

Quellen: [bestehende S2-UC-Bindung](../../../docs/S2UC_QUELLENVERGLEICH_BINDUNG.md), [S2-TY-Ressourcenabgrenzung](../../../docs/S2TY_RESSOURCEN_UND_ANSCHLUSSBILANZ.md), [aktueller Entwicklungsbeleg](../v6-admission-development-20260920-155753/REPORT.md), [negativer Umbauentscheid](../final-split-feasibility-20260920-163154/DECISION.md). Aktuelle Implementierungsstellen: `_s2uc_resource_ledger.py`, `_s2uc_run_entry.py:65-95,98-207`, `_s2uc_run_binding.py:169-313,489-540`, `_s2uc_dependencies.py`.

Erneut statisch gemessen: 29 Laufzeit-Projektdateien = **477.802 Byte**. Dazu die beiden aktuellen S2-UC-Testdateien = **75.073 Byte**. Vereinigung ohne doppelt gezaehlte Pfade: **31 Dateien / 552.875 Byte**. Groessen und SHA-256 stehen in `measured-inputs-and-proposed-limits.json`; alle Laufzeitdateihashes entsprechen dem vorhandenen Inventar. Das sind Dateimessungen, keine Prozessspeichermessungen. Der vorhandene NU-Ausfuehrungsplan hat **44.937 Byte**; er wurde nur gelesen/gehasht, nicht ausgefuehrt.

Alle nachfolgenden Obergrenzen sind VORSCHLAEGE. Planposten sind Reservierungen, keine Behauptung kuenftig gemessener Groessen. Es wurden keine Projektmodule importiert, Tests, Rezeptoren oder Quellen ausgefuehrt.

## 2. Wissenschaftlicher Zustand und Wahrnehmung: unveraendert

| Posten | Grenze / feste Form | Zuordnung |
|---|---|---|
| S2-TW retained / bildend | 2 Vierframe-Slots / 1 Vierframe-Puffer | 8 + 4 = 12 Traceframes |
| S2-UA retained / Kandidat / bildend | jeweils 1 Vierframe-Platz | 4 + 4 + 4 = 12 Traceframes |
| Frame | 48 Binary64-Werte | 384 native Wertebytes |
| Tracewerte je Arm | 12 Frames | 4.608 Byte; beide Arme 9.216 Byte |
| Hintpuffer je Arm | 2 Frames | 768 Byte; beide Arme 1.536 Byte |
| Aktueller NJ-Endpunkt | 1 Halbprofil | 384 native Wertebytes; gemeinsamer Endpunkt beider Arme |
| Roher Rezeptorendpunkt | 1 Profil mit 48 Werten | 384 native Wertebytes |
| PCM | hoechstens 1 Fenster, 4.800 Float32-Samples | 19.200 Byte; keine PCM-Liste |
| Geschichten | 3 frische, nacheinander abgeschlossene Zustaende | keine Addition zur 69-Ereignis-Einzelruntime |
| Pro Geschichte | <=28 Ereignisse, <=20 Formationsframes, <=22 Endpunkte | bestehende Grenzwerte |
| G1 / G2 / G3 | 26/17/26 Ereignisse; 16/12/16 Formationsframes; 22/14/22 Endpunkte | unveraendert |
| Gesamtfolge | 69 Ereignisse, 44 Formationsframes, 14 Hintframes/7 Entscheidungen, 11 Closes, 58 Endpunktverwendungen | unveraendert |

Die genannten gleichzeitig relevanten nativen Werteposten summieren sich konservativ auf **30.720 Byte** (9.216+1.536+384+384+19.200). Das ist KEINE neue Gesamtzustandsgrenze: Objekt-/Referenzverwaltung, Receipts und NumPy-Arbeitsarrays sind darin nicht enthalten. Zwei Referenzen auf denselben NJ-Endpunkt erzeugen keine zwei weiteren Kopien seiner Werte; tatsaechliche Kopien muessen als Runtime-Puffer gesondert erfasst werden. Kandidaten bleiben fuer Hints unzugaenglich, Hints read-only, Quellenverwendungen nicht dedupliziert.

Rezeptor-/FFT-Raum separat: der historische S2-TY-Beleg nennt **979.592 Byte Konfiguration** und **mindestens 1.939.992 Byte FFT-Arbeitsarrays**. Das sind uebernommene statische Ansatzwerte der damaligen Implementierung, keine aktuelle Peakmessung und keine bewiesenen Obergrenzen. Pythonobjekte, NumPy-Temporaries, Codec-Kandidaten, geladenes JSON und Bibliotheken verbleiben im offenen Laufzeitkonto.

Keine Uebernahme der alten S2-TY-Einzelruntime-/98.304-Byte-Huelle als neue S2-UC-Zustandsfreigabe. Die bestehenden S2-UC-Framegrenzen bleiben massgeblich.

## 3. Eigenes endliches Projektcodebudget

**Neue Grenze C = 655.360 Byte (640 KiB).** Sie umfasst jeden transitiv benoetigten Projektquelltext des realen Starters, seiner Pruefer und der gebundenen neutralen Tests, inklusive Paketinitialisierer, verzögerter Importe und verwendeter Lazy-Exports. Testdateien koennen damit nicht aus der Rechnung verschwinden. Gleicher kanonischer Pfad wird einmal gezaehlt; zwei verschiedene tatsaechliche Dateien mit gleichen Inhalten werden beide gezaehlt. Symlinks/Aliase duerfen Vollstaendigkeits- und Hashpruefungen nicht umgehen.

Begruendung: aktueller gemessener Bestand **552.875** + explizite technische Entwicklungsreserve **98.304 (96 KiB)** = **651.179 Byte**; auf die naechste 32-KiB-Stufe begrenzt ergibt **655.360**, Rest **4.181 Byte**. Gesamter Spielraum **102.485 Byte**, rund 18,5 % des gebundenen Bestands. Diese Reserve ist eine bewusste technische Vertragsentscheidung fuer neue Ledger/Validatoren und Gegenproben, keine aus der Memoryfunktion abgeleitete Notwendigkeit. Sie waechst nicht automatisch mit dem Code. Jede weitere Erhoehung waere eine erneute ausdrueckliche Vertragsaenderung.

Vor einer spaeteren Bindung ist die Vereinigung der Laufzeit- UND Testimportmengen erneut vollstaendig zu ermitteln; neu gefundene Dateien gehen zusaetzlich in C ein. Die jetzigen 31 Dateien sind der gemessene Planungsstand, keine Freigabe fuer ungescannte zukuenftige Testimporte. Alte _ACTIVE-Teillisten sind kein Zulassungsnachweis.

Externe Python-/NumPy-Laufzeit: getrennte Modul-/Distributionsidentitaeten mit Version, Interpreteridentitaet und geeignetem Installations-/Dateinachweis binden. Ihre installierten Bibliotheksbytes und ihr RAM gelten nicht als Null; sie sind ausdruecklich ausserhalb der **Projekt**quellbytegrenze. Der Artefaktvertrag ist somit keine Gesamtdisk- oder Prozessspeichergarantie.

## 4. Artefaktklassen und eindeutige Zuordnung

| Konto | Vorgeschlagene Grenze | Inhalt / Regel |
|---|---:|---|
| C Projektcode | 655.360 | Vollstaendige Projektquelltexte und gebundene Tests; aus Shared herausgeloest |
| M Metadaten | 65.536 | Vollstaendig serialisiertes Manifest einschliesslich Huelle und finale kompakte Bindung; interne Feldkopien in einem Record gehoeren zu R |
| B statische Shared-Unterklasse | 196.608 | Alle unten gelisteten Quellen-/Qualifikations-/Vertragsbelege, ohne Projektquelltexte |
| S Shared gesamt | 262.144 | B plus gleichzeitig bestehende Fehler-/Terminaldateien |
| R Record | Reserve 245.760; absolute Grenze 262.144 | Ein veroeffentlichter Erfolgs- ODER Fehlerrecord; Reserve und absolute Grenze unveraendert, beide pruefen |
| V Verifikation inkl. fachlicher Auswertung | Reserve 131.072; absolute Grenze 262.144 | Ein eigenstaendiger serialisierter Verifikations-/Auswertungsbeleg; auch nach spaeterem Fehler vorhandene Datei weiterzaehlen |
| E Fehlerbeleg | 16.384 je Lauf | Unterklasse von S; nie mit T alternativ wegkuerzen |
| T normaler Terminalbeleg | 16.384 | Unterklasse von S; volle Dateigroesse einschliesslich Huelle/Referenzen |
| Tmin Minimalabschluss | 16.384 | Unterklasse von S; falls T noch existiert, T UND Tmin zaehlen |
| W Publikations-Staging | 245.760 | Neues, explizites Gesamt-Unterkonto fuer maximal eine temporaere Ausgabedatei; keine RAM-Behauptung |
| G gebundener Code-/Artefakt-/Staging-Gesamtumfang | 4.194.304 | C + M + S + R + V + W; kein Codeverlust aus der Gesamtrechnung |

Die Groesse ist immer die tatsaechliche Bytezahl der konkreten kanonischen Datei, nicht Zeichenanzahl oder komprimierte Vorstellung. Der alte Feldname final_binding_reserve bleibt, falls im neuen Schema weiterverwendet, **exakte Dateigroesse**, keine Obergrenzenreserve. Reservierungen und Istwerte sind getrennte Felder; kein Ausgleich einer lokalen Ueberschreitung durch freie andere Konten.

**Explizite Formatentscheidung im neuen Entwurf:** Die bisher im Terminal eingebetteten technical/evaluation-Daten werden als eigener V-Beleg gespeichert; T enthaelt deren Groesse/Hashreferenz. So wird physisch gespeicherter Inhalt eindeutig genau einer Hauptklasse zugerechnet, waehrend der Terminal seine volle 16-KiB-Grenze behaelt. Keine Aenderung der fachlichen Pruefung; dies ist eine neue Serialisierungsform und muss separat neutral qualifiziert werden. Die bisherige konservative gleichzeitige Anrechnung eingebetteter Verifikation und voller Terminaldatei wird nicht stillschweigend weiterverwendet oder als neue Istbilanz ausgegeben. Offen ausgewiesene Folge: Bisher begrenzt die 16-KiB-Terminaldatei faktisch auch den eingebetteten Verifikationsteil. Im neuen Format kann V seine bestehende 131.072-Byte-Reserve eigenstaendig nutzen. Diese Aenderung der effektiven Serialisierungskapazitaet ist Teil des vorgeschlagenen neuen Vertrags, keine unveraenderte V6-Eigenschaft.

Statische B-Planposten:

| Beleg | Eigene Planobergrenze |
|---|---:|
| Unveraenderter NU-Ausfuehrungsplan | 65.536 (gemessen 44.937) |
| Eingefrorene Quellenbindung | 24.576 (historische Referenz 19.210, vor Neubindung neu messen) |
| Vollstaendiges Abhaengigkeitsinventar inkl. Runtimeidentitaeten | 16.384 |
| Qualifikationszusammenfassung | 16.384 |
| Vollstaendiges Testprotokoll mit IDs | 32.768 |
| Qualifikationsbudget | 8.192 |
| Qualifikationsergebnis | 4.096 |
| Finaler Ressourcenledger | 8.192 |
| Maschinenlesbarer neuer Ressourcenvertrag | 8.192 |
| **Summe Planobergrenzen** | **184.320** |
| **Verbleibender B-Spielraum** | **12.288** |

Diese Planobergrenzen sind neue ausdrueckliche Teilobergrenzen, keine gemessenen Istgroessen. B muss zusaetzlich <=196.608 bleiben. Jeder weitere geladene/bindende Projektbeleg muss registriert, gehasht und in B gezählt werden; unbekannte Belege werden abgewiesen. Keine Umgehung durch sidecar-Dateien. Die vorhandene NU-Plandatei wird hier ausdruecklich mitgezaehlt, nicht nur ihr Pfad/Hash im Quellenbinder. Codehash-Referenztexte in Inventaren belegen deren eigene Serialisierungsbytes in B; die Quelldateien selbst nur C.

## 5. Vollstaendige Abschlussalternativen

Die folgende Tabelle verwendet pessimistisch C=655.360, M=65.536, B=196.608 und W=245.760. Die Istbilanz nimmt jeweils tatsaechlich vorhandene Dateien. Erfolg und Fehlerverlauf sind alternative Laeufe; innerhalb eines Fehlerverlaufs vorhandene Dateien sind gleichzeitig, nicht alternativ.

| Abschluss | S | R | V | W | G einschl. C+M |
|---|---:|---:|---:|---:|---:|
| Erfolg: B+T | 212.992 | 245.760 | 131.072 | 245.760 | 1.556.480 |
| Fehler vor erster Recordpublikation: B+E+T | 229.376 | 0 | 0 | 245.760 | 1.196.032 |
| Fehler nach Recordpublikation: B+E+T | 229.376 | 245.760 | bis 131.072 | 245.760 | 1.572.864 |
| Minimalfallback bei noch vorhandenem T: B+E+T+Tmin | 245.760 | bis 245.760 | bis 131.072 | 245.760 | 1.589.248 |

V darf nach Publikation nicht auf 0 gesetzt werden, nur weil eine spaetere Auswertung/Terminalpublikation scheitert. Vor Publikation einer Verifikation wird ihr Kandidat nur als Runtimewert bzw. im Staging gezaehlt; publizierte Teil-/Fehlerdateien duerfen nicht verschwinden. Bei einem Fehler vor Recordpublikation wird kein neuer verkleinerter Record erzwungen: nur E/T beziehungsweise Fallback, keine nachtraegliche Aussage COMPLETE/VERIFIED.

Selbst bei allen reservierten Hauptklassengrenzen (S=262.144) ergibt G **1.605.632**, unter 4.194.304. Das ist eine prospektive Budgetrechnung, kein erfolgreicher Laufnachweis. R/V-Reserven bleiben die strengeren Publikationsschranken; die absoluten Grenzen werden zusaetzlich getestet.

Staging: Kandidat vor Dateipublikation auf Reserve und absolutes Limit pruefen; hoechstens eine .tmp-Datei bis W, auch bei Write-Failure nachmessen. Vor der naechsten Stagingdatei vorhandenes .tmp bereinigen oder den Abschluss als nicht vollstaendig publizierbar melden. Keine zweite temporaere Datei ausserhalb von W anlegen. Ist Bereinigung/Schreiben unmoeglich, Fehler und fehlende Dauerbelege explizit melden, keine erfolgreiche Budget-/Abschlussbehauptung. Ein im RAM uebergrosser Codec-Kandidat ist kein erlaubter Record und gehoert zum offenen Prozesskonto.

## 6. Gegenueberstellung alt / neu

| Aspekt | Bestehende Bindung | Neuer Entwurf |
|---|---|---|
| Wissenschaftliche Slots/Frames/Hints/Ereignisse | feste S2-UC-Form | identisch |
| Aktive Bindungen/Projektquellbytes | 131.072 Reserve; Code zusaetzlich in Shared | eigenstaendiges C=655.360, inkl. Testquellen; alte Reserve NICHT umbenennen |
| Shared | 262.144, bisher Code-/Belegmischung | 262.144 bleibt; nur Belege, B<=196.608, explizit inkl. NU-Plan und neuem Vertragsbeleg |
| Record / Verifikation | Reserven 245.760 / 131.072; absolute Grenzen je 262.144 | unveraendert |
| Terminal / Fehlerbeleg | 16.384 je Beleg | unveraendert; gleichzeitig Vorhandenes explizit addiert |
| V innerhalb T | konservativ doppelte logische Anrechnung moeglich | neuer separater V-Beleg + Hashreferenz in T; neue Formatqualifikation erforderlich |
| Staging | kein expliziter Gesamtposten | eigenes W<=245.760, in G enthalten |
| Gesamt | 4.194.304 in bisheriger gemischter Bilanz | gleicher Zahlenwert, aber ausdruecklich C+M+S+R+V+W; Vertragssemantik geaendert |
| Laufzeit/RAM | Peak offen, keine Ableitung aus Codebytes | bleibt separat offen; keine Behauptung einer RAM-Zulassung |

Dies ist eine bewusste prospektive Vertragsaenderung. Sie macht weder V6 noch V14 oder einen historischen NOT_EVALUABLE-Lauf nachtraeglich gueltig. Weder die alten Limits-Dictionaries noch alte Ergebnisdateien werden ueberschrieben.

## 7. Separates Runtimekonto

Vor spaeterer realer Zulassung muss ein eigener Runtimebeleg Interpreter/NumPy, Basisprozess, Rezeptorinitialisierung, Materialisierung, Codec, Reload/Verifikation und terminalen Fehlerpfad unterscheiden. Native rechnerische Puffer, Messwerte und unbekannte Anteile separat markieren; nicht Quellbytes in RSS umrechnen. RSS/Commit-Spitze, Pythonobjekte und NumPy-Temporaries bleiben derzeit UNKNOWN. Dieser Entwurf setzt dafuer keine erfundene endliche Obergrenze und gibt keinen realen Lauf frei. Ein nachgelagerter neutraler Messauftrag muesste Messmethode, Umgebung, Messluecken und gegebenenfalls eine begruendete Prozessgrenze festlegen.

## 8. Unmittelbar umsetzbarer Entwicklungsplan nach Beauftragung

1. **Neues versioniertes Ledger**, etwa `_s2uc_resource_contract_v7.py`: rein funktionale Klassifikation und Nachrechnung C/M/B/S/R/V/E/T/Tmin/W/G; feste Konfiguration mit Vertrags-ID und Digest; jede Datei exakt einem Hauptkonto zuordnen, Unterkonten nicht nochmals in G addieren. Alte `_s2uc_resource_ledger.py`-Semantik fuer V6 unveraendert erhalten.
2. **`_s2uc_dependencies.py`**: feste Einstiegs- plus Qualifikationstest-Wurzeln, komplette transitive/relative/verzoegerte Importmenge und Paketinitialisierer; kanonische Pfade, doppelte Pfade/unerlaubte Aliasierung, fehlende Dateien und veraltete Hashes abweisen. Projektcode und externe Runtime getrennt binden. Bei unsicherer dynamischer Aufloesung geschlossen bleiben.
3. **`_s2uc_run_binding.py`**: neuer strikt versionierter V7-Validator mit `resource_contract_ref`, `purpose` und separaten Ist-/Reservefeldern. Keine automatische Migration. V6 bleibt unter seinen bisherigen Grenzen. Synthetische/DRAFT-Belege nie zur Zulassung nutzen. Vollstaendigkeit, Codebudget, alle Qualifikationsinhalte und Klassensummen vor Supplier/Gate/Ausgabeordner pruefen. Fehlercodes je Grenze, fehlender Abhaengigkeit und Unterzaehlung unterscheiden.
4. **`_s2uc_run_entry.py`**: fuer den neuen Pfad den vollstaendig zugelassenen Inventarsnapshot verwenden, nicht _ACTIVE. Neues V-Artefakt atomar publizieren und per Hash wieder referenzieren; Record weiterhin vor Publikation pruefen und danach erneut lesen/verifizieren. Alle vorhandenen Dateien bei jedem Fehlerabschluss inventarisieren; E/T/Tmin/V/R plus .tmp nachmessen. Primärfehler erhalten, Bewertung sperren, Gate im finally schliessen.
5. **`s2uc_run_bound_once.py`**: keine Defaultumschaltung auf neue Laufbindung; neuer Formatpfad ausschliesslich mit spaeter separat gueltiger Bindung und ausdruecklicher Autorisierung. Im Entwicklungsauftrag nur neutrale Fixtures/gesperrte Vorpruefungen. Dieser Entwurf selbst ist niemals Starterinput.
6. **Tests erweitern**, nachfolgende Matrix vollstaendig implementieren; dann beide S2-UC-Suiten neutral regressiv ausfuehren. Code-/Testhashes vor/nach, komplette Test-IDs, Exitcode, Komponenten- und Gesamtsummen sichern. Das waere Entwicklungsevidenz, noch keine formale Qualifikation oder unabhaengige Abnahme.

## 9. Neutrale Abnahmematrix fuer die Umsetzung (hier nicht ausgefuehrt)

- `test_v7_code_union_counts_runtime_and_tests_once`: bekannte kleine Tempdateien, transitive/verzoegerte/relative Kanten, gemeinsame Pfade; unterschiedliche Dateien gleichen Inhalts beide zaehlen. Inventar nur mit passenden Hashes, aber fehlender Abhaengigkeit, muss scheitern.
- `test_v7_code_limit_equal_and_plus_one`: 655.360 angenommen, 655.361 abgewiesen; neuer Code-/Testbestand nicht gegen alten 131.072-Posten verrechnen. Keine reale Codeausfuehrung notwendig.
- `test_v7_item_and_branch_undercount_with_refreshed_digests`: Code-, Plan-, Qualifikations-, Record-, V-, E-, T-, Tmin- und W-Posten um ein Byte verkuerzen; korrigierte Hashreferenzen/Summen duerfen Herkunftsabweichung nicht verdecken. Fehlende/doppelte/negative/nichtganzzahlige Posten und unbekannte Kategorien ablehnen.
- `test_v7_local_caps_and_total`: jede Grenze exakt/+1, B- und S-Summen unabhaengig pruefen. Da die realen Klassenmaxima G nicht ausschöpfen, zusaetzlich rein funktionaler Ledger-Test mit testlokal kleinerem Gesamtlimit, um die G-Addition nachzuweisen; kein vom Starter erreichbarer Testschalter.
- `test_v7_reserve_distinct_from_absolute`: Record 245.761 bzw. V 131.073 bereits wegen Reserve ablehnen, obwohl absolute 262.144 noch nicht erreicht; absolute Schranke ebenfalls separat belegen.
- `test_v7_three_closures_and_minimal_coexistence`: Erfolg, Fehler vor R, Fehler nach R/V, bestehendes T plus E und Tmin; exakt vorhandene Belege zaehlen, V bei spaeterem Fehler nicht verlieren, keine Erfolgsauswertung im Fehlerfall.
- `test_v7_staging_write_and_cleanup_failure`: Teil-.tmp, Renamefehler und fehlgeschlagene Bereinigung; Ist-W erfassen, keine unbudgetierte zweite Datei, fehlenden Dauerabschluss melden, Primärfehler erhalten.
- `test_v7_preflight_keeps_supplier_gate_output_closed`: alle Vorpruefungsfehler am echten Starter: Supplier=0, Gate=False, kein Ausgabeordner. Keine Mockumgehung der Zulassung.
- `test_v7_draft_synthetic_and_legacy_not_admitted`: dieser Entwurf, synthetische Belege, falsche Vertrags-ID/Version und Versuch, alte V6-Bindung mit neuen Limits zu laden, scheitern. V6-Budgetsperre und historische Lesbarkeit bleiben erhalten.
- `test_v7_scientific_binding_unchanged`: Manifest, Plan-/Profilpins, Slots/Frames, Ereignisse, Endpunktverwendungen und TARGETS unveraendert; reine statische Vergleiche plus spaeter autorisierte neutrale Materialisierungsregression, keine realen NU-Quellen.

## 10. Entscheidungsvorschlag und Abschluss

Vorschlag an den Projektleiter: diesen Vertrag als Grundlage eines begrenzten neutralen Implementierungspakets pruefen, mit neuer Version und unveraenderter alter Sperre. Der erste Umsetzungsschritt ist das reine neue Ledger samt Grenz-/Unterzaehlungstests; danach Bindung und Abschlussformen anschliessen. Keine weitere Modultrennung zum Schrumpfen des Projektcodes.

Offen bleiben die unabhaengige Abnahme des vorhandenen Zulassungspakets, die Abnahme eines kuenftig implementierten neuen Vertrags und der Prozessspeichernachweis. Dieser Entwurf schliesst nur die beauftragte statische Ausarbeitung ab.

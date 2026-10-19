# Erfahrungsvergleich: neutrale Anschlussqualifikation

**QUALIFIED, 22/22**, genau ein Aufruf, 18,476 Sekunden. Keine Fehler,
keine übersprungenen Prüfungen, Quellenhashes vor/nach identisch.
Repository-Bezug `537109994cf777f8d36cda617aafe12226806c25` plus das
unveränderlich gespeicherte aktuelle [Codeinventar](inventory.json).
Historische Qualifikationen wurden nicht wiederholt oder als neue Passzahlen
übernommen. Kein reales Medium geöffnet und kein Decoder gestartet.

## Implementierter Anschluss

- `_experience_comparison.py`: zwei getrennte native Instanzen und Owner,
  einmalige gemeinsame aktuelle Eingänge, unveränderte Halbprofilmechanik,
  ALL_BANDS_24 und bestehende Direktbaselines.
- `_experience_verification.py`: unabhängige Zustands-/Transaktions-,
  Generations- und Scanprüfung aus gespeicherten Belegen. Keine erneute
  Formation, Feldfortschreibung oder Rezeptorberechnung.
- `_experience_entry.py`: privater, standardmäßig gesperrter Einmaleinstieg.
  Der Decoder-/Materialisierungsweg bleibt der bestehende UHD-Anschluss;
  keine neue Bedienoberfläche und keine Quellenproduktion.
- `run_experience_comparison_once.py`: vorgebundener einzelner Testaufruf
  und separate Erstellung der noch nicht autorisierten realen Bindung.

Frisch: lokale Ordinale 1..14 bei gemeinsamen Zeitpositionen 11..24.
Beide Arme erhalten identische aktuelle Modalitätsfenster, Operationen und
Quellenbelege. Der erste frische Feldschritt umfasst ausdrücklich
`[0, 2.100.000.000)` ns, einschließlich leerer Vorlaufzeit; es gibt weder
vorgeschaltete Kontakte noch einen künstlich vorgealterten Memoryzustand.
Die aktuellen Kontakte selbst liegen unverändert an der gemeinsamen Zeit.
Feldtrajektorien werden nicht gleichgesetzt. Ablaufalter bleibt an tatsächliche
Formationen gebunden; frühere erfahrene Spuren werden nicht verjüngt.

Herkunft wird je Slotgeneration über tatsächlich belegte Aktualisierungen
geführt. CREATED/REPLACED beginnen eine neue Kette, MATCHED ergänzt sie,
CLEARED/FREE entfernen sie. Reine Zielherkunft, gemischte, andere und fehlende
Herkunft werden getrennt dargestellt. Gleiche Datei allein zählt nicht als
passender Abruf. Gemischte Zulassung ist kein bestätigter Zielgewinn und
ebenso wenig automatisch eine semantische Fehlzuordnung.

## Tatsächlich erreicht

| Neutraler Hauptfall | Erfahren | Frisch | Gemeinsam |
|---|---:|---:|---:|
| Ereignisse | 24 | 14 | 38 |
| Formationen | 20 | 10 | 30 |
| Hinweise | 4 | 4 | 8 |
| Feldkontakte | 7.392 | 4.032 | 11.424 |
| Scanbelege einschließlich Direktbaseline | 8 | 8 | 16 |
| Status nach Abschluss | CLOSED | CLOSED | RECORDING_COMPLETE |

Der neutrale Lieferant wurde genau 24-mal aufgerufen, nicht nochmals für den
frischen Arm. Synthetische Rezeptorendpunkte, keine realen PCM-/RGB-Payloads.
Hinweise sind unverändert read-only, beide Scanimplementierungen stimmen
überein. Die unabhängige Prüfung des gespeicherten JSON wurde einmal erreicht.
An allen vier Kontrollen ergeben beide Arme `ABSTAIN_INTERNAL_AMBIGUITY`:
gültiger negativer Vergleich, keine Gewinne oder Verluste. Das ist keine
Prognose für das reale Video.

Separat geprüft: Nullzustands-/Instanztrennung und wiederholtes close,
Materialisierungsfehler nach einer erreichten Formation, unzulässige Position,
Profilmanipulation, Auswertungssperre, unveränderlicher Manifesttyp,
Herkunftsergänzung und Ersetzung, getrennte Gewinn-/Verlustflags, geschlossener
Haupteinstieg, Ablehnung eines neutralen Lieferanten im Medienmodus,
Budgetgleichstand und Überschreitung sämtlicher gemeinsamer Klassen.
Die aktuelle Qualifikation ist keine erneute Decoder- oder Rezeptorqualifikation.

Zusätzliche unabhängige Verifikationsarbeit im nativen Hauptfall: 30
Formationsprüfungen, 126 Zustandsvalidierungspässe, 9.408 Fast-Rangterme,
8.736 PPB-Auswahlterme, 20.160 Updatekomponenten, 3.920 Scanvergleiche.
Diese Arbeit ist nicht als zusätzliche operative Erfahrung gezählt.

## Belegbudget

Ausdrücklich neues privates Profil `EXPERIENCE_COMPARISON_24M_V1`.
Keine Änderung historischer oder einzelner nativer Beleggrenzen.

| Klasse | Gemeinsame Vorreservierung | Grenze |
|---|---:|---:|
| Gesamt | 20.619.300 | 25.165.824 |
| Metadaten einschließlich vollständiger Logs/Abschluss | 1.048.576 | 3.145.728 |
| Quellenbelege | 59.428 | 524.288 |
| Zusatzhülle | 434.212 | 786.432 |
| Verifikation | 262.144 | 262.144 |

Die Bilanz umfasst erhaltene Qualifikation, geplantes reales Ergebnis und
eine temporäre Publikationskopie. Erfolgs- und Fehlerabschluss sind Alternativen.
Je 131.072 Byte für neutralen und künftigen realen Verifikationsbeleg teilen
sich die eine gemeinsame Verifikationsgrenze. Keine doppelte Gesamtfreigabe.

Ist nach Test, vor Bericht/abschließender Bilanz: nativer Gesamtbeleg
1.670.795 Byte, unabhängige Verifikation 22.811, Auswertung 66.582,
vollständiges Testlog 2.479. Qualifikationsdateien einschließlich result.json:
1.780.539 Byte. Reale Vorbindung: 7.350 plus 1.775 Byte Budgetdatei.
Fünf neue aktive Quell-/Test-/Aufrufdateien: 46.396 Byte; Inventar 13.032
bereits physisch in der Qualifikation enthalten, nicht nochmals zählen.

Vorhandene Softwarevoraussetzungen bleiben im transitativen Pfad-/Byte-/Hash-
Inventar gebunden und werden nicht in die Belegablage kopiert. Dies folgt der
bestehenden Software-/Belegklassifikation, nicht einer Löschung von Abhängigkeiten.
Bericht und abschließende Bilanz liegen in der gemeinsamen Metadatenreserve.
Die Reservierung ist eine endliche Ausgabebegrenzung, keine Garantie beliebig
großer Fehlerprotokolle. Tatsächliche Medienwerte wurden nicht vorweggenommen.

Wichtig zur physischen Mehrfachablage: Die zwei nativen Armbelege enthalten
**34** NJ-Quellenbelege (22 plus zwölf), obwohl nur 22 Projektionen erzeugt
werden. Die 32.768-Byte-Zeile ist eine Byte-Reserve, keine Behauptung von
32 Projektionen oder Belegen. Die geschlossene Quellenbelegform hat höchstens
839 kanonische Byte: feste Digestfelder plus beide maximalen Listen mit allen
48 Bandindizes. Damit benötigen 34 Belege höchstens 28.526 Byte. Es werden
keine fehlenden numerischen Rohwerte rekonstruiert. Tatsächlich: 19.234 Byte.
Diese Größenherleitung ist administrative Syntaxarithmetik, keine weitere
Rezeptorprüfung oder wiederholte Verifikation.

Weitere Istklassen des nativen Belegs: 32 Zustände 1.087.903 Byte, 38 Eingänge
170.331, 38 Schritte 104.288, 16 Scans 219.250, 30 Formationsbelege 32.844,
30 Generationsbelege 17.321 und 19.624 Byte Restmetadaten. Beide Nullzustände
und alle physisch doppelt gespeicherten aktuellen Eingänge sind mitgezählt.

## Finale Vorbindung und Grenzen

Vorgesehene, nicht verbrauchte ID `experience-comparison-real-20260919-01`.
[Bindung](../experience-comparison-real-20260919-01-binding/binding.json), SHA-256:
`d1d7e195e65b184f55f03b46ad483171f3abd5a17e2723844182a423e868a7e3`.
`authorized=False`, Ausgabe bei Bindung abwesend. Keine reale Ausführung.

Präregistrierung SHA-256:
`58234adc5ef78c8c05b40c3b71201be5930d83a2ab3d3ffb516bd388a55c8b43`.
Quelleninventar SHA-256:
`0ec8626fea900dfe373d1b60cddf03c8fedcc7b4df225322de153ed4f1c81937`.

Realer Decoder-/Dateizugriff und dessen Fehlerfälle wurden hier nicht erneut
ausgeführt. Die Gateöffnung und reale Vergleichsausführung brauchen eine
separate Freigabe. Keine Memoryregel, Maske, Medienwahl oder UI geändert;
ME/MI bleiben gesperrt, Prognosezweig ruhend. Ein späterer Unterschied wäre
nur ein Befund zu diesen vier Kontrollen auf bereits untersuchtem Material.

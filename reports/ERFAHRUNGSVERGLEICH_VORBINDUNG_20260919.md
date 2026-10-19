# Erfahrener gegen frischen Arm: Vorbindung und Budgetvorabstopp

Auftrag: aktuelle Workflow-Übergabe „Den aktuellen Erfahrungsvergleich
fortsetzen“, 19.09.2026. Bezugs-HEAD:
`537109994cf777f8d36cda617aafe12226806c25`, bereits veränderter Arbeitsbaum.
Keine historischen Prüfungen wiederholt. Keine Projektimporte, Rezeptoren,
Decoder, Memory- oder Feldaufrufe. Nur Codelektüre und Reservearithmetik.
Keine Laufnummer vergeben; die einmalige neutrale Qualifikation ist unbenutzt.

## Identität und Umfang

Der neue Auftrag ist nicht der historische 14/14-Medienanschluss. Er umfasst
zwei getrennte Zustände und einen kausalen Vergleich bei gleichen aktuellen
Eingaben. Der Checkpointzweig bleibt geschlossen.

| Arbeit | Erfahren | Frisch | Gemeinsam |
|---|---:|---:|---:|
| Ereignisse | 24 | 14 | 38 |
| Formationen | 20 | 10 | 30 |
| Audiohinweise | 2 | 2 | 4 |
| Visualhinweise | 2 | 2 | 4 |
| Feldkontakte | 7.392 | 4.032 | 11.424 |
| Scanbelege einschließlich Direktbaseline | 8 | 8 | 16 |

Ein gemeinsamer Materialisierer: 22 Audioanalysen, 22 NJ-Projektionen und
22 visuelle Analysen im späteren Lauf. Aktuelle Ergebnisse werden beiden Armen
unveränderlich bereitgestellt; keine zweite Analyse für den frischen Arm.
Zwei Medienpassagen, keine dritte Dekodierung für den frischen Arm. Physischer
Decoderverbrauch bleibt ein gemeinsamer Zähler, nicht je Arm ein neuer Vorrat.
Quelle bleibt die bereits untersuchte lokale MP4 aus dem Plan; sie wurde hier
weder geöffnet noch erneut gehasht.

## Kleinster Zeit- und Herkunftsanschluss

Gemeinsame aktuelle Ereignisse sind die Positionen 11 bis 24 der historischen
Auswahl. Frischer lokaler Ordinal 1 bis 14 entspricht jeweils globaler
Zeitposition 11 bis 24. Die Rezeptorwerte, Audio-/Visualfenster und aktuelle
Hinweiswerte müssen identisch sein; lokale Ereignis- und Ownerbindungen sind
armgetrennt. Kein Voraltern des frischen Memoryzustands durch erfundene
Formationen. Ablaufalter weiterhin aus tatsächlichen Formationsschritten,
nicht aus einer neu eingeführten Uhr oder Wartezeit.

`_s2ob_private_caller_binding.expected_times()` (Zeile 90), `bind_input()`
(273) und `_s2ob_private_caller_verification.source_receipt()` (12) binden Zeit
derzeit an den lokalen Ordinal. Einfaches Umnummerieren erzeugt daher andere
Zeitbindungen. Nötig wäre ein eigener privater Anschluss mit expliziter
lokaler Ordinal-/globaler Zeitpositionsbindung und entsprechender unabhängiger
Prüfung. Historische Validatoren dürfen dabei nicht gelockert werden.
Der frische erste Feldkontakt braucht zusätzlich eine ausdrücklich geprüfte
Behandlung der Anfangslücke; ein bereits fortgeschriebener Feldzustand darf
nicht als frischer Nullzustand ausgegeben werden. Noch nicht implementiert.

Auswertung vorab konservativ: Zu jedem Hinweis gehört ausschließlich die
entsprechende Fensterposition 2 beziehungsweise 8 beider Passagen als
vorgebundene Zielherkunft. Gleiche Datei allein genügt nicht. Herkunft muss
aus tatsächlichen CREATED/REPLACED/MATCHED-Transaktionen fortgeschrieben
werden: Neubelegung beginnt eine Herkunftskette, MATCHED ergänzt sie,
Ersetzung oder Freigabe beendet die alte Kette. Die bisherigen `births`
allein erfassen keine Prototypvermischung
(`_s2oa_private_runtime_binding.generation_step`, Zeile 106).

Nur vollständig belegte, ausschließlich zur gebundenen Fensterposition
gehörende Aktualisierungsketten zählen als reine Zielherkunft. Beteiligung
anderer Fenster wird als gemischt separat berichtet, nicht automatisch als
richtiger Abruf. Fehlende Herkunft bleibt unbestimmbar. Bereich, Generation,
Kandidatenmenge, Enthaltung und Wertegleichheit bleiben getrennte Merkmale.
Diese experimentelle Herkunftszuordnung behauptet keine Objektidentität.

## Konkreter Konflikt der bisherigen Vorabsicherung

Bestehende Grenzen: `_s2oe_media_binding.SESSION_LIMITS` (Zeile 13) übernimmt
die Gesamtgrenze 4.194.304 Byte und Verifikation 262.144 Byte aus
`_s2ob_private_caller_binding.LIMITS` (29). Metadaten 131.072, Quellen 327.680,
gemeinsame Zusatzhülle 393.216 Byte. Das größere private Checkpointprofil gilt
nicht automatisch für diesen Vergleich.

Die bisherige strukturelle Vorprüfung reserviert Einzelmaxima aus
`_s2oc_shared_verification.CAPS` (9) mit `synthetic_forms()` (21).
Bereits mit günstiger gemeinsamer Ablage des identischen Nullzustands und
aller gemeinsamen Eingangsbelege ergibt dieses Verfahren:

| Klasse | Anzahl × Einzelreserve | Byte |
|---|---:|---:|
| Zustände, Nullzustand nur einmal | 31 × 98.304 | 3.047.424 |
| Eingänge, aktuelle Eingänge nur einmal | 24 × 16.384 | 393.216 |
| Schritte beider Arme | 38 × 16.384 | 622.592 |
| Scans einschließlich Direktbaselines | 16 × 32.767 | 524.272 |
| NJ-Belege gemeinsam | 22 × 1.024 | 22.528 |
| Formationsbelege | 30 × 1.536 | 46.080 |
| Generationsbelege | 30 × 1.536 | 46.080 |
| Eine gemeinsame Verifikation | 1 × 262.144 | 262.144 |
| **Reservierte Teilsumme** | | **4.964.336** |

Schon diese Teilsumme überschreitet die Gesamtgrenze um **770.032 Byte**.
Quellen, Referenzauflösung, Manifeste, Test-/Qualifikationsbindung, Auswertung,
Anzeige und Abschluss sind darin noch nicht enthalten. Ihre Werte sind
**offen, nicht null**. Keine vollständige tragfähige Laufbilanz behauptet.
Die gemeinsame Zusatzhülle reserviert davon zunächst 114.688 Byte für NJ,
Formationen und Generationen; für Quellen bleiben rechnerisch höchstens
278.528 Byte. Auch deren vollständige aktive Liste ist noch nicht gebunden.

Zudem sind im bisherigen Ledger Formationen und Generationen jeweils auf
30.720 Byte begrenzt. Jeweils 46.080 Byte Reserve für 30 Belege überschreiten
dies um 15.360 Byte. Diese Beträge sind Teil der obigen Gesamtteilsumme,
keine nochmals hinzuzuaddierenden Ausgaben. Erfolgs- und Fehlerabschlüsse
wären alternativ, nicht additiv zu prüfen. Eine bereits unpassende
Erfolgsreserve wird durch eine kleinere Fehlerhülle nicht zulässig.

Wichtig: Summe bisheriger Einzelmaxima ist **keine tatsächliche Laufgröße**
und kein Beweis, dass alle Maxima gleichzeitig erreichbar sind. Sie zeigt,
dass das bisherige Vorabsicherungsverfahren den neuen Umfang nicht trägt.
Eine passende kleine Fixture wäre umgekehrt kein struktureller Gegenbeweis.
Die einmalige gemeinsame Null-/Eingangsablage ist hier bereits günstig
unterstellt, noch kein implementierter, qualifizierter Referenzanschluss.

## Konsequenz und verbleibende Arbeit

Vor einer einmaligen Qualifikation fehlt eine tragfähige gemeinsame Hülle.
Keine zwei separat zugestandenen 4-MiB-Budgets, keine Übernahme des
Checkpointbudgets, keine Reduktion der 30 Formationen oder acht Hinweise.
Noch keine ausführbare Laufbindung, keine Qualifikation und keine neue
Produktdatei angelegt. Historische Befunde und Gates unverändert.

Kleinste mögliche Fortsetzung innerhalb der Grenzen wäre ein nachweislich
engerer struktureller Größenbeleg für die vorhandenen Ausgabeformen und eine
vollständig auflösbare gemeinsame Eingangsablage. Ob dies ausreicht, ist
offen; nicht durch eine Erfolgsfixture oder neue Kompaktierungsmechanik
vorwegnehmen. Alternativ wäre eine ausdrücklich neue private gemeinsame
Belegbudgetentscheidung nötig, die hier nicht erteilt oder umgesetzt wurde.

Das vorbereitete Prüfinventar bleibt: Arm-/Ownerisolation, identische aktuelle
Werte und Zeiten, Nullbeginn ohne künstliche Alterung, Read-only-Hinweise vor
Formation, fortgesetzte frische Geschichte, unabhängige Direktbaselines,
transaktionsgebundene reine/gemischte/fehlende Herkunft, gültige negative
Vergleiche, kontrollierter Fehler/close sowie gemeinsame Erfolgs-/Fehlerbilanz
über alle Fortschrittspositionen. Noch keine dieser neuen Kontrollen als
bestanden ausgegeben.

## Gelesene Quellenstände (SHA-256)

- `_s2oe_media_binding.py`: `58184e85fb33d3a9b860f2facb0e058bc5e4c1b9fa2a1984f5343803c2511bd6`
- `_s2oc_shared_verification.py`: `554c087eb966eefbb0a56bfdf8ef0845910db774509ceeab4daeda86300cf4df`
- `_s2ob_private_caller_binding.py`: `4c58c5adf96c3a6643682a6a6be33e599e4eac5f245b996c18221239543f780d`
- `_s2ob_private_caller_verification.py`: `3ec4772f420be4dbb838179b123584e9abd597b64cb3a675a3ca900b257f2b3d`
- `_s2oa_private_runtime_binding.py`: `196c2ab662dd3f82033b439de317a314e421b360442d459266777bff6826b3e0`

Die Liste belegt diese statische Klärung, nicht das vollständige transitive
Manifest eines implementierten Vergleichsanschlusses.

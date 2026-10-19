# Was darf der visuelle Abruf behaupten?

Stand 12.09.2026. Auftrag `ABRUF-ANZEIGE-AUSSAGEUMFANG`.
Ausschließlich dokumentarische Aufgabenbindung und Anzeigevorschlag.

Nachfolgender Implementierungsstand: Der separat freigegebene historische
Lesemodus ist mit 15/15 neuen neutralen Prüfungen qualifiziert und
[bereitgestellt](../reports/s2oe/history-display-qualification-20260912-01/view.html).
[Befund und Grenzen](../reports/s2oe/history-display-qualification-20260912-01/REPORT.md).
Die folgende Tabelle beschreibt den Ausgangsstand des Vorschlags. Seine
Detailprojektion ist jetzt für abgeschlossene, gepinnte Medienbelege verfügbar,
nicht als neuer laufender Runtimeanschluss. Keine neue Medienanalyse.

## Vergleich unverändert geschlossen

Der [Einmalvergleich](../reports/s2oe/visual-b-frozen-comparison-20260912-01/REPORT.md)
bleibt technisch gültig und fachlich gemischt: vier neue richtige
B-Anwendbarkeiten nach der vorgebundenen Bewertung, eine neue falsche
B-Anwendbarkeit und genau ein neuer öffentlicher B-Zielabruf bei vb-05.
Bei vb-06 verhindert A-Mehrdeutigkeit nur die öffentliche Fehlzulassung;
sie korrigiert nicht die falsche B-Anwendbarkeit. Gewinne und Fehler werden
nicht verrechnet. In allen Erhaltungsgruppen D=0: Erhaltung nicht geprüft.

vb-01/02/03/06 sind bytegleich nach Okklusion, bei getrennten Quellenrollen.
Diese Fälle sind keine unabhängigen Replikate. Gleicher sichtbarer Eingang
und gleicher Zustand enthalten keinen Hinweis auf ihre verdeckten Unterschiede.
Eine andere Schwelle kann diese fehlende Information nicht hinzufügen.
Keine bevorzugte Integration von <= 1/255, weitere Schwellen-/Pegelsuche
oder Wiederholung. Historische Erwartungen und Ergebnisdateien unverändert.

## Zwei verschiedene Aufgaben

| Aufgabe | Zulässiger Aussageumfang | Nicht dadurch belegt |
| --- | --- | --- |
| Bezug beobachteter Komponenten | Die tatsächlich beobachteten Komponenten erfüllen die benannte Vergleichsbedingung zu einer gespeicherten Spur. Sicht, Regel und Generation gehören zur Aussage. | Gleiche Quelle, gleicher Gegenstand, gleiche gesamte Szene; auch kein automatisch richtiger Inhaltsbezug. |
| Zuordnung der gesamten Szene | Eine vorab definierte Gesamtzuordnung müsste relevante veränderte räumliche Struktur berücksichtigen. | Die geprüften 32 Komponenten reichen dafür nicht. Eindeutigkeit innerhalb einer Kandidatenmenge ersetzt fehlende Wahrnehmungsinformation nicht. |

**Verbindliches Architekturziel:** Der Abruf beschreibt ausschließlich den
ersten Fall: Beobachtete Komponenten erfüllen eine benannte Vergleichsbedingung
zur gespeicherten Spur. Ein Anwendbarkeitsbefund und eine öffentliche
Zulassung bleiben dabei getrennt; eine Enthaltung wird nicht zur Empfehlung
umgedeutet. Die zweite Aufgabe bleibt offen, solange Gesamtzuordnung und
ihre erforderliche räumliche Evidenz nicht festgelegt sind.

Das ist die beschlossene Aufgabenbindung, keine bereits implementierte
Ausgabeänderung. Insbesondere wird vb-06 nicht rückwirkend vom Fehler zum
Erfolg umbenannt. Die Aufgabenbindung ändert frühere Bewertungen nicht.

## Kompakter Anzeigevorschlag für den vorhandenen Player

Vier Bereiche genügen: **zuletzt verarbeitete Wahrnehmung**, **gespeicherte
Spur**, **beobachtete Vergleichsbasis**, **Abrufausgang**. Keine semantischen
Namen, Identitätsbehauptungen oder erfundenen Konfidenzwerte. „Aktuell“ meint
den letzten abgeschlossenen Verarbeitungsschritt, nicht das gerade sichtbare
Bild der ausdrücklich unsynchronen Vorschau.

| Anzeigefeld | Vorhandene Datenquelle | Noch fehlender Anzeigeanschluss |
| --- | --- | --- |
| Ereignis, Durchlauf, ausgewähltes Medienfenster, Runtimezeit | `Player._run()` setzt `last_processed`; bereits im Status und in `render()` angezeigt. | Keine neue Erfassung; Auswahlzeit nicht als tatsächlichen Framezeitpunkt ausgeben. |
| Wahrnehmungsstatus und Herkunft | `projection()` übernimmt `perception_status`; native Eingangs- und Quellenbelege liegen im Sitzungsbeleg als `inputs` und `source_receipts`. | Gebundene Quellen-/Profil- und native Zeitreferenz zusätzlich in die Anzeigeprojektion aufnehmen. Ein Status allein zeigt keine Rezeptorwerte oder ein Rezeptorbild. |
| Memorybildung oder unveränderter Zustand | `memory_status` bereits im Player; `rows`, `states` und Formationsbelege im Gesamtbeleg. | Bestehenden Formationsbefund lesend zuordnen; nicht aus einem Abrufstatus auf Lernen schließen. Support bleibt gesättigter Evidenzzähler. |
| Bereich, Bank, Slot und Generation der Spur | Scans, Zustandsreferenzen sowie `generations` und `current_births` der Runtimezeilen sind gespeichert; `generation_step()` begründet die Fortschreibung. | Ereignisgebundene Verknüpfung von Scankandidat und vorhandener Generation fehlt in der Playerprojektion. Nur bei eindeutiger vorhandener Bindung anzeigen; sonst „Generation nicht ausgewiesen“. Slot-ID oder Gesamtdigest sind kein Ersatz. |
| Tatsächlich beobachtete Komponenten | Gebundener Cueeingang und Sicht-/Profildefinition im bestehenden Eingangs- und Codebezug; nicht im kompakten Playerstatus. | Originalindizes mit ihrer gebundenen Kanal-/Rasterposition sichtbar machen. Keine verdeckten Werte, ergänzte Rasterzelle oder aus Prototypen rekonstruierte Beobachtung. Fehlende Positionsbindung ausdrücklich anzeigen. |
| Vergleichsregel und Einzelbefund | Aktive Profil-/Regelbindung und gespeicherte Scans einschließlich Direktbaseline; der Medienpfad bindet `ALL_BANDS_24` für Audio, einen eigenen visuellen Adapter. | Tatsächlich verwendete modalitäts- und bereichsspezifische Regel referenzieren. Vorhandene Terme nur anzeigen, falls gespeichert; fehlende numerische Differenzen nicht neu berechnen. Der experimentelle visuelle Vergleich `<= 1/255` ist kein Playerdefault. |
| Hypothese, Mehrdeutigkeit oder Enthaltungsgrund | Unveränderliches Schrittergebnis enthält `hypothesis`, `context_status` und `error_codes`; `projection()` reduziert die Hypothese auf Vorhandensein und Digest. | Typisierten Ausgang lesbar benennen und, soweit belegt, Spurbezug ergänzen. Hypotheseninhalt nicht aus dem Booleschen Wert rekonstruieren. Technischen Fehler getrennt darstellen. |

**Ausgabebedeutung:** Bei einer Hypothese: „Komponentenbezogene Hypothese“
mit Regel- und Spurbezug, niemals „Objekt erkannt“ oder „Szene identifiziert“.
Interne beziehungsweise bereichsübergreifende Mehrdeutigkeit bleibt explizit.
„Kein passender Kontext“ ist von „kein Kontextbestand“ zu unterscheiden.
Bei einer Formation ohne Abruf lautet die Anzeige „Abruf nicht angefordert“,
nicht automatisch „Enthaltung“. Historische Verfügbarkeit wird auf den
damaligen Ereigniszustand bezogen; eine ersetzte Generation ist nicht aktuell.

**Kleinste Anschlusslücke:** eine rein lesende, ereignisgebundene
Anzeigeprojektion der vorhandenen Belege. Heute liefern `projection()` und
`status()` diese Detailverknüpfung nicht. Es fehlt keine neue Wahrnehmung,
sondern ihre begrenzte Anzeigezuordnung; bei tatsächlich fehlenden Angaben
bleibt „nicht belegt“. Keine zusätzlichen Scans bei Statusabfragen, keine
Medienanalyse, keine Zustandsfortschreibung und keine neue Belegplattform.
Dieser Vorschlag implementiert oder qualifiziert den Anschluss noch nicht.

Statische Codebezüge: [Playerprojektion](../tools/_s2oe_local_player.py),
[bestehende Anzeige](../tools/s2oe_player.html),
[Sitzungsbeleg mit Eingängen, Zuständen und Scans](../tools/_s2oc_bound_session.py),
[Medienprofil und Adapter](../tools/_s2oe_media_session.py),
[Generationsfortschreibung](../tools/_s2oa_private_runtime_binding.py).

## Zurückgestellter explorativer Vorschlag für Aufgabe zwei

Nicht beauftragt: Die folgende zusätzliche Zelle wird nicht implementiert.
Ihre Wahl erfolgte bei bereits bekannten Fällen; sie ist keine unabhängige
Bestätigung und gehört nicht zum Anzeigevorschlag.

Vorschlag: genau **eine zusätzliche vollständige Rasterzelle** außerhalb
der bisherigen Sicht beobachten, separat belegt, ohne Verschieben der alten
Sicht. Als konkrete geometrische Wahl für das vorhandene 1920×1080-Raster:
die Zelle unmittelbar links oberhalb der Bildmitte, Spalte 5 / Zeile 3
(nullbasiert), Rechteck **[800,960) × [405,540)**. Ihre drei ursprünglichen
Komponenten sind **123, 124, 125** im unveränderten 12×8×3-Raster.

Diese Wahl verwendet eine feste Bildgeometrie, keine spätere Trefferleistung.
Der vorhandene Korpus und seine Rezepte sind allerdings bereits bekannt:
Auch diese vorbereitete Ortswahl ist kein unabhängiger Bestätigungstest.
Sie ist hier ein konkreter Vorschlag, noch kein gebundener neuer Prüfbestand.

- Benötigt wird tatsächlicher unokkludierter RGB-Inhalt desselben Cueframes,
  mit identischem Originalraum, Frame-/Zeit- und Quellenbezug. Er darf nicht
  aus Memory, Generatorrollen oder den nullgesetzten Cuekomponenten ergänzt
  werden. Fehlt dieser Eingang, lautet der Befund zusätzliche Evidenz fehlt.
- Der Rezeptor behält sein Raster. Kein vergrößerter Ausschnitt, keine
  Vollvektorumordnung, kein Tracking und keine automatische Ortswahl.
  Die bestehende historische Cueform wird nicht umetikettiert. Für eine
  spätere Umsetzung fehlt eine separat versionierte Orts-/Evidenzbindung.
- Gegenübergestellt würden nur diese neu beobachteten Komponenten und die
  korrespondierenden gespeicherten Komponenten derselben Slotgeneration.
  Quellenherkunft und Zeitpunkt bleiben eigenständig prüfbar. Zunächst
  keine neue Zulassung, Maskenvereinigung oder Konjunktion daraus ableiten.

**Wesentliche Grenze:** Eine zusätzliche Zelle kann allenfalls an diesem Ort
weitere Information liefern. Übereinstimmung bestätigt nicht die ganze Szene;
Unterschiedlichkeit allein beweist noch keine unzulässige Veränderung.
Rastermittelwerte können verschiedene Pixelstrukturen zusammenfassen.
Für eine Gesamtzuordnung fehlen weiterhin eine konkrete zulässige
Veränderungsdefinition und ein begründeter Abdeckungsanspruch. Dieser kleine
Schritt schließt die Gesamtaufgabe daher ausdrücklich nicht ab.

## Frühere Befunde bleiben wirksam

NP/NQ zeigten einen begrenzten Vorteil einer verteilten auditiven Sicht;
der neue NR-Strom zeigte öffentliche Verluste und eine Fehlzulassung trotz
erhaltener Zielbeziehungen. Daraus folgt keine generell bessere feste Sicht.
NS lieferte mit der Konjunktion keinen Zusatznutzen gegenüber LOWER und
neue Fehlzulassungen gegenüber UPPER: zusätzlicher Ausschluss kann schützende
Mehrdeutigkeit entfernen. Das sind auditive Befunde, kein direkter Beweis
über diese visuelle Zelle; ihre Auswahl- und Aussagegrenzen bleiben relevant.

Deshalb keine Wiederaufnahme dieser Konfigurationen als fertige Lösung und
kein automatisches UND über zwei fertige Hypothesen. Erst Aufgabenentscheidung,
dann gegebenenfalls eine separat freigegebene Beobachtungsbindung.
Gates False; keine Implementierung, Quellenproduktion, Berechnung oder Ausführung.

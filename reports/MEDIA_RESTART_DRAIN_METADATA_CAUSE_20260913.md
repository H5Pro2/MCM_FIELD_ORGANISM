# DRAIN-Metadaten: Ursachenklärung und vorbereiteter Regressionsfall

**Nur Ursachenklärung.** Kein Testaufruf, Projektimport, Decoder-, Rezeptor-
oder Runtimeaufruf; keine Wahrnehmungsrekonstruktion. Bestehende JSON-Belege,
Dateigrößen und Code wurden gelesen und administrativ gegenübergestellt.
Der Lauf `media-restart-real-20260913-01` bleibt unverändert NOT_EVALUABLE.

HEAD: `537109994cf777f8d36cda617aafe12226806c25`. Die acht untersuchten
Quelldateien stimmen mit dem laufgebundenen Inventar überein. Einzeldateien,
Hashes, Summanden und der noch unausgeführte Regressionsfall stehen in
[MEDIA_RESTART_DRAIN_METADATA_CASE_20260913.json](MEDIA_RESTART_DRAIN_METADATA_CASE_20260913.json).
Historische Abschlussdateien wurden nicht ergänzt oder verändert.

## 1. Vollständige Zerlegung der 134.341 Byte

### Bereits vorhandene externe Metadaten: 89.972 Byte

| Unverändert aktive Belege | Byte |
| --- | ---: |
| Restart-Qualifikation -01: Vorregistrierung, Ergebnis, stderr | 27.914 |
| Restart-Qualifikation -05: Vorregistrierung, Ergebnis, stderr | 14.766 |
| Zulassungsqualifikation -02: sieben Bindungs-/Abschlussdateien | 28.907 |
| Reale Bindung: archive.json, PLAN.md, budget.json, binding.json, authorization.json | 18.385 |
| **Summe, alle 18 Einzeldateien im JSON aufgelistet** | **89.972** |

### Bis zur Abweisung zusätzlich gespeicherte Metadaten: 12.049 Byte

| Datei beziehungsweise logische Objektrolle | Byte |
| --- | ---: |
| run.claim | 88 |
| reference.claim | 142 |
| initial, Objekt `38a47742…` | 1.051 |
| runtime_config, Objekt `3b60c232…` | 416 |
| binding, Objekt `82af0a57…` | 3.462 |
| inputs-Verweisindex, Objekt `6e0f0a57…` | 2.330 |
| source_receipts-Verweisindex, Objekt `d9a4175e…` | 2.230 |
| rows-Verweisindex, Objekt `cd0ea7fd…` | 2.330 |
| **Summe** | **12.049** |

Die vollständigen Objektnamen sind im JSON gebunden. Die Rollen ergeben
sich aus den gespeicherten Verwaltungsformen und dem Packpfad, nicht aus
neu berechneten Wahrnehmungswerten. reference.stdout und reference.stderr
waren zu diesem Zeitpunkt leer: Der Fehlerbeleg weist Logverbrauch null aus.
Die spätere stderr-Ausgabe, failure.json und die Abschlussdokumente gehören
nicht rückwirkend zu diesem Zeitpunkt.

Damit ergibt sich exakt der gespeicherte Wert:
**89.972 + 12.049 = 102.021 Byte bereits belegte Metadaten.**

| Weitere Anforderung bei der abgewiesenen Publikation | Byte |
| --- | ---: |
| Neuer Beleg, endgültiger Pfad | 3.872 |
| Derselbe Beleg, temporärer .pending-Pfad | 3.872 |
| Noch offene Logreserve | 8.192 |
| Noch offene Auswertungs-/Abschlussreserve | 8.192 |
| Primärfehlerreserve: zwei Kopien zu höchstens 4.096 Byte | 8.192 |
| **102.021 + sämtliche obigen Beiträge** | **134.341** |

Grenze 131.072, Überschreitung **3.269 Byte**. Beide angebotenen
Veröffentlichungskopien sind tatsächlich vertraglich zu zählen. Die
Abweisung liegt vor dem Schreiben der temporären Datei; diese 7.744 Byte
wurden nicht nachträglich als tatsächlich gespeicherte Bytes ausgegeben.

**Zuordnung des neuen Belegs:** Nach der Code-Reihenfolge ist es der
`states`-Verweisindex: `CallerRuntime.record()` führt states nach rows,
`Store.pack()` schreibt hierfür native Einzelobjekte und dann einen
Metadatenindex. Alle vorgelagerten Verwaltungsobjekte liegen vor.
Der Fehlerbeleg speichert jedoch weder Objektpfad noch logischen Schlüssel
oder Inhalt des abgewiesenen Objekts. Seine **Größe und Klasse** sind direkt
belegt; die konkrete Rolle ist eine statische Zuordnung. Kein fehlender
Byteinhalt wurde nachgebaut.

Code: [record()](../tools/_s2ob_private_caller_binding.py:381),
[DRAIN und publish()](../tools/_media_restart_checkpoint.py:249),
[Packreihenfolge](../tools/_media_restart_evidence.py:114),
[Prüfung vor beiden Kopien](../tools/_media_restart_evidence.py:78).

## 2. Unterschied zur Vorbindung

Die finale Vorbindung hielt **114.548 Byte** fest:
89.972 vorhandene Metadaten plus dreimal 8.192 Reserve. Ihre administrative
Publikationsspitze **122.350** addierte den größten Bindungsdateikörper
von 7.802 Byte. Das beschreibt die Vorbereitung, nicht den späteren Packpfad.

**Es fehlt ein eigener Ansatz für die entstehenden Verwaltungsobjekte und
Verweisindizes.** Schon bis zur ersten abgewiesenen Publikation kommen
12.049 vorhandene und 7.744 angebotene Bytes hinzu: **19.793 Byte**.
Die Vorbindung lässt nach ihren Reserven nur **16.524 Byte** frei.
Die Differenz ist wiederum 3.269 Byte. Weitere noch ausstehende Belege sind
damit überhaupt noch nicht abgedeckt.

Kein nachgewiesener Klassifikationsfehler im laufenden Ledger: Die Indizes
sind gemäß Packcode Metadaten. Sie dürfen nicht aus dem Native-Budget bezahlt
oder nachträglich als native Werte umklassifiziert werden. Eine tatsächliche
weitere Ablage bleibt auch bei inhaltlicher Überschneidung mit Eingangsbindungen
vollständig gezählt.

Der Dateieinstieg prüft vor Beginn nur `store.budget()` für vorhandene Dateien
und benannte Zukunftsgruppen. Er fordert keinen vollständigen Plan aller
späteren Packpublikationen. Die Vorbereitung verwendet daneben eine eigene
Summenrechnung. Eine gemeinsame Funktion allein genügt deshalb nicht: Auch
die zugrunde gelegten künftigen Verpflichtungen müssen dieselben sein.

Code: [Vorbereitungsrechnung](qualify_media_restart_admission_once.py:133),
[tatsächlicher Vorstartcheck](run_selected_media_restart_once.py:156).
Die endgültige, administrativ abgegrenzte Vorbindung selbst bleibt unter
`media-restart-real-20260913-01-binding/budget.json` unverändert erhalten.

Dieselbe bestehende Regel, auf die drei verschiedenen Zeitpunkte angewandt:

| Zeitpunkt | Physische Metadaten | Zusätzlich angebotene Kopien | Offene Gruppen | Primärreserve | Summe |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vorbindung | 89.972 | 0 | 16.384 | 8.192 | 114.548 |
| DRAIN vor abgewiesener Publikation | 102.021 | 7.744 | 16.384 | 8.192 | 134.341 |
| Gesicherter Fehlerabschluss samt Bericht/Bilanz | 110.943 | 0 | 6.752 | 8.192 | 125.887 |

Die letzte Zeile ist der gespeicherten Abschlussbilanz entnommen, keine
nachträgliche Gegenrechnung für den nicht geschriebenen Erfolgsbeleg.

## 3. Reserven nach Lebensphase

| Reserve | Bei der DRAIN-Abweisung | Nach dem technischen Fehler |
| --- | --- | --- |
| Logs 8.192 | Verbrauch null; Referenzfehlerausgabe und weitere Prozesse konnten noch Ausgabe erzeugen. Nicht freigebbar. | 1.440 Byte tatsächlich geschrieben; Prozesse beendet. Die alte Markerregel hält trotzdem 6.752 Byte, weil result.json fehlt. |
| Auswertung/Abschluss 8.192 | Keine der benannten Dateien geschrieben. Beim erfolgreichen Fortgang noch erforderlich; der states-Index gehört nicht zu diesen Pfaden. | Fachliche Auswertung gesperrt. Fehlerbericht und Bilanz bleiben erforderlich; ihre vollständige Fehlerform braucht eine eigene vorgebundene Zuordnung. |
| Primärfehler 8.192 | Fehler noch nicht veröffentlicht, Reserve nicht verbraucht. Sie durfte nicht als bereits ersetzte Ausgabe abgezogen werden. | 3.368 Byte Fehlerbeleg geschrieben, kein zweiter Primärabschluss erlaubt. Die alte budget()-Rechnung schützt dennoch konstant nochmals die volle Reserve. |

**Bei DRAIN ist keine schon verbrauchte, fälschlich weitergeführte Reserve
nachgewiesen.** Historische Qualifikationslogs sind aktive Eingänge; sie
verbrauchen nicht die Reserve der neuen Prozesslogs.

Die spätere kleinere Istbilanz erklärt sich auch dadurch, dass der abgewiesene
Beleg und alle weiteren Erfolgsbelege fehlen. Sie begründet keine günstigere
DRAIN-Bewertung. Die nach Fehlerabschluss konservativ weitergeführten Reserven
sind ein getrenntes Lebenszyklusproblem, nicht rückwirkend dessen Ursache.

Code: [genaue Pfad-/Markerzuordnung](../tools/_media_restart_reservations.py:43),
[konstante Primärreserve](../tools/_media_restart_evidence.py:74),
[direkter Fehlerabschluss](../tools/_media_restart_evidence.py:201).

## 4. Kleinste zusammenhängende Korrektur, noch nicht implementiert

1. **Vorbereitung und execute():** Einen vollständigen, manifestgebundenen
   Publikationsplan verlangen, einschließlich Claims, innerer Metadatenobjekte,
   aller Verweisindizes, Record-/Checkpointhüllen, Prozessbelege, Verifikation,
   Logs und beider terminaler Formen. Fehlender oder nicht begründeter
   Größenansatz muss vor Medienzugriff typisiert sperren. Kein impliziter Nullansatz.
2. **Store.pack()/intern() und derselbe Ledger:** Jede erzeugte Verwaltungsrolle
   eindeutig der vorgebundenen Verpflichtung zuordnen. Beim tatsächlichen
   Schreiben ersetzt ihre physische Belegung genau diese Reserve; zusätzliche
   Kopien bleiben zusätzlich. Vor einer Gesamtveröffentlichung auch deren noch
   ausstehende innere Publikationen und Peaks prüfen, nicht erst am nächsten
   einzelnen Objekt unerwartet scheitern. Im Budgetfehler logische Rolle,
   Zielpfad, Anteil und vollständige Restverpflichtungen festhalten.
3. **reservations.assess():** Physische Belegung und verbleibende Verpflichtungen
   als gemeinsame Basis für Vorbindung, DRAIN und Abschluss verwenden.
   Erfolg und technischer Fehler sind alternative terminale Pfade. Ihre
   Spitzen müssen über sämtliche zulässigen Fehlerzeitpunkte betrachtet werden:
   Eine im erfolgreichen Präfix bereits geschriebene oder liegengebliebene
   Datei bleibt auch im Fehlerpfad vorhanden. Nicht einfach die Primärreserve
   aus jeder Erfolgsrechnung streichen.
4. **Einmaleinstieg/Abschluss:** Nach belegtem Prozessende und verbindlichem
   Fehlerabschluss keine unerreichbaren Auswertungs- oder zweiten Primärbelege
   weiter reservieren. Die vollständige tatsächliche Fehlerform und verbleibende
   Bericht-/Bilanzarbeit müssen trotzdem Platz haben. Kein zweiter Abschluss
   und keine neue Recorderplattform.

Gemeinsame Rechenregel je zulässigem Pfad und Publikationszeitpunkt:
**physische Belegung + noch nicht erfüllte Verpflichtungen + gleichzeitig
zusätzlich vorhandene Veröffentlichungskopien.** Der höchste Wert aller
zulässigen Erfolgs- und Fehlerzeitpunkte entscheidet. Ein späterer Fehler
setzt keine bereits angefallenen Präfixbytes zurück.

Der vorliegende Befund beweist nicht, dass eine vollständige, korrekte
Alternative-Rechnung den gesamten Vergleich in die Grenze bringt. Dafür
fehlen noch formatgebundene Größenansätze der restlichen Referenzpublikation,
des Suspend-/Restorearms und der vollständigen Fehleralternative. Keine
pauschale Erhöhung um 3.269 Byte und keine neue Laufempfehlung auf Verdacht.

## 5. Rezeptorfreie Regression vorbereitet, nicht ausgeführt

Das beigefügte JSON enthält ausschließlich administrative Größen, Dateireferenzen,
Codebindungen, Reserven und den gespeicherten Fehler. Keine PCM-, Bild-,
Wahrnehmungs- oder nativen Zustandskörper. Ein Testaufruf bleibt separat freizugeben.

Für die unveränderte alte Regel ist das sichere erwartete Ergebnis schon
vor Medienbeginn bestimmt:
**89.972 + 12.049 + 2 × 3.872 + 24.576 = 134.341 > 131.072**.
Diese Untergrenze des gespeicherten Falls muss bereits den Vorstart sperren.
Sie ist keine aus einem einzelnen Lauf abgeleitete allgemeine Obergrenze.

Vorgesehene Kontrollen: historische Zerlegung erhalten; Vorstartsperre ohne
Medienzugriff; erfüllte Verpflichtung nicht doppelt reservieren; physische
Kopien weiter zählen; reine Rechenkontrolle exakt an der Grenze und einen
Byte darüber; unvollständigen Publikationsplan abweisen. Eine künftig
abweichende positive Bewertung benötigt die vollständige begründete
Erfolgs-/Fehlerrechnung, nicht nur eine gestrichene Reserve.

**Kein Produktcode geändert, keine Regression ausgeführt, kein Medienlauf
vorbereitet. Gates bleiben False.**

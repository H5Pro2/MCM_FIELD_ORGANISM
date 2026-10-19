# Detailblick: lesende Einordnung und Entwicklungsentscheidung

Der Vergleich bleibt unverändert geschlossen. Dieser Nachtrag liest nur
vorhandene Ergebnisse und Code; keine neue Bildanalyse, Berechnung,
Verifikation, Implementierung oder Ausführung. Keine Ausschnittsuche,
Schwellenänderung oder Memoryintegration. Repository-Bezug wie im
[Abschluss](FIXED_DETAIL_CLOSURE_RESULT.md).

## Was trägt die Aussage?

`evaluate()` in `tools/_s2oe_detail_closure.py` setzt
`detail_advantage='NOT_ESTABLISHED'` ausdrücklich konstant. Es gibt dort
keinen berechneten Vorteilsscore und kein bestandenes negatives
Leistungskriterium. **Nicht nachgewiesen ist nicht gleich widerlegt.**

| Evidenz | Gespeicherter Befund | Aussagegrenze |
| --- | --- | --- |
| Reales Video, zehn Paare | jeweils gleiche native Frameherkunft, unterschiedliche RGB-Hashes, feste unterschiedliche Abdeckung | korrekte Darstellungsanbindung; keine Messung besserer Strukturerkennung |
| Reale Rezeptorwerte | zwanzig Vektoren gespeichert | keine berechnete zeitliche Struktur-, Wiedererkennungs- oder Stabilitätsbewertung |
| Synthetische K0/K1-Kontrolle | unterschiedliche Pixel, jeweils 288 bitgleiche Werte in Übersicht und Detail | konkrete Kollision; kein Nachweis ihrer Ursächlichkeit im Video |

Die 576 Kontrollgleichheiten sind die numerische Vergleichsgröße. Die
RGB-Hashunterschiede belegen keine brauchbare Unterscheidung durch den
Rezeptor. Der bisherige Befund rechtfertigt keine Integration, ist aber
auch kein fairer negativer Leistungstest fokussierten Sehens.

## Räumliche Verdichtung

`mcm_field_organism/finite_video_path.py:27` bindet 12 Spalten, acht Zeilen
und drei Kanäle. `LocalChannelGridReceptor.analyze()` (Zeilen 191–216)
mittelt mit `mean(axis=(1, 3))` alle Pixel pro Zelle und Kanal, teilt durch
255 und erhält die feste Zeilen-/Spalten-/RGB-Reihenfolge.

Erhalten bleiben grobe räumliche Lage und mittlere Farb-/Helligkeitsverteilung
über 96 Zellen. Verloren gehen die Anordnung innerhalb jeder Zelle, lokale
Kantenorientierung, Textur und sonstige Verteilungen mit denselben drei
Summen. Pixelumordnungen innerhalb einer Zelle bleiben unsichtbar.
Bewegung über Zellgrenzen kann Werte ändern, ohne dass sich die Form geändert
hat. Zeitliche Korrespondenz, Objektgrenzen und Bewegung werden nicht kodiert.
Der frühere Übersichtsskalierer kann davor zusätzliche Information verlieren;
der Detailausschnitt verwirft dagegen den Außenbereich. Keine dieser Aussagen
belegt, welcher Verlust den konkreten Videoverlauf erklärt.

## Vorhandene Ansätze nicht neu beginnen

- [S2-LV](../../docs/S2LV_POSE_FORM_VERGLEICH.md): vorhandene Pose-/Formtrennung
  verbessert die Zentroidzuordnung von 14/32 auf 32/32, bei weiterhin
  überlappenden Distanzen. Keine allgemeine Zulassungsschwelle.
- [S2-LX](../../docs/S2LX_MASKENKONDITIONIERTER_POSE_FORM_VERGLEICH.md):
  maskierte Form hilft gegenüber rohen Teilwerten, verliert jedoch bei kleinen
  Formen und großen Lageänderungen; keine Wiedergewinnung verdeckter Werte.
- [S2-LY](../../docs/S2LY_ZWEI_BLICK_FORMKONSENS_VERGLEICH.md): Formkonsens
  kann gemeinsam falsch liegen; mehr Abdeckung half im damaligen Korpus,
  begründet aber keine allgemeine Integration.
- [S2-MI](../../docs/S2MI_BINDUNGSBEOBACHTBARKEITSAUDIT.md): Pose/Form allein
  liefern keine beobachtete Korrespondenz oder sichere Lernbindung.
- [S2-MQ](../s2mq/S2MQ_KORPUSVERGLEICH_LAUF_03_BEFUND.md): Sparse-LK wurde
  bereits untersucht. Vier von zwölf Bewegungsbeziehungen auswertbar und
  bestanden, während Pixel-L1 alle sechs seiner Beziehungen trennte.
  Kein zusätzlicher Trennnutzen, bei kantenarmen Bildern unzureichende
  Evidenz. Deshalb nicht pauschal einen neuen Tracker vorschlagen.

## Kleinste begründbare Entscheidung

Die aktuelle Darstellung ist **noch nicht als ausreichend für wiederkehrende
Struktur trotz Bewegung nachgewiesen**. Ebenso wenig ist eine konkrete neue
Merkmalsfamilie durch diesen Detailvergleich begründet.

Als kleinster fehlender Wahrnehmungsnachweis ist eine **bewegungsbedingte
Änderung der Lage getrennt von einer Änderung der räumlichen Struktur** zu
prüfen. Dafür ist zuerst die bereits vorhandene Pose-/Formprojektion als
private read-only Vergleichsansicht vorzusehen, nicht erneut zu entwickeln.
Ihre Rolle wäre eine strukturbezogene Vergleichsbasis ohne Memoryzulassung;
der fehlende Anschluss ist deren aufgabenbezogener Nachweis an bewegter,
nicht bereits passend segmentierter Wahrnehmung.

Eine spätere kleine Gegenprobe müsste unveränderte Struktur bei Lageänderung
und veränderte Struktur bei vergleichbarer Lageänderung auseinanderhalten,
gegen rohe Rasterwerte und die vorhandene Formprojektion. Nicht beobachtbare
oder mehrdeutige Zuordnungen müssen offen bleiben. Generatorrollen wären nur
Bewertungsherkunft, niemals Korrespondenzbeweis. Dies ist eine Richtungs-
empfehlung, noch kein festgelegter Korpus oder ausführbarer Prüfplan.

Nur falls sich dabei eine konkrete Informationslücke innerhalb der Zellen
zeigt, wäre ein pixelnaher räumlicher Zusatzbaustein zu begründen. Ihn jetzt
aus der Streifenkollision direkt abzuleiten, würde Ursache und Aufgabenbedarf
überspringen. Keine automatische Neuauflage von LV oder MQ, keine neue
Memoryregel. ME/MI bleiben gesperrt; Gates False.

# S2-NU: vorab gebundene neutrale Quellenqualifikation

ID `s2nu-source-binding-qualification-20260909-01`, genau ein Testaufruf,
16 Testkoerper, kein Retry. Quellen, Testinventar, Interpreter/Umgebung und
dieses Dokument werden vor dem Aufruf gehasht. Historische Sealer-Einstiege
werden nicht aufgerufen; bestehende reine Metadaten-/Dateihelfer bleiben erhalten.

## Umfang vor NU-Quellenerzeugung

1. 30 getrennte Fenster- und Rezeptidentitaeten.
2. Native Zeitfenster und Ablehnung ungueltiger Snapshotgrundlagen.
3. Literale s02/s03-Permutation, gleiche Rezepte, getrennte Quellzeitbindungen.
4. Hashphasen mit neutralem Seed und unveraenderte Nullpartialpositionen.
5. Lokale Oszillatorzeit gegen fortlaufende integrierte Synthesephase.
6. Gain bezieht sich auf den Syntheseindex, nicht auf die neue Aufnahmezeit.
7. Nullmultiplikatoren ueberspringen keine beteiligte Gruppe.
8. Genau eine finale Float32-Ablage pro Sample, unveraenderte Binary64-Eingabe.
9. Alle fuenf Syntheseausdruecke mit neutralen Gruppen direkt nachrechnen.
10. Vollstaendige synthetische Metadatenpruefung mit gesperrter PCM-Erzeugung.
11. Manipulierte native Quellzeit abweisen.
12. Manipulierte Permutationsbindung abweisen.
13. Zeit-/Ordinal-/Quell-/Zustandsfelder in ungeordneter Kontrolle abweisen.
14. Getrennte Evaluationswurzel und exakt fuenf strikte Kriterien binden.
15. Metadaten- und Payloadgrenzen fail-closed pruefen.
16. Unveraenderlichkeit, Built-in-math, Profilabweichung und Importgrenze.

Nur erfundene kleine neutrale Gruppen beziehungsweise reine Planmetadaten.
Keine NU-Payloads, Rezeptor-, NJ-, Differenz-, Ordnungs-, Memory-, Feld-,
Kontext- oder Runtimeaufrufe. Die theoretischen Messformeln werden als Text
gebunden, nicht ausgefuehrt. Die Parameter der neutralen Oszillatoren stehen
literal in der Testdatei und entsprechen keiner NU-Gruppe.

Die Suite erzeugt insgesamt hoechstens 18 synthetische Samples (72 Byte),
maximal einen 12-Byte-Payload gleichzeitig, sowie skalare neutrale
Synthesereferenzen. Hoechstens 512 sin-Aufrufe und 32.768 Metadaten-/Digestchecks;
kein 4.800-Sample-Fenster. Produktgrenzen: 30 spaetere Fenster, je 19.200 Byte,
maximal ein PCM-Fenster lebend, insgesamt 576.000 erzeugte Byte ohne Ablage.
Jede Plan-/Siegelwurzel hoechstens 65.536 Byte; spaeterer Gesamtbeleg 2.097.152
Byte, Verifikation 262.144 Byte. Keine Anhebung nach einem Fehler.

## Aussagegrenzen

Die Kontrolle der ungeordneten Ansicht prueft jetzt nur ihren strikt
geschlossenen Eingabevertrag: Profil und sortierte Wertebytes, keine
Zeit-/Ordinal-/Quellkennungen. Sie implementiert und qualifiziert noch keinen
Vergleicher mit realen Vektoren. Provenienz bleibt ausserhalb der funktionalen
Eingabe. Ihre spaetere Durchsetzung am Messanschluss bleibt zu pruefen.

Nach Bestehen genau eine Vorversiegelung unter
`s2nu-source-preseal-20260909-01`, danach genau eine unabhaengige Bindungspruefung
ohne PCM-Regeneration. Payloadhashes belegen dann die erzeugten Bytes;
die Offline-Pruefung berechnet diese Bytes nicht unabhaengig nach.
Erzeugungskategorien sind keine erkannten Kategorien. Auch spaetere Kennzahl-
Empfindlichkeit gegen Umordnung waere keine Quellenfortsetzung oder Lernbindung.
ME/MI und alle Hauptgates bleiben geschlossen.

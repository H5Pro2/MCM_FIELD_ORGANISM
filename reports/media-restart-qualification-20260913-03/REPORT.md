# DATEIBETRIEB-CHECKPOINT-BEDIENUNG: Vorabstopp

**PRESTART_BLOCKED, null Testaufrufe.** Sechs fokussierte Prüfgruppen sind
vorbereitet, nicht ausgeführt. Kein neuer Qualifikationsbefund. Bezugscommit
`537109994cf777f8d36cda617aafe12226806c25`, uncommittierter Arbeitsstand.
Aktuelle Codehashes, Abhängigkeiten und Rechnungen: [Vorbindung](preregistration.json).
SHA-256: `4df58e12c07cc134e7aab8d99187686cb8f022b04a2de2ee464fc24f910a01db`.

## Vollständige Zuordnung der 6.788 Byte

Die 43 vorhandenen Metadatenobjekte des vorherigen Aufrufs belegen:

| Inhalt | Byte |
|---|---:|
| Zustandsindizes | 7.956 |
| Eingangsindizes | 4.690 |
| Schrittindizes | 4.690 |
| Quellenbelegindizes | 4.490 |
| Auswahlindizes | 4.730 |
| Leerer Scanindex | 31 |
| Zwei Präfixköpfe | 4.118 |
| Gesamtkopf | 2.063 |
| Anfangsbindung | 1.054 |
| Bindung | 3.462 |
| Manifest | 2.902 |
| Runtimekonfiguration | 419 |
| 20 einzelne Auswahlbelege | 7.143 |
| Gesamt | 47.748 |

Alle Objektdateien sind in `prior_objects.groups` mit Hash und Größe einzeln
zugeordnet. Ohne die Auswahlbelege: 40.605 Byte. Die alte Pauschale 40.960
ließ rechnerisch nur 355 Byte für deren 7.143 Byte: Differenz 6.788.
Dies erklärt die Unterreservierung vollständig, behauptet aber nicht, die
alte Planung hätte gerade diese Gruppe bewusst ausgelassen.

## Anschlusskorrektur, noch unqualifiziert

`_media_restart_reservations.bind/assess` bindet endliche Zukunftsgruppen.
Geschriebene Bytes ersetzen den entsprechenden Rest; ein terminaler Beleg
gibt ungenutzten Rest frei. Temporäre Kopien bleiben zusätzlich gezählt.
`_media_restart_evidence.Store.budget/_write` verwendet dieselbe Rechnung
für Istbelegung, Veröffentlichung und Abschluss. Die Primärfehlerreserve
bleibt 8.192 Byte, der Fehlerbeleg höchstens 4.096 Byte. Keine Logkürzung.
`Session` verlangt eine explizite Reservebindung. Keine Kernänderung.

## Warum kein weiterer Test gestartet wurde

19 Unterbrechungspositionen, 209 Kombinationen aus Schnitt und Fortschritt
sind vorgebunden. Bereits bekannte Formatgrenzen reichen nicht zum Nachweis
einer passenden vollständigen Hülle. Beispiel Schnitt 19, Fortschritt 20:

| Teilreserve | Byte |
|---|---:|
| Native Belege | 5.453.266 |
| Metadatenabhängigkeiten und Indizes | 85.864 |
| Quellen | 267.323 |
| NJ / Formationen / Generationen | 41.960 / 62.760 / 62.800 |
| Feldbelege | 1.572.864 |
| Gesamt, noch ohne weitere Abschlussanteile | 7.546.837 |

Gesamtgrenze 4.194.304, Differenz 3.352.533 Byte. Auch die gemeinsame
Zusatzhülle erreicht 434.843 gegenüber 393.216 Byte. Weitere Pflichtanteile
sind ausdrücklich als noch nicht enthalten benannt, nicht als null behandelt.
Das betrifft schon einen Vergleich, nicht erst beide Qualifikationsarme.

Dies ist eine konservative Reserve aus den bestehenden Einzelgrenzen, keine
gemessene Mindestgröße. Übernommene Restore-Präfixe sind berücksichtigt;
Gleichheit mit unabhängig erzeugten Referenzbelegen wird nicht vorausgesetzt.
Es fehlt eine engere begründete Obergrenze für den vorgesehenen neutralen
Bestand. Die frühere Istgröße oder eine pauschale Allokation ersetzt sie nicht.

Kein Test, keine Payloaddatei, kein Rezeptor-/Memory-/Feldlauf erzeugt. Gates
False. Alte 11/12- und 8/11-Befunde unverändert NOT_QUALIFIED. Keine weitere
Änderung nach der Vorbindung. Die reine Vorbereitungs-Istbilanz steht separat
in `closure-balance.json`; sie qualifiziert keine spätere Laufhülle.

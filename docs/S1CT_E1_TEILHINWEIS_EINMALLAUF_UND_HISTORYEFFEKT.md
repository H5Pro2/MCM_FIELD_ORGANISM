# S1-CT: E1 Teilhinweis-Einmallauf und Historyeffekt

## Status

Der in S1-CS registrierte 36er-Teilhinweislauf wurde genau einmal
ausgefuehrt und atomar gespeichert. Alle 36 Beobachtungen, Kontrollen und
Digests sind vollstaendig. Versuchsnachweis und Sperrdatei wurden nach dem
Erfolg entfernt; die vorhandene Ergebnisdatei verhindert eine Wiederholung.

## Technische Entscheidung

```text
HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT
```

Der passende gegen den gekreuzten G4-Geschichtszustand erzeugt unter
gespiegelten Viertelhinweisen eine messbare signierte S/H-Interaktion. P0
und der eine statische H8-Adapter besitzen keine Historyinteraktion.

## Rohmetriken

```text
Teilhinweis-Historyinteraktion L-inf: 0.0005379061925296288
Vollhinweis-Historyinteraktion L-inf: 0.0021516247701185154
Teil/Voll-Verhaeltnis:                0.25
Teil/Voll-Richtungsskalarprodukt:      3.1212877271059945e-06
P0-Interaktion L-inf:                  0.0
B1-static-H8-Interaktion L-inf:        0.0
Gekreuzter Historykontrast L-inf:      0.0005379061925296288
Spiegelungsfehler L-inf:               3.469446951953614e-18
Relativer n=2/n=4-Rest:                2.5868378748081485e-12
```

Alle Zeitplan- und Invariantenflags bestehen. Die Teil- und
Vollkontaktinteraktion besitzen dieselbe gerichtete Orientierung.

## Ergebnisartefakt

```text
reports/e1_partial_cue_s1ct_once_v1.json
Bericht SHA-256:  ee569666e63ab7f4821f5778c3fb80d62a02f47bf3269c871b8e05bf1a450d26
Ergebnis SHA-256: 4080575ddeda8899687473d6c1491a012ca7d16d0f001177dc6fa7c03a1c20fb
Vertrag SHA-256:  7dbba163fbf9898f4b1a4a13ab54f79338b86d61ba28864882a33127343d040a
```

Vor dem realen Start bestanden 11 fokussierte Einmallauftests und 70
relevante Verbundtests. Alte Einmallaufergebnisse wurden nicht wiederholt.

## Wissenschaftliche Einordnung

Der Lauf zeigt mehr als einen unspezifischen Nachhall: Das schnelle
Probefeld beginnt in jedem Arm frisch und wertidentisch; nur der zuvor durch
Weltkontakt veraenderte G4-E1-Zustand unterscheidet passende und gekreuzte
Geschichte. Ein einzelner statischer H8-Adapter kann diese
Historyinteraktion nicht erzeugen.

Die Teilinteraktion ist jedoch exakt ein Viertel der Vollinteraktion und
entspricht damit genau der Viertelamplitude des Hinweises. Der aktuelle
Befund ist daher eine lineare, history-spezifische Substratmodulation. Er
zeigt noch keine Mustervervollstaendigung und darf nicht als Rekonstruktion
bezeichnet werden.

## Aussagegrenze

`HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT` ist kein Nachweis fuer MCM-Memory,
Rekonstruktion, Bedeutung, Organisation, Selbstregulation oder KI. Fuer
einen staerkeren funktionalen Memorybefund muss gezeigt werden, ob der Effekt
ueber mehrere Hinweisstaerken robust bleibt und ob er ueber reine lineare
Amplitudenskalierung hinausgeht oder durch Freigabe beziehungsweise
Umpraegung gezielt verloren geht.

## Bester naechster Schritt

S1-CU registriert statisch eine Cue-Amplitudenkurve mit mindestens
`0.125, 0.25, 0.5, 1.0`. Primaere Gegenbaseline ist die aus S1-CT direkt
folgende lineare Nullprognose `Interaktion(q) = q * Interaktion(1.0)`.
Erst ein sauberer Vergleich gegen diese Prognose kann trennen zwischen
linearer Historymodulation und einer weitergehenden Teilhinweisfunktion.

# Statischer Plan: gebundene zeitliche Teilverlaufsspur

Status: ausschließlich Planung. Keine Implementierung, Quellenproduktion,
Qualifikation oder Ausführung ist freigegeben. ME/MI bleiben gesperrt.

## Frage und Aussagegrenze

Die begrenzte Frage lautet: Kann eine zuvor gespeicherte geordnete
Wahrnehmungsfolge anhand eines späteren Teilverlaufs wiedergefunden werden,
während dieselben Einzelzustände in umgekehrter Reihenfolge nicht als dieselbe
Spur gelten?

S2-NU belegt Reihenfolgeinformation bei gleichem Rand und gleichem Multiset,
aber keinen Abruf. NW bis NZ bleiben ohne Systemverbraucher und werden nicht
wiederholt. S2-SP zeigt, dass Teiltreffer keine Gesamtidentität begründen. Der
Plan prüft daher nur exakte, sitzungsgebundene Ordnung: weder zulässige
Variation noch Quellenfortsetzung noch Objektidentität.

## Ereignisarten und Lebensdauer

Die private `TemporalTraceV1` ist vom bestehenden A/B-Memory, Feld, B4, Fast,
Slow, PPB und Hypothesen getrennt. Sie besitzt genau drei Ereignisarten:

| Ereignisart | Eingabe | Wirkung auf die Spur |
|---|---|---|
| `TRACE_FORMATION` | ein vollständiger auditiver Halbprofilzustand | schreibt höchstens vier Zustände in die aktive Spur |
| `TRACE_HINT_FRAME` | ein vollständiger auditiver Halbprofilzustand | schreibt nie; zwei aufeinanderfolgende Frames bilden nur einen read-only Hint |
| `TRACE_SESSION_CLOSE` | keine Wahrnehmungswerte | entfernt die aktive Spur endgültig |

Eine Spur entsteht erst nach vier gültigen `TRACE_FORMATION`-Ereignissen
derselben Sitzung und desselben Profils. Ihre Reihenfolge verlangt strikt
wachsende Ereignisordinale und Runtimezeiten. Native Fenstergrenzen und
NJ-Snapshotindizes bleiben je Quellennutzung unverändert gebunden; bei einer
expliziten Wiederverwendung dürfen sie nicht als Ersatzordnung über die
Ereignisfolge erzwungen werden. Diese Metadaten validieren allein die Zulässigkeit; sie gehen
nicht in die numerische Wiedererkennungsentscheidung ein.

Die aktive Spur hält genau vier Zustände. Ein fünftes
`TRACE_FORMATION`-Ereignis verwirft diese Generation mit
`TRACE_CAPACITY_EXPIRED` und beginnt **keine** gleitende Ersatzspur. Nur ein
neues, explizites Sitzungssegment kann danach wieder vier Formationen für eine
neue Generation sammeln. `TRACE_SESSION_CLOSE` verwirft eine aktive oder
unvollständige Spur als `TRACE_SESSION_CLOSED`. Hints verlängern, ersetzen und
reaktivieren keine Spur. Das ist eine technische Versuchsbedingung, keine
autonome Lernentscheidung.

## Minimaler Zustand und Abruf

Die aktive Generation enthält nur:

1. vier geordnete 48-Wert-Binary64-Vektoren in Originalindexfolge;
2. einen Vektorwertdigest je Zustand sowie einen Integritätsdigest über
   Vektor, Profil, Sitzung und Zeitbindung;
3. Profil- und Sitzungsbindung, Ordinal- und Zeitvalidierung sowie
   Trace-Generation.

Vorzeichenbehaftete Differenzvektoren werden **nicht** gespeichert: Sie sind
für den exakten Teilfolgenvergleich nicht entscheidungsnotwendig. Rohpayloads,
Quellennamen, Rezepte, Rollen, native Zeiten und Herkunftsdigests werden
weder verglichen noch als Ersatzwerte verwendet.

Ein Hint besteht aus zwei `TRACE_HINT_FRAME`-Zuständen. Nach erfolgreicher
Profil-/Sitzungs-/Zeitvalidierung prüft der Vergleich ausschließlich die zwei
48-Wert-Vektoren gegen die drei geordneten Zweizustandspositionen der aktiven
Spurgeneration. Die zeitliche Ordnung des Hints folgt nur aus seiner
Ereignisreihenfolge. Mögliche Ergebnisse:

- `TRACE_MATCH`: genau eine Position stimmt bitgleich in der Reihenfolge;
- `ABSTAIN_NO_TRACE`: keine aktive Generation, insbesondere nach Close oder
  Kapazitätsverfall;
- `ABSTAIN_ORDER_MISMATCH`: beide Werte kommen nicht als geordneter Abschnitt
  vor;
- `ABSTAIN_AMBIGUOUS_OFFSET`: mehrere Spurpositionen passen;
- typisierte technische Ablehnung bei fehlerhafter Form-, Profil-, Sitzungs-
  oder Zeitbindung.

Ein einzelner Hintframe erzeugt keinen Abruf. Die Ausgabe bleibt ein privater
Spurbeleg aus Trace-Generation und Offset, keine öffentliche A/B-Hypothese.

## Faire Baselines und feste Gegenprognosen

Die spätere Testfolge bindet vor jeder Rezeptoranalyse zwei Sitzungen.

| Sitzung | Ereignisse | Zweck |
|---|---|---|
| S1 | Formationen `a,b,c,d`; Hints `b,c`, `c,b`, `a,c`; `TRACE_SESSION_CLOSE` | eindeutiger Teilverlauf, Permutation, Nichtnachbarschaft, Verfall |
| S2 | Hint `b,c` ohne aktive Spur; Formationen `a,b,a,b`; Hint `a,b` | Abruf nach Verfall, mehrfach vorkommender Abschnitt |

Die Sollrollen liegen ausschließlich in einer getrennten Evaluationswurzel.
Der Spurvergleich erhält nur gebundene Vektoren und ihre Gültigkeitsbelege.

Alle drei Vergleicher erhalten die gleichen gespeicherten Vektoren:

| Vergleicher | Zulässige Information | Tatsächliche Ausgabe |
|---|---|---|
| geordnete Spur | Reihenfolge der vier gespeicherten Vektoren | `TRACE_MATCH` oder definierte Enthaltung |
| Einzelzustand | Inhalt der zwei Hintwerte, aber keine Hintreihenfolge | zwei getrennte Inhaltsmitgliedschaften |
| ungeordnet | kanonisches Multiset der vier gespeicherten Vektoren mit Multiplizität | Inhaltsmitgliedschaft des Hintmultisets |

Die Einzelzustands- und ungeordnete Baseline dürfen also `b,c` und `c,b` beide
als inhaltlich vorhanden melden. Für diese beiden Hints müssen ihre Ergebnisse
bitgleich sein. Sie erhalten kein künstliches Zulassungsverbot; zwei
Inhaltsmeldungen oder zwei Enthaltungen sind regulär und werden getrennt vom
geordneten Spururteil ausgewertet. Ein Ordnungsvorteil besteht nur, wenn der
Spurvergleich `b,c` eindeutig findet und `c,b` nicht zulässt, während die
beiden Baselines tatsächlich gleich bleiben.

Die Nichtnachbarschaft `a,c` muss trotz vorhandener Einzelzustände als
`ABSTAIN_ORDER_MISMATCH` enden. Die zweite Spur `a,b,a,b` besitzt die
Abschnitte `a,b` an zwei Offsets; ihr Hint `a,b` muss
`ABSTAIN_AMBIGUOUS_OFFSET` ergeben. Nach dem Close von S1 muss `b,c` in S2
`ABSTAIN_NO_TRACE` liefern. Diese drei Kontrollen sind keine technischen
Fehler, sondern vorgebundene fachliche Grenzen.

## Vollständige vorläufige Budgets

Der spätere Versuch hat exakt 18 wahrgenommene Audioendpunkte:

- acht `TRACE_FORMATION`-Endpunkte, vier je Sitzung;
- zehn `TRACE_HINT_FRAME`-Endpunkte, sechs in S1 und vier in S2;
- fünf resultierende read-only Hintentscheidungen;
- zwei `TRACE_SESSION_CLOSE`-Ereignisse ohne Payload.

Damit liegen acht Formationen und 20 Ereignisse unter den bestehenden
Obergrenzen von 20 Formationen und 28 Ereignissen. Der spätere Anschluss bleibt
rezeptor- und feldfrei außerhalb der bereits verwendeten audiovisuellen
Runtime: höchstens 18 direkte Audioanalysen und 18 NJ-Projektionen, null
Feldkontakte, null A/B-Scans und keine Hypothesenanwendung.

Für die vier aktiven Zweiframe-Hints mit Spur stehen je drei Kandidatoffsets,
zwei Vektoren und 48 Werte bereit: maximal 1.152 produktive
Komponentengleichheiten. Einzelzustands- und ungeordnete Baseline prüfen je
1.536 Komponentengleichheiten; zusammen 4.224. Die unabhängige Direktrechnung
wiederholt exakt diese 4.224 Gleichheiten, ohne produktive Helfer zu nutzen.
Der Hint nach Close prüft nur die fehlende Generation und führt keine
Vektorvergleiche aus.

Die aktive Spur speichert höchstens `4 * 48 * 8 = 1.536` Byte native
Vektorwerte zuzüglich ihrer notwendigen Bindungen; zwei Sitzungen werden nicht
gleichzeitig aktiv gehalten. Vor Umsetzung sind vollständige Zustandshülle,
Generations-, Fehler- und Verifikationsbelege gegen die bestehenden Grenzen
von 98.304 Byte Zustand, 65.536 Byte Metadaten und 262.144 Byte Zusatzhülle
zu bilanzieren. Reicht die Bilanz nicht, bleibt der Anschluss gesperrt; es
gibt keine Grenzerhöhung, Kürzung oder Metadatenauslagerung.

## Widerlegung und verbleibende Grenze

Der Ansatz ist widerlegt oder begrenzt, wenn der passende Teilverlauf nicht
eindeutig gefunden wird, die Permutation oder Nichtnachbarschaft zugelassen
wird, die Mehrfachposition eindeutig erscheint, ein Hint die Spur verändert,
eine abgelaufene Generation verfügbar wird oder eine Baseline Ordnung über
Nebenmetadaten unterscheidet.

Auch ein vollständiger Erfolg belegt nur exakte Wiederfindung einer kleinen,
explizit sitzungsgebundenen Reihenfolge. Er belegt kein gelerntes Verdichten,
keine Variantenrobustheit, keine Quellen-/Objektidentität und keinen Nutzen
für die bestehende A/B-Auflösung.

WEITER: Zuerst ist die technische und fachliche Trennung dieser begrenzten
Sequenzspur zu prüfen. Erst danach wären Quellen, Anschluss und eine neutrale
Qualifikation gesondert zu binden.

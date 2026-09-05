# S2-MC: Rollenfreier Lernlebenszyklus

## Zweck

S2-MC bindet genau eine zeitlich zusammenhaengende Wahrnehmungsgeschichte, in
der derselbe visuelle Zwei-Blick-Hinweis vor einer Erfahrung zur Enthaltung und
nach realer Bildung eines stabilen Prototyps zu einem kontrollierten
`B_STABLE`-Abruf fuehren muss. Unbekannte und quellenwiderspruechliche Hinweise
muessen danach weiterhin enthalten werden.

Der Laufpfad kennt ausschliesslich neutrale Ereignis-, Quellen-, Zeit- und
Ownerbindungen. Begriffe wie Ziel, Lernen, Druck, bekannt, unbekannt oder
Sollstatus existieren nur in der nachgelagerten Evaluationswurzel.

## Unveraenderte Grundlagen

Der Vertrag verwendet ohne Aenderung:

- das Default-Live-Profil mit `48 + 288` Rezeptorwerten;
- die visuellen Masken `VIEW_A_96`, `VIEW_B_96` und `UNION_192` aus S2-LZ;
- den posebereinigten maskenkonditionierten Formdeskriptor aus S2-LY;
- die fluechtige Zwei-Blick-Integration aus S2-MA;
- die reale `B_STABLE`-Slotprojektion und Direktbaseline aus S2-MB;
- die bestehenden Feld-, AV-Paarungs- und atomaren Memoryadapter.

Gebundene Wurzeln:

```text
S2-LZ plan digest:
ae5bbba16138673e429817f32d9cb1f6bd695f58590ef23740ec5e3e3391d06c

S2-MB result digest:
7334bc17c35928873f0a5ed836861deac7bdd10edfe20a5a6fd087a2874096cc

Default-Live config digest:
72c74a8298d98013ef7d1552f764e46c4df1935703f0e4188f11a6eca0479beb
```

Es entstehen keine neuen Masken, Deskriptoren, Schwellen, Rezeptoren,
Memoryregeln oder Feldmechaniken.

## Neutrale Ereignisfolge

Die unveraenderliche Ausfuehrungswurzel enthaelt nur folgende technischen
Spezifikationen:

```text
e01  PARTIAL_VISUAL_CUE  source-005  VIEW_A_96
e02  PARTIAL_VISUAL_CUE  source-005  VIEW_B_96

e03  COMPLETE_AV_PERCEPTION  source-001
e04  COMPLETE_AV_PERCEPTION  source-001
e05  COMPLETE_AV_PERCEPTION  source-001
e06  COMPLETE_AV_PERCEPTION  source-001

e07  COMPLETE_AV_PERCEPTION  source-033
e08  COMPLETE_AV_PERCEPTION  source-033
e09  COMPLETE_AV_PERCEPTION  source-033
e10  COMPLETE_AV_PERCEPTION  source-033
e11  COMPLETE_AV_PERCEPTION  source-033
e12  COMPLETE_AV_PERCEPTION  source-033
e13  COMPLETE_AV_PERCEPTION  source-033
e14  COMPLETE_AV_PERCEPTION  source-033
e15  COMPLETE_AV_PERCEPTION  source-033

e16  PARTIAL_VISUAL_CUE  source-005  VIEW_A_96
e17  PARTIAL_VISUAL_CUE  source-005  VIEW_B_96
e18  PARTIAL_VISUAL_CUE  source-025  VIEW_A_96
e19  PARTIAL_VISUAL_CUE  source-025  VIEW_B_96
e20  PARTIAL_VISUAL_CUE  source-005  VIEW_A_96
e21  PARTIAL_VISUAL_CUE  source-011  VIEW_B_96
```

Jedes Ereignis besitzt einen eigenen Einmal-Owner. Die native visuelle Zeit
und die gemeinsame Feldzeit schreiten strikt fort. Wiederholter
Wahrnehmungsinhalt verwendet neue Zeitfenster und neue Ereignisbelege. Alle 21
Ereignisse erzeugen einen unabhaengigen Feldkontakt. Nur `e03...e15` fuehren
genau eine atomare AV-Memoryformation aus.

`source-033` ist der neutrale Laufalias fuer die unveraenderte, bereits
digestgebundene S2-JX-D1-/D_FAR-AV-Fixture. Weder Alias noch Ereignisform
enthalten deren spaetere Evaluationsrolle.

Vor `e01` wird das Feld ausschliesslich aus der gebundenen Default-Live-
Dockgeometrie und Nullkomponenten als `PRE_CONTACT` aufgebaut. Dabei entsteht
weder eine Rezeptorverteilung noch ein Snapshot oder ein vorweggenommener
AV-Kontakt. `e01` ist der erste reale Feldschritt; danach ist der Feldzustand
`COMPLETED`.

## Lebenszyklus und Projektion

Nach `e02`, `e17`, `e19` und `e21` wird das jeweilige Zwei-Blick-Fenster
vollstaendig ausgewertet und geloescht. Die aktuelle visuelle Slow-Bank wird
dabei direkt aus dem bereits vorhandenen Zustand gelesen; es findet keine
Vollprobe und keine zweite Memoryabfrage statt.

Die Kandidatenprojektion akzeptiert `0...4` stabile visuelle Slots:

- kein stabiler Slot ergibt den typisierten Befund `ABSENT_VALID` und zwingend
  Enthaltung;
- vorhandene Slots muessen Support mindestens `stable_after` sowie gueltige
  Slot-, Prototyp-, Kalibrations- und Zustandsdigests besitzen;
- jeder vorhandene Slot wird unveraendert durch die S2-MB-Projektion gebunden;
- die Entscheidung bleibt "genau ein Kandidat innerhalb seiner vorab
  gebundenen Huelle", ohne Rangfolge oder Fallback;
- die unabhaengige Direktbaseline bildet den Nullkandidatenfall selbst ab und
  teilt keinen Entscheidungshelfer mit dem Kontextarm.

`CURRENT_ONLY` erzeugt in allen vier Faellen keine Kontexthypothese. Eine
zugelassene Form bleibt getrennte Hypothese und wird weder als beobachteter
Rezeptorwert noch als Feldkontakt ausgegeben.

## Statische Erreichbarkeit

Vor `e03` ist der frische Memoryzustand leer. Der erste `source-005`-Hinweis
endet daher nach zwei gueltigen Feldkontakten als `ABSENT_VALID`.

`source-001` wird viermal bitidentisch gebildet. Wie in S2-MB entsteht im
visuellen Slow-Slot die Folge `CREATED -> MATCHED -> MATCHED` mit Support `3`;
der resultierende Binary64-Prototypdigest ist
`8c1afc598b3c8a54c5b3f72d62581cad5894267bad4456a361fa8c1fc9066e4a`.

Neun anschliessende `source-033`-Formationen fuellen B4 vollstaendig mit den
spaeteren Wahrnehmungen und lassen den frueheren Fast-Zusammenhang ablaufen.
Sie bilden einen getrennten stabilen visuellen Slot. Die Distanz von
`source-005` zum ersten stabilen Formmodell ist `0.0007429922323539343` und
liegt innerhalb dessen unveraenderter Kalibrationshuelle
`0.002439408479636238`; der Druckslot passt nicht.

`source-025` liegt ausserhalb beider realer Huellen. Das letzte Blickpaar
besitzt zwei verschiedene Quellen und Payloaddigests und darf deshalb keine
`UNION_192`-Evidenz bilden. Diese Beziehungen wurden im gebundenen S2-MB-Lauf
bereits mit denselben Rezeptor-, Projektions- und Kalibrationsfunktionen
ermittelt; S2-MC aendert weder Werte noch Grenzen.

## Schreib- und Read-only-Grenzen

- `e03...e15` schreiben erwartungsgemaess den Memoryzustand.
- `e01...e02` lesen den frischen Zustand nur fuer den Abwesenheitsbefund.
- `e16...e21` lesen den finalen Zustand; ihr gemeinsamer Memory-Pre-/Postdigest
  muss identisch bleiben.
- Feldschritte sind fuer alle 21 Ereignisse schreibend und werden durch einen
  Memory-, Scan- oder Kontextfehler nicht zurueckgenommen.
- Die fluechtigen Zwei-Blick-Werte werden nach jeder Paarentscheidung
  verworfen und niemals an `B_STABLE` uebergeben.
- Rohframes und PCM-Fenster werden nach der Rezeptorreduktion verworfen.

## Gebundene Zaehlung

```text
Stromereignisse                 21
vollstaendige AV-Formationen   13
visuelle Teilblicke             8
Feldschritte                    21
Zwei-Blick-Abschluesse           4
Kontextentscheidungen            4
Direktbaselineentscheidungen     4
CURRENT_ONLY-Befunde             4
```

Ein einzelner atomarer Ergebnisbeleg unter `262144` Byte genuegt. Eine neue
Operationsregistry, ein append-only Recorder oder eine neue Laufplattform sind
ausgeschlossen.

## Evaluationswurzel

Erst nach vollstaendig erzeugten Armresultaten ordnet der getrennte Auswerter
die neutralen Ereignisse fachlich zu:

```text
e01/e02  vor Erfahrung       -> ABSTAINED / ABSENT_VALID
e03-e06  wiederholte Bildung -> visueller B_STABLE-Support 3
e07-e15  spaetere Folge      -> Ziel nicht mehr in B4 oder Fast
e16/e17  gleicher Hinweis    -> ADMITTED aus B_STABLE
e18/e19  unbekannter Hinweis -> ABSTAINED / NO_MODEL_WITHIN_ENVELOPE
e20/e21  Quellenkonflikt     -> ABSTAINED / PAIR_INCOMPATIBLE_NO_UNION
```

Zielrollen, Sollentscheidungen und vollstaendige Zielwerte sind keine Eltern
des Laufpfads. Kontextarm und Direktbaseline muessen in Status, ausgewaehltem
Slot und Entscheidungsdigest uebereinstimmen.

## Abschlussregeln

`S2MC_ROLE_FREE_LEARNING_LIFECYCLE_CONFIRMED` ist nur zulaessig, wenn:

- alle 21 Feldkontakte gueltig und zeitlich geordnet sind;
- die erste Teilwahrnehmung ohne Kontext enthaelt;
- der spaetere reale Slot Support `3` besitzt und aus B4/Fast verschwunden ist;
- derselbe Hinweis danach genau diesen `B_STABLE`-Slot zulaesst;
- unbekannter und quellenwiderspruechlicher Hinweis enthalten;
- Current-only unveraendert bleibt und Direktbaseline exakt uebereinstimmt;
- alle vier Abrufphasen den jeweiligen Memoryzustand unveraendert lassen;
- kein Rohpayload, Sollwert oder Rollenlabel in einen Funktionsarm gelangt.

Ein technischer Quellen-, Zeit-, Digest-, Owner- oder Belegfehler ergibt
`NOT_EVALUABLE`. Ein vollstaendiger, verifizierter Lauf mit abweichender
fachlicher Entscheidung ist `S2MC_ROLE_FREE_LEARNING_LIFECYCLE_FALSIFIED`.
Keine Abweichung autorisiert Retry, Fixturewechsel oder Schwellenanpassung.

## Aussagegrenze

Ein spaeterer Erfolg wuerde Lernen als zeitliche Zustandsaenderung in einem
zusammenhaengenden Wahrnehmungsstrom belegen: derselbe Teilhinweis ist vor der
Erfahrung nicht nutzbar und danach ueber einen real gebildeten stabilen
Prototyp nutzbar. Die bekannte adaptive Prototypbildung, Formprojektion und
Direktbaseline duerfen den Befund vollstaendig erklaeren. Nicht belegt waeren
Semantik, autonome Maskenbildung, allgemeine Open-Set-Erkennung,
Kontextrueckwirkung oder neue MCM-Physik.

## Ergebnis

Die erste neutrale Komponentenqualifikation bestand mit `8/8`. Der erste
Hauptversuch `...-01` stoppte vor dem ersten Feldschritt als `NOT_EVALUABLE`,
weil der private Runner einen visuellen Teilhinweis unzulaessig zur
Feldinitialisierung verwendete. Feld- und Memorymutation blieben `0`; es fand
keine Funktionsauswertung statt.

Die enge Korrektur verwendete danach den bereits qualifizierten
`PRE_CONTACT`-Zustand aus Default-Live-Dockgeometrie und Nullkomponenten. Die
neue Qualifikation bestand einmalig mit `9/9`, Exit-Code `0` und `OK`. Der neue
Lauf `s2mc-role-free-learning-lifecycle-20260905-02` wurde genau einmal
ausgefuehrt und genau einmal read-only als `RECORDING_COMPLETE` verifiziert.

```text
s01  ABSTAINED  ABSENT_VALID
s02  ADMITTED   ppb1.visual.default-live.v1.slot.000
s03  ABSTAINED  NO_MODEL_WITHIN_ENVELOPE
s04  ABSTAINED  PAIR_INCOMPATIBLE_NO_UNION
```

Alle `21` Ereignisse erzeugten einen Feldschritt. Genau `13` vollstaendige
AV-Wahrnehmungen schrieben Memory. Die `8` Teilblicke und alle vier
Kontextentscheidungen veraenderten Memory nicht. Produktarm und unabhaengige
Direktbaseline waren digestgleich. Damit ist der gebundene rollenfreie
Lernlebenszyklus fuer diese eine Wahrnehmungsfamilie bestaetigt.

# S2-MD: Quellenneutraler MCM-Lernruntime - Materialisierbarkeitsaudit

## Status

`S2MD_RUNTIME_IMPLEMENTATION_BLOCKED`

Dieser rein statische Audit prueft, ob der bestaetigte S2-MC-Lebenszyklus ohne
Szenario-, Familien-, Ziel- oder Sollrollen in einen allgemeinen privaten
Lernruntime ueberfuehrt werden kann. Es wurden keine Module implementiert,
keine Tests ausgefuehrt und keine Rezeptor-, Feld-, Memory- oder
Kontextfunktion aufgerufen.

S2-MC bleibt als begrenzter, gueltiger Funktionsbefund unveraendert. Der Audit
begrenzt ausschliesslich dessen Verallgemeinerung zu S2-MD.

## Beabsichtigte Runtimegrenze

Der angeforderte Runtimepfad lautet:

```text
kanonisches AV-Ereignis
-> gemeinsamer unveraenderlicher Wahrnehmungsbeleg
-> unabhaengiger Feldzweig
-> atomarer A_RECENT-/B_STABLE-Memoryzweig
-> bei Teilblicken: fluechtiges Zwei-Blick-Fenster
-> transparente Kontexthypothese oder Enthaltung
```

Dabei duerfen keine Szenario-, Familien-, Ziel- oder Bedeutungsrollen im
Runtimepfad vorkommen. Es duerfen weder neue Schwellen noch neue
Deskriptoren, Speicherbereiche oder Lernregeln eingefuehrt werden.

## Statisch wiederverwendbare Teile

### Rollenfreier Strom und getrennte Zweige

Der private S2-LM-Prozessor besitzt Ereignisowner pro Aufruf, haelt den Strom
nach einem Ereignis offen und behandelt Feld und Memory als unabhaengige
Geschwisterzweige. Vollstaendige AV-Ereignisse koennen deshalb ohne neue
Kopplung an Feld und atomaren B4-/TSPM-Verbund weitergereicht werden.

### Feldinitialisierung

Die in S2-MC qualifizierte `PRE_CONTACT`-Bindung bildet den noch unberuehrten
Feldzustand ohne unzulaessigen Snapshot ab. Nach dem ersten realen Feldkontakt
kann der bestehende abgeschlossene Felddigest verwendet werden.

### Endliche Memoryzustaende

Die vorhandenen 336-Werte-Adapter stellen endliche Zustaende fuer B4, Fast und
beide PPB-Banken bereit. Oeffentlich bleiben diese in `A_RECENT` und
`B_STABLE` gegliedert. Die Memorykerne muessen fuer S2-MD nicht geaendert
werden.

### Fluechtige Zwei-Blick-Mechanik

S2-MA begrenzt das visuelle Wahrnehmungsfenster auf hoechstens zwei gebundene
Blicke und verwirft es nach Auswertung, Konflikt, Ablauf oder Quellenwechsel.
Die Teilansichten werden nicht nach `B_STABLE` uebernommen.

## Blockierender Befund MD-B01

### Externe Anwendbarkeitshuelle

Die reale S2-MC-Zulassung eines visuellen `B_STABLE`-Kandidaten ist nicht
allein aus dem PPB-Slot ableitbar. `BStableCalibrationBindingV1` verlangt pro
Slot unter anderem:

- `calibration_id`;
- `calibration_radius`;
- `calibration_digest`;
- `expected_prototype_values_digest`.

Der Scan akzeptiert einen Kandidaten nur, wenn der Abstand des
maskenkonditionierten Formdeskriptors dessen `calibration_radius` nicht
ueberschreitet. Der PPB-Slot selbst enthaelt Prototyp, Support und technische
Slotprovenienz, aber keine qualifizierte Zwei-Blick-Anwendbarkeitshuelle.

### S2-MC-spezifische Bindung

Der S2-MC-Runner bezieht die Huelle aus der versiegelten S2-LZ-Auswertung:

```text
prior["calibration_envelopes"]["representations"]["UNION_FORM_192"]
rows["model-01"]
```

Anschliessend wird der reale Slow-Slot explizit an `model-01` gebunden. Die
AV-Ereignisse des Laufs sind rollenfrei, die spaetere Kandidatenzulassung ist
damit jedoch weiterhin von einer externen, versuchsspezifischen Modellrolle
abhaengig.

### Konsequenz

Ein allgemeiner S2-MD-Runtime kann den S2-MC-Befund unter den vorgegebenen
Grenzen nicht reproduzieren:

1. Die S2-LZ-Huelle in den Runtimepfad zu uebernehmen, wuerde eine
   Szenario-/Familienrolle einfuehren.
2. Einen globalen Radius zu waehlen, waere eine neue Schwelle.
3. Einen Radius nachtraeglich aus dem fertigen Prototyp oder aus
   Auswertungsdaten abzuleiten, waere zirkulaer.
4. Eine Huelle aus der Formationsgeschichte zu lernen, waere eine neue
   prospektiv zu qualifizierende Evidenz- und Lernregel.
5. Ohne Huelle zuzulassen oder still auf einen anderen Vergleich
   zurueckzufallen, wuerde die bestaetigte Fail-Closed-Regel aendern.

Damit fehlt keine Laufhuelledetailarbeit, sondern eine fachlich autorisierte,
rollenfreie Anwendbarkeitsevidenz fuer reale `B_STABLE`-Formkandidaten.

## Weitere Materialisierungsluecken

### MD-B02: Endliche statt fortlaufende kanonische Zeit

Die qualifizierte S2-JO-Grenze bindet alle Fenster an genau eine
`200_000_000`-Tick-Episode. `_require_window` weist jedes spaetere Fenster ab.
Sie ist damit eine gueltige endliche Quellenreferenz, aber noch keine
kanonische Zeitdomane fuer einen persistent offenen Runtime.

Eine Laufzeitverlaengerung, Epochenverkettung oder neue Clockregel ist in
S2-MD nicht freigegeben.

### MD-B03: Einzelblickscan statt Zwei-Blick-Routing

S2-LM leitet jedes `PARTIAL_VISUAL_CUE` unmittelbar an den qualifizierten
S2-KQ-Einzelblickscan und dessen Direktbaseline weiter. Der Prozessor besitzt
keinen neutralen Routingzustand, der zwei visuelle Teilereignisse zuerst in
S2-MA sammelt und erst danach gegen reale Slow-Slots auswertet.

Diese Luecke ist technisch begrenzt, darf aber erst geschlossen werden, wenn
MD-B01 eine gueltige rollenfreie Kandidatenanwendbarkeit bereitstellt.

## Nichtzirkularitaet

Eine zulaessige spaetere Loesung muss folgende Reihenfolge einhalten:

```text
kanonische Rohquelle
-> Rezeptorwerte und Quellenprovenienz
-> vollstaendige Formationen
-> PPB-Uebergangskette
-> rollenfreie Anwendbarkeitsevidenz
-> spaetere Teilblicke
-> maskenkonditionierter Vergleich
-> Zulassung oder Enthaltung
-> getrennte Auswertung
```

Nicht zulaessig sind Rueckkanten von Teilblick, Sollstatus, Holdoutrolle oder
Auswertung zur Bildung der Anwendbarkeitsevidenz.

## Entscheidung

S2-MD wird in der angeforderten Form nicht implementiert. Der Runtime duerfte
sonst entweder versteckte S2-LZ-Modellrollen tragen oder eine neue Schwelle
beziehungsweise Lernregel ohne prospektive Qualifikation einfuehren.

Der naechste fachlich notwendige Schritt ist kein Runtimebau, sondern eine
enge Entscheidung ueber rollenfreie `B_STABLE`-Anwendbarkeitsevidenz. Soll
diese Evidenz aus der eigenen homogenen Formationskette entstehen, ist das
ausdruecklich eine neue, separat zu falsifizierende Lernregel. Ohne eine solche
Freigabe bleibt S2-MC der gueltige begrenzte Nachweis und S2-MD blockiert.

Die README wird durch diesen Forschungs- und Auditbefund nicht erweitert.

## Gebundener Quellstand

Auditbasis ist Commit:

```text
0914abeecbcc578c90a7256e580c6fd5fac2480f
```

Gebundene Quellhashes:

```text
ab1a3b93929ec483e03e2b5a1a303a3a6d0ba3930463d1bce3998cbdb582356d  tools/_s2mb_private_bstable_two_view.py
2e53c3ecc9932c9e6dffc3f081a91bc9b2640c65575d70424ffc73e7955a0d91  tools/_s2ma_private_arecent_two_view_integration.py
d681c25dfec603faedfaea08875bf7c75a0299e745514c73c9ec7877d1fa691d  tools/_s2mc_private_learning_lifecycle_runner.py
50a39fb3865fbd11b3577f79db2983f9dd3260262dee0f199ae5f884bed4ef71  tools/_s2jo_private_canonical_av_boundary.py
84c5650f7f52fe13eb0b8248ab73656dbb67f17fbdd93b2dfc520bacfec7e127  tools/_s2lm_private_role_free_stream_processor.py
```


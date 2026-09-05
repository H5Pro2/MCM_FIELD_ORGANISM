# S2-MA: Fluechtige A_RECENT-Zwei-Blick-Integration

## Vertrag

S2-MA integriert hoechstens zwei zeitlich aufeinanderfolgende visuelle
Teilansichten als private, fluechtige Funktion von `A_RECENT`. Die Funktion
ist keine dritte Memoryebene und veraendert weder B4, Fast, `B_STABLE` noch das
MCM-Feld.

Ein Blick bindet ausschliesslich:

- 96 tatsaechlich beobachtete Rezeptorpositionen und Werte;
- Maske, Quelle, Payloaddigest und Rezeptorgeometrie;
- strikt fortschreitende native Zeit;
- einen eigenen Einmal-Owner;
- optional den Digest eines bereits unabhaengig entstandenen Feldkontakts.

Der erste gueltige Blick erzeugt nur `PENDING`. Der zweite Blick darf mit dem
ersten ausschliesslich dann vereinigt werden, wenn Quelle, Payload und
Geometrie identisch sind, die Maskenrollen `A` und `B` bilden und der zweite
Tick innerhalb des gebundenen Ein-Tick-Fensters liegt. Die Vereinigung besteht
exakt aus den beiden disjunkten 96er-Sichten.

Quellenwechsel, Geometriekonflikt, falsche Maskenfolge oder Ablauf fuehren zur
Enthaltung. In jedem terminalen Pfad wird das Fenster geloescht. Auch nach
erfolgreicher Auswertung wird keine Teilansicht behalten. Wiederverwendete
Owner stoppen fail-closed.

Die Open-Set-Entscheidung ist unveraendert die qualifizierte S2-LZ-
Direktfunktion. S2-MA fuehrt keine weitere Schwelle, Rangfolge oder
Auswahlregel ein. Der begrenzte Integrationslauf muss fuer alle 20 versiegelten
S2-LZ-Faelle exakt dieselben Status-, Modell-, Grund- und Entscheidungsdigests
wie der `UNION_192_OPEN_SET`-Arm liefern.

## Grenzen

- keine Imputation oder Rekonstruktion verdeckter Werte;
- keine Uebergabe der Ansichten an `B_STABLE`;
- keine Feld-, Memory- oder Kontextmutation;
- Feldkontakte bleiben auch bei Integrationsfehlern gueltig und unabhaengig;
- Rohframes werden nach der Rezeptorreduktion verworfen;
- keine allgemeine Open-Set- oder Objektverfolgungsbehauptung.

## Ergebnis

Die neutrale Qualifikation bestand mit `12/12`, Exit-Code `0` und `OK`. Der
begrenzte Lauf reproduzierte anschliessend alle 20 versiegelten S2-LZ-Faelle
exakt:

- `20/20` gleiche Statuswerte, Modellbindungen und Entscheidungsgruende;
- `20/20` gleiche interne Open-Set-Entscheidungsdigests;
- Fenster nach jedem Fall und am Laufende leer;
- keine Teilansicht fuer `B_STABLE` behalten;
- Memorykern-, Kontext- und Feldaufrufe jeweils `0`;
- separate read-only Verifikation: `RECORDING_COMPLETE`.

Das Ergebnis belegt, dass die qualifizierte Zwei-Blick-Evidenz als fluechtige
interne Funktion von `A_RECENT` materialisiert werden kann, ohne eine dritte
Memoryebene oder eine Rueckwirkung auf Feld und Memory einzufuehren.

Ergebnisdatei: `48.826` Byte, SHA-256
`d7062c8dcb7bcff1b288b935ab91dfd5eba714958fd858c2df02d1b9bf4e809c`.

Belege:

- `reports/s2ma/s2ma-arecent-two-view-integration-20260905-01/comparison.json`
- `reports/s2ma/s2ma-arecent-two-view-integration-20260905-01/verification.json`
- `reports/s2ma/s2ma-transient-arecent-integration-qualification-20260905-01/qualification.json`

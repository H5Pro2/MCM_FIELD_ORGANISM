# S1-RD: Statischer Drei-Knoten-A/B/C-Geometrie-, Lastanpassungs- und Frischprojektionsaudit

## Status und Umfang

S1-RD prueft ausschliesslich, ob die vorhandene
`THREE_NODE_OPEN_LINE`-Geometrie aus S1-JN/S1-JV gemeinsam folgende
S1-PZ-Pflichten tragen kann:

- `A_FOCAL` als fokalen Ort;
- `B_LOCAL` als direkt lokalen Konkurrenzort;
- `C_REMOTE` als nicht direkt lokalen Kontrollort;
- geometrisch und exogen angepasste B/C-Belastung;
- dieselbe oeffentliche Frischprojektion fuer alle 14 Baseline-Modellrollen.

Der Audit registriert keine Geometrie oder Rollenbelegung, fuehrt keinen
Test und keinen Feldlauf aus, implementiert keine Mappingzeile oder
Frischfabrik und bindet keine Kontaktwerte, Intervalle, Parameter oder
Fixture.

Auditentscheidung:

```text
THREE_NODE_OPEN_LINE_HAS_EXACT_A_B_AND_B_C_EDGES_WITH_NO_A_C_EDGE
ONE_TO_ONE_DOCKS_SUPPORT_VALUE_AND_TIME_MATCHED_B_C_EXOGENOUS_LOAD
NO_NODE_ROLE_ASSIGNMENT_SATISFIES_LOCAL_B_REMOTE_C_AND_GEOMETRIC_B_C_MATCH
PUBLIC_FRESH_PROJECTION_IS_STRUCTURALLY_COMPATIBLE_ACROSS_ALL_FOURTEEN_ROLES
CURRENT_S1JV_GEOMETRY_SET_CANNOT_SUPPORT_THE_S1RA_MATRIX
A2_AND_M4_BRIDGE_IMPLEMENTATION_REMAINS_BLOCKED
NO_REGISTRATION_NO_IMPLEMENTATION_NO_EXECUTION_NO_RESULT_DECISION
```

## Vorhandene Drei-Knoten-Geometrie

Die S1-JN-/S1-JV-Identitaet bindet:

| Rolle | Bestand |
|---|---|
| Feld | `mcm.s1jn.field.3n` |
| Layer | `mcm.s1jn.layer.3n` |
| Geometrie | `mcm.s1jn.geometry.3n` |
| Knoten | `node-a`, `node-b`, `node-c` an den Positionen 0, 1, 2 |
| Sampleoffsets | direkter linker und rechter Nachbar |
| Periodizitaet | keine |
| Kanten | `node-a--node-b`, `node-b--node-c` |
| Dock | ein gemeinsamer auditiver Drei-Knoten-Dock |
| Carrierabbildung | `carrier-a->node-a`, `carrier-b->node-b`, `carrier-c->node-c` |

Der vorhandene Kanteninventarhelper bestaetigt fuer diese Form genau eine
zusammenhaengende offene Linie. `node-a` und `node-c` besitzen jeweils einen
direkten Nachbarn. `node-b` besitzt zwei direkte Nachbarn.

## Verbindliche S1-PZ-Geometriekriterien

Fuer eine zulaessige Rollenbelegung muessen gleichzeitig gelten:

1. A und B teilen das registrierte lokale Umfeld;
2. A und C teilen dieses direkte lokale Umfeld nicht;
3. B und C sind fuer den Kontrollvergleich geometrisch angepasst;
4. B und C koennen denselben exogenen Input mit derselben Zeitstruktur
   erhalten;
5. die Rollen werden nur durch Geometrie und Input materialisiert, nicht
   durch ein Modelllabel.

S1-RD liest `lokales Umfeld` fuer diese vorhandene erste Geometrie als
direkte Kantenadjazenz. Eine nachtraegliche Definition, die C trotz direkter
A-C-Kante als entfernt bezeichnet, waere nicht fail-closed.

## Vollstaendiger Rollenbelegungsaudit

Die sechs moeglichen A/B/C-Zuordnungen zerfallen in zwei Klassen.

### Klasse 1 - A ist ein Randknoten

Wird A auf `node-a` oder spiegelbildlich auf `node-c` gelegt, ist genau der
mittlere Knoten direkt lokal und der gegenueberliegende Randknoten nicht
direkt benachbart.

Damit erzwingt die lokale/entfernte Rollenbedingung:

```text
A = Rand
B = Mitte
C = gegenueberliegender Rand
```

Die lokale/entfernte Trennung ist dann eindeutig. B und C sind aber nicht
geometrisch angepasst:

- B besitzt zwei direkte Feldnachbarn;
- C besitzt nur einen direkten Feldnachbarn;
- B liest lokale Samples von beiden Seiten;
- C liegt an einer offenen Grenze;
- B liegt auf zwei Feldkanten, C nur auf einer.

Gleiche Rezeptorwerte und gleiche Dauer beseitigen diesen strukturellen
Unterschied nicht. Eine Feldreaktion kann sich allein wegen Grad und
Randlage unterscheiden.

### Klasse 2 - A ist der mittlere Knoten

Wird A auf `node-b` gelegt, sind die beiden Randknoten geometrisch
spiegelsymmetrisch. Sie koennen deshalb als B und C dieselbe Randrolle und
dieselbe exogene Last tragen.

Beide Randknoten sind jedoch direkt mit A verbunden. Es gibt keinen
nichtlokalen C-Ort. Die Rollenbedingung `C_REMOTE` ist damit verletzt.

### Ergebnis ueber alle Permutationen

Keine Rollenbelegung erfuellt alle Kriterien gleichzeitig:

| A-Lage | A/B lokal | A/C nichtlokal | B/C geometrisch angepasst | Gesamtstatus |
|---|---|---|---|---|
| Rand | ja | ja | nein | ungueltig |
| Mitte | ja | nein | ja | ungueltig |

Die Spiegelung der Linie aendert keine dieser Aussagen.

## Exogene B/C-Lastanpassung

Die Dockoberflaeche ist fuer sich geeignet:

- jeder Knoten besitzt genau einen eigenen Carrier;
- eine Rezeptorframebreite von drei deckt alle Orte atomar ab;
- B und C koennen denselben Kontaktwert bei sonst nullgesetzten Carriern
  erhalten;
- beide Frames koennen dieselbe Feldzeit, Dauer und Ordinalstruktur tragen;
- Nullkontakt kann ueber alle drei Carrier wertidentisch materialisiert
  werden.

Damit gilt:

```text
EXOGENOUS_VALUE_SHAPE_AND_TIME_MATCHING_POSSIBLE
```

Diese Moeglichkeit reicht nicht aus. Die unterschiedliche Feldnachbarschaft
von B und C in Klasse 1 bleibt eine alternative technische Erklaerung fuer
jeden spaeteren Kontrast.

## Warum Align die Geometrie nicht repariert

`ALIGN_READOUT_SH` darf nur unmittelbar vor einer Probe aktuellen Kontakt, S
und H angleichen. Es darf weder Feldzeit verbrauchen noch Geometrie,
Nachbarschaft oder privaten Carry veraendern.

Eine Angleichung kann daher nicht:

- den zusaetzlichen Nachbarn von B entfernen;
- C eine zweite Kante geben;
- die vorherige B- oder C-Geschichte geometrisch gleich machen;
- eine Randlage in eine Mittellage umwandeln.

Eine korrigierende Gewichtung, Normierung oder S/H-Klemme waehrend der
Geschichte waere eine neue Geometrie- oder Feldregel und ist gesperrt.

## Historische Drei-Knoten-Profile sind kein Ersatz

Die alten P_IK- und P_IN-Fixtures verwenden dieselbe Drei-Knoten-Linie, aber
keine vollstaendige S1-PZ-B/C-Remote-Kontrolle. Insbesondere ersetzen die
historischen A-, B-, Gap- und Probegrenzen keine geometrisch angepasste
C-Geschichte.

Ihre gespeicherten Grenzwerte, Profilnamen und Ergebnisvektoren duerfen
nicht zur neuen Rollenbelegung, Lastkorrektur oder Geometrievalidierung
herangezogen werden.

## Oeffentliche Frischprojektion

Unabhaengig vom A/B/C-Fehler besitzt die Drei-Knoten-Identitaet eine
geeignete oeffentliche Frischform:

- identische Feld-, Layer-, Geometrie-, Dock- und Knotenidentitaeten;
- kanonische Knotenordnung `node-a`, `node-b`, `node-c`;
- S und H an allen Knoten auf positivem Nullwert;
- Rezeptorkontakte auf null;
- keine lokalen Samples im Frischzustand;
- gemeinsamer initialer Feldtakt;
- keine letzte Rezeptorverteilung.

Diese oeffentliche Projektion ist fuer alle Modellrollen strukturell
kompatibel.

## Modellrollenabgleich der Frischprojektion

| Modellgruppe | Private Frischrolle | Oeffentliche Drei-Knoten-Projektion |
|---|---|---|
| A0 | Zustandslosmarkierung | kompatibel |
| A1 | kein Privatstatus ausser Feld | kompatibel |
| A2 B1/B2 | externer Fixed-Adapter- beziehungsweise L-Zustand | kompatibel |
| A2 B3-B6 | eingebettetes rollenprivates M im vollstaendigen Feldobjekt | nach Ausblendung des privaten M kompatibel |
| A3-NORM | lokaler Drei-Orte-Zustand | kompatibel |
| M1 | zwei lokale Drei-Orte-Spuren | kompatibel |
| M2 DELAY/REPLAY | leerer Drei-Orte-Evidencepuffer | kompatibel |
| M4 | externe DTS-1-Anatomie | kompatibel |
| M5 | lokaler Drei-Orte-Retentionszustand | kompatibel |

B3 bis B6 zeigen, warum S1-QZ zwischen oeffentlicher Feldprojektion und
rollenprivatem eingebettetem Payload trennt. Ihre S1-JZ-Frischfelder besitzen
ein M-Substrat, waehrend B1/B2 keines besitzen. S, H, Perzeption, Docks,
Geometrie und Feldzeit koennen dennoch oeffentlich gleich sein.

Der Audit bestaetigt nur strukturelle Kompatibilitaet. Eine gemeinsame
Frischfabrik fuer alle 14 Rollen ist weiterhin nicht implementiert.

## Auswirkung auf A2 und M4

S1-RB hatte A2 unter der Bedingung einer vorhandenen S1-JV-Geometrie als
prinzipiell brueckbar klassifiziert. S1-RD zeigt nun, dass keine der beiden
vorhandenen S1-JV-Geometrien den S1-PZ-A/B/C-Vergleich traegt:

- zwei Knoten reichen fuer drei Rollen nicht aus;
- drei offene Knoten erfuellen die Kontrollsymmetrie nicht.

Damit gilt fuer die aktuelle Mappingmenge:

```text
A2_NOT_CONNECTABLE_TO_S1RA_WITH_CURRENT_S1JV_GEOMETRIES
```

Der M4-Kern kann allgemeinere Feldgeometrien technisch lesen, darf aber nicht
allein auf einer anderen Geometrie als die uebrigen Baselines laufen. Auch
M4 bleibt deshalb fuer die gemeinsame Matrix gesperrt.

Eine neue Geometrie waere keine reine S1-QZ-Formbruecke fuer A2. Sie
erfordert vor einer Implementierung einen neuen endlichen Geometrie-,
Mapping-, Fixed-Adapter- und Frischzustandsvertrag. S1-RD autorisiert das
nicht.

## Paketstatus

Die oeffentliche Frischprojektion ist nicht der Blocker. Die raeumliche
Kontrollgeometrie ist unzureichend:

```text
PUBLIC_FRESH_PROJECTION_COMPATIBLE
S1PZ_LOCAL_REMOTE_GEOMETRY_INVALID
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Ein fehlender gueltiger C-Ort erzeugt kein positives lokales Residuum. Ohne
geometrisch angepasste entfernte Kontrolle koennten spaetere Unterschiede
nicht sauber zwischen lokaler Konkurrenz und Rand-/Gradwirkung getrennt
werden.

## Fail-Closed-Regeln

S1-RD wird verletzt, wenn spaeter:

- der mittlere und ein aeusserer Knoten trotz unterschiedlicher
  Nachbarschaft als geometrisch angepasst gelten;
- ein direkt an A liegender Ort als `C_REMOTE` bezeichnet wird;
- gleiche Kontaktwerte als Ersatz fuer geometrische Anpassung gelten;
- Align, Normierung oder Gewichtung eine fehlende Kontrollsymmetrie
  reparieren soll;
- historische P_IK-/P_IN-Grenzen als S1-PZ-C-Geschichte erscheinen;
- private B3-B6-M-Payloads in die oeffentliche Frischprojektion gelangen;
- unterschiedliche oeffentliche Frischfelder zwischen Modellrollen
  akzeptiert werden;
- eine neue A2-Geometriemappingzeile ohne eigenen Vertrag entsteht;
- die 224-Zellen-Matrix auf der Drei-Knoten-Offenlinie ausgefuehrt wird.

## Aussagegrenze

S1-RD ist ein statischer Geometrie- und Anschlussaudit. Er verwirft nicht den
MCM-Wahrnehmungsfeldkern und bewertet keine Baselinefunktion. Es gibt keine
neue Geometrie, Implementierung, Ausfuehrung oder Aussage zu einer
hypothetischen MCM-Memory. Alle geschlossenen Zweige bleiben unveraendert.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RE - statischer Minimalgeometrieklassen- und A2/M4-Mappingfolgenaudit
        fuer lokale B- und geometrisch angepasste entfernte C-Kontrollen
```

S1-RE soll ohne Geometrieregistrierung die kleinsten vorhandenen
Feldtopologieklassen vergleichen, die gleichzeitig A-B-Nachbarschaft,
A-C-Nichtnachbarschaft, geometrische B/C-Gleichheit, getrennte Carrier und
eine zusammenhaengende endliche Geometrie bereitstellen koennen. Es muss die
Folgen fuer A2-B1-B6-Mapping, Fixed-Adapter-Payload, private Frischzustaende
und M4-Anatomie benennen und genau eine minimale Klasse vorschlagen. Wenn
keine Klasse ohne neue Baselinefunktion bleibt, ist die Matrix zu pausieren.
Keine konkrete Geometrie-ID, Knotenanzahl, Parameter, Mappingzeile,
Implementierung, Fixture, Testausfuehrung oder Feldlauf.

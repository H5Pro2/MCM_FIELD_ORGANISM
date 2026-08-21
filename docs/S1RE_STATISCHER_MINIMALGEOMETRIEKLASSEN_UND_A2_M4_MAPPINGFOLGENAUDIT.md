# S1-RE: Statischer Minimalgeometrieklassen- und A2/M4-Mappingfolgenaudit

## Status und Umfang

S1-RE vergleicht ausschliesslich endliche ungerichtete Feldtopologieklassen,
die den S1-PZ-Vergleich zwischen `A_FOCAL`, `B_LOCAL` und `C_REMOTE` fair
tragen koennen. Der Audit bindet noch keine konkrete Geometrieidentitaet,
keine Knotennamen, keine Rezeptorwerte und keine Parameter.

Es wird keine Geometrie registriert, kein Code implementiert, kein Test und
kein Feldlauf ausgefuehrt und keine Ergebnisentscheidung getroffen.

Auditentscheidung:

```text
FOUR_NODE_OPEN_LINE_IS_THE_MINIMAL_ADMISSIBLE_TOPOLOGY_CLASS
ABSTRACT_ROLE_ORDER_IS_B_LOCAL_A_FOCAL_D_CONTROL_C_REMOTE
B_AND_C_ARE_MATCHED_OPEN_BOUNDARY_ENDPOINTS
A_B_DISTANCE_IS_ONE_AND_A_C_DISTANCE_IS_TWO
EXISTING_FIELD_SAMPLING_PRIMITIVES_CAN_REPRESENT_THE_CLASS
A2_REQUIRES_NEW_FOUR_NODE_IDENTITY_MAPPING_AND_PRIVATE_STATE_SHAPES
B1_REQUIRES_AN_EXPLICIT_FOUR_NODE_FIXED_ADAPTER_EDGE_PAYLOAD_CONTRACT
M4_REQUIRES_A_REFLECTION_SYMMETRIC_FOUR_NODE_FRESH_ANATOMY
NO_BASELINE_EQUATION_OR_CONFIGURATION_CHANGE_IS_JUSTIFIED
MANDATORY_BASELINE_PACKAGE_REMAINS_NOT_EXECUTABLE
NO_REGISTRATION_NO_IMPLEMENTATION_NO_EXECUTION_NO_RESULT_DECISION
```

## Verbindliche Auswahlkriterien

Eine Topologieklasse ist nur zulaessig, wenn gemeinsam gilt:

1. sie ist endlich, zusammenhaengend und verwendet die bestehende
   symmetrische lokale Feldabtastung;
2. A und B sind direkt benachbart;
3. A und C sind nicht direkt benachbart;
4. B und C besitzen vor jeder Exposition dieselbe geometrische Rolle;
5. B und C koennen ueber getrennte Carrier dieselbe exogene Form, Last und
   Zeitstruktur erhalten;
6. die Klasse fuegt keine neue Feldregel oder Baselinefunktion ein;
7. alle Modellrollen koennen dieselbe oeffentliche Frischgeometrie sehen;
8. private Frischzustaende bleiben rollengetrennt und respektieren die
   geometrische B/C-Symmetrie.

Geometrische Anpassung bedeutet nicht, dass B und C nach einer A-Exposition
dieselben Feldwerte liefern muessen. Sie bedeutet, dass ihre unbehandelten
Ortsrollen durch eine Spiegelung der Topologie ineinander uebergehen. Die
gezielte A-Nachbarschaft darf diese Symmetrie spaeter kausal brechen.

## Untere Schranke

Weniger als drei Knoten koennen A, B und C nicht als verschiedene Orte
bereitstellen.

Bei drei Knoten gibt es fuer eine zusammenhaengende einfache ungerichtete
Topologie nur zwei relevante Klassen:

- Die offene Drei-Knoten-Linie scheitert nach S1-RD: Bei lokalem B und
  entferntem C besitzen B und C verschiedene Grad- und Randrollen.
- Im Drei-Knoten-Dreieck ist jeder Ort direkt mit jedem anderen verbunden;
  C kann deshalb nicht entfernt von A sein.

Damit sind mindestens vier Knoten erforderlich.

## Ausgewaehlte minimale Klasse

Die offene Vier-Knoten-Linie wird abstrakt so belegt:

```text
B_LOCAL -- A_FOCAL -- D_CONTROL -- C_REMOTE
```

`D_CONTROL` ist ein technischer Stuetz- und Kontrollort. Er erweitert nicht
die drei S1-PZ-Expositionsrollen und ist kein Modelllabel. Seine spaetere
Rezeptorbelegung muss oeffentlich im Expositionsplan gebunden werden und
darf keine private Korrektur tragen.

Die Klasse besitzt folgende rein strukturelle Eigenschaften:

| Eigenschaft | A | B | C | D |
|---|---:|---:|---:|---:|
| Grad | 2 | 1 | 1 | 2 |
| offene Randrolle | nein | ja | ja | nein |
| Distanz zu A | 0 | 1 | 2 | 1 |
| direkt mit A verbunden | - | ja | nein | ja |

Die Spiegelung der Linie tauscht B mit C und A mit D. B und C sind damit
vor der Exposition geometrisch gleichartige Endpunkte. Die spaetere
Unterscheidung entsteht ausschliesslich dadurch, dass A die fokale
Geschichte traegt und D deren oeffentlich gebundene Kontrollgegenlage.

Die Linie ist auch kantenminimal. Jede zusammenhaengende Vier-Knoten-
Topologie benoetigt mindestens drei Kanten. Unter den beiden ungerichteten
Vier-Knoten-Baumklassen erfuellt die Sternklasse die Rollenpflicht nicht;
die offene Linie erfuellt sie.

## Abgelehnte oder nachrangige Klassen

### Vier-Knoten-Stern

Liegt A im Zentrum, sind alle Blaetter direkt lokal. Liegt A auf einem
Blatt, ist nur das Zentrum direkt lokal, waehrend entfernte Blaetter eine
andere Gradrolle besitzen. Die Klasse scheitert.

### Vier-Knoten-Zyklus

Ein Zyklus kann einen direkten B-Ort und einen gegenueberliegenden C-Ort
bereitstellen. Er ist jedoch nicht minimal in der Kantenanzahl, fuegt eine
zusaetzliche Kopplungsstrecke ein und benoetigt entweder Periodizitaet oder
eine zweidimensionale Einbettung. Er bleibt theoretisch zulaessig, ist aber
fuer den ersten kontrollierten Vergleich nachrangig.

### Dichtere Vier-Knoten-Klassen

Zusaetzliche Kanten sind fuer die Rollenpflicht nicht erforderlich. Sie
koennen C wieder direkt mit A verbinden oder weitere Ausbreitungswege als
Kontrollvariable einfuehren. Ohne eigene Notwendigkeit werden sie nicht
ausgewaehlt.

## Anschluss an den Feldkern

Der vorhandene `MCMNeuronLayer` kann eine eindimensionale offene Linie mit
symmetrischen Offsets und ohne periodische Achse darstellen. Der
Kanteninventarhelper leitet daraus jede lokale Kante genau einmal ab.

Die ausgewaehlte Klasse benoetigt daher keine neue Samplingregel, keine neue
Randgleichung und keine neue Feldmechanik. Erforderlich ist spaeter nur eine
neue endliche Identitaets- und Digestregistrierung mit vier Knoten, drei
Kanten, vier getrennten Carriern und einem vollstaendigen Nullkontaktframe.

S1-RE nimmt diese Registrierung nicht vor.

## Oeffentliche Frischprojektion

Alle 14 Modellrollen muessen spaeter dieselbe oeffentliche Vier-Knoten-
Projektion tragen:

- dieselbe Feld-, Layer-, Geometrie- und Dockidentitaet;
- dieselbe kanonische Knoten- und Carrierordnung;
- dieselben symmetrischen Sampleoffsets und dieselbe offene Randform;
- S, H und Rezeptorkontakt auf positivem Nullwert;
- keine lokalen Samples und keine letzte Verteilung;
- denselben initialen Feldtakt.

Die B/C-Symmetrie ist nur dann erhalten, wenn auch jeder rollenprivate
Frischzustand unter der Linienspiegelung B/C und A/D strukturgleich bleibt.
Das bindet noch keine Zahlenwerte.

## A2-Mappingfolgen

### Gemeinsame Mappinggrenze

Der heutige A2-Adapter waehlt ausschliesslich die registrierten Zwei- und
Drei-Knoten-Zeilen aus S1-JV. Die Vier-Knoten-Linie kann deshalb nicht durch
eine aeussere Formhuelle angeschlossen werden.

Vor jeder Implementierung werden mindestens benoetigt:

- eine neue endliche Feld-, Layer-, Geometrie-, Dock- und Carrieridentitaet;
- ein kanonischer Vier-Knoten-Bestand und ein Drei-Kanten-Digest;
- eine explizite Vier-Knoten-Mappingzeile;
- eine oeffentliche Frischprojektion und rollenprivate Frischformen;
- eine neue Fehlerpruefung, die unbekannte Knotenzahlen nicht auf eine
  vorhandene Geometrie fallen laesst.

### B1 Fixed Adapter

Der aktuelle B1-Pfad unterscheidet im Code nur zwischen zwei Knoten und dem
sonst angenommenen Drei-Knoten-Payload. Eine Vier-Knoten-Eingabe wuerde
dadurch faelschlich den Drei-Knoten-Kantensatz erwarten.

B1 ist daher nicht allein durch eine Mappingzeile erweiterbar. Ein eigener
statischer Vier-Knoten-Payloadvertrag muss spaeter alle drei Linienkanten,
ihren Inventardigest und die bestehende feste Ableitungsregel exakt binden.
Dabei darf weder eine neue Rate gewaehlt noch die Fixed-Adapter-Funktion
veraendert werden.

### B2 Integrator

Der B2-Kern arbeitet ueber die vollstaendige kanonische Knotenfolge und kann
strukturell vier Orte tragen. Sein privater L-Frischzustand und jeder
Folgezustand benoetigen jedoch genau vier geordnete Eintraege. Historische
Zwei- oder Drei-Knoten-Payloads sind nicht wiederverwendbar.

### B3 bis B6

Die F3-basierten Kerne lesen den vollstaendigen Feld- und M-Bestand und sind
nicht auf drei Knoten festgelegt. Fuer die neue Klasse werden trotzdem neue
rollenprivate Vier-Knoten-M-Zustaende mit passendem Drei-Kanten-Digest
benoetigt.

Die bestehenden Modellkonfigurationen, Gleichungen und Refinementrollen
bleiben unveraendert. Eine Geometrieerweiterung rechtfertigt kein Retuning.

## M4-Mappingfolgen

Der M4-DTS-1-Kern verarbeitet die Knoten- und Kanteninventare des
vollstaendigen Feldes und bleibt strukturell auf der Vier-Knoten-Linie
anwendbar. Er benoetigt jedoch eine neue vollstaendige Frischanatomie fuer:

- vier freie Knotenkapazitaetsrollen;
- drei leitend gebundene Kantenrollen;
- drei refraktaere Kantenrollen;
- den neuen Drei-Kanten-Inventardigest;
- eine globale Erhaltungsbilanz ohne kantweise Verdopplung freier
  Knotenkapazitaet.

Nach S1-RC bleibt T1 eine eingefrorene Ein-Kanten-Gegenbaseline und wird
nicht als eigener Mehrkanten-Laufzustand projiziert. Die M4-Anatomie muss
weiterhin ihre eigenen knotennahen Halbanteilsledger und die globale Bilanz
verwenden.

Vor Exposition muss die private M4-Anatomie unter der Spiegelung der Linie
strukturgleich sein. Konkrete Kapazitaeten, Raten, Parameter und
Initialmengen werden in S1-RE nicht gebunden.

## Folgen fuer das Gesamtpaket

Die Topologieluecke aus S1-RD ist auf Klassenebene geschlossen. Die
Vier-Knoten-Linie ist aber noch nicht registriert und keine der 224
Lebenszykluszellen ist ausfuehrbar.

Insbesondere gilt:

```text
GEOMETRY_CLASS_SELECTED
GEOMETRY_IDENTITY_NOT_REGISTERED
A2_FOUR_NODE_PAYLOADS_NOT_BOUND
M4_FOUR_NODE_FRESH_ANATOMY_NOT_BOUND
COMMON_FRESH_FACTORY_NOT_IMPLEMENTED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

Dieser Befund ist keine Funktions- oder Ergebnisentscheidung und keine
Aussage zu einer hypothetischen MCM-Memory.

## Fail-Closed-Regeln

S1-RE wird verletzt, wenn spaeter:

- die Rolle D als vierte Expositions- oder Modellrolle erscheint;
- B und C verschiedene Rand-, Grad- oder private Frischrollen erhalten;
- C direkt mit A verbunden wird;
- D eine versteckte Korrektur oder ein modellabhaengiges Eingangssignal
  erhaelt;
- eine periodische oder dichtere Geometrie ohne neuen Audit die offene Linie
  ersetzt;
- der B1-Code eine unbekannte Knotenzahl weiterhin als Drei-Knoten-Fall
  behandelt;
- alte Zwei-/Drei-Knoten-Payloads auf vier Knoten aufgefuellt werden;
- A2- oder M4-Konfigurationen wegen der Geometrie neu abgestimmt werden;
- T1 als mehrfacher Kantenlaufzustand in M4 kopiert wird;
- vor vollstaendiger Registrierung ein Test oder Feldlauf beginnt.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RF - statischer Vier-Knoten-Offenlinien-Identitaets-, Rollen-, Dock-,
        Frischzustands- und A2/M4-Erweiterungspflichtenvertrag
```

S1-RF darf konkrete kanonische Identitaetsrollen und erforderliche
Payloadfelder binden. Er muss die Spiegelungsinvariante, D-Kontrollgrenze,
vier Carrier, drei Kanten, A2-B1-B6-Privatformen und die M4-Anatomieform
fail-closed festlegen. Keine Gleichung, kein Zahlenparameter, keine
Implementierung, kein Fixturebau, kein Test und kein Feldlauf.

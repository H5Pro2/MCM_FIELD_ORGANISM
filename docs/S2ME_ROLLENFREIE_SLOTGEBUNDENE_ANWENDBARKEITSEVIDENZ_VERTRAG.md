# S2-ME: Rollenfreie slotgebundene Anwendbarkeitsevidenz

## Status und Zweck

`S2ME_STATIC_LEARNING_AND_FALSIFICATION_CONTRACT_BOUND`

S2-ME untersucht genau eine neue Lernregel: Ein visueller `B_STABLE`-Slot
bindet neben seinem bestehenden adaptiven PPB-Prototyp eine endliche Evidenz
darueber, in welchem maskenkonditionierten Formbereich die ihm tatsaechlich
zugeordneten vollstaendigen Wahrnehmungen lagen.

Die Regel ersetzt die externe S2-LZ-Modellhuelle aus S2-MC nicht nachtraeglich.
Sie gilt ausschliesslich prospektiv fuer neue Formationen und neue Laeufe.
S2-MC bleibt ein gueltiger kalibrierter Versuch; S2-MD bleibt bis zu einem
positiven S2-ME-Befund blockiert.

Dieser Schritt bindet nur Funktion, Datenfluss, Falsifikation und Ressourcen.
Er implementiert und startet nichts.

## Unveraenderte Systemgrenzen

Unveraendert bleiben:

- die kanonische RGB-/PCM-Grenze und die bestehenden Rezeptoren;
- das Default-Live-Profil mit `48 + 288` Werten;
- B4 und Fast als interne Rollen von `A_RECENT`;
- die auditive und visuelle PPB-1-Bank als `B_STABLE`;
- Kapazitaeten, Matchschwellen, Aktualisierungsraten und Stabilitaetsgrenzen;
- der vorhandene posebereinigte Formdeskriptor;
- die zwei gebundenen 96er-Masken und ihre konfliktfreie 192er-Vereinigung;
- die Trennung von Feld, Memory und read-only Kontext;
- die Enthaltung bei null oder mehreren anwendbaren Kandidaten.

Es entsteht keine dritte Memory-Ebene. Die neue Evidenz ist privater,
slotgebundener Metazustand der visuellen Slow-Bank. Sie darf weder als eigener
oeffentlicher Memorybereich noch als unabhaengige Kandidatenautoritaet
projiziert werden.

MD-B02 zur fortlaufenden Zeit und MD-B03 zum Zwei-Blick-Routing bleiben
ausdruecklich ausserhalb von S2-ME.

## Rollenfreie Eingangsgrenze

An der Lernregel liegt pro vollstaendiger Formation ausschliesslich vor:

- der validierte visuelle 288-Werte-Rezeptorzustand;
- dessen Quellen-, Geometrie-, Zeit- und Konfigurationsbindung;
- der bestehende atomare Memory-Prestate;
- der reale visuelle PPB-Uebergang mit ausgewaehlter Slot-ID;
- der aus demselben Rezeptorzustand deterministisch gebildete
  maskenkonditionierte 192er-Formdeskriptor.

Nicht zulaessig sind Familien-, Modell-, Holdout-, Ziel-, Soll- oder
Auswertungsrollen. Insbesondere existieren im Laufpfad weder `model-01` noch
eine vergleichbare Ersatzkennung.

Der Formdeskriptor wird vor dem Memoryfortschritt aus dem vollstaendigen
Rezeptorzustand erzeugt, verwendet aber exakt die fuer spaetere zwei Blicke
gebundenen 192 Raster-/Kanalpositionen. Dadurch besitzen Formationsevidenz und
spaetere Blickvereinigung dieselbe 144-dimensionale Deskriptorform, ohne
verdeckte Werte aus dem spaeteren Teilhinweis zu rekonstruieren.

## Private Datenformen

### `AssignedFormEvidenceV1`

Jeder Evidenzeintrag bindet unveraenderlich:

- `slot_id`;
- `slot_generation_digest`;
- `ppb_accepted_step`;
- `ppb_transition` aus `CREATED`, `MATCHED` oder `REPLACED`;
- `formation_receipt_digest` und visuellen PPB-Inputdigest;
- visuellen Rezeptorwertedigest;
- Quellenclock und vollstaendiges Quellzeitfenster;
- Profil-, Geometrie-, Masken- und Deskriptorschemadigest;
- genau 144 Formdeskriptorwerte und deren Digest;
- den Digest des vorherigen Eintrags derselben Slotgeneration oder
  `ABSENT_VALID` fuer deren ersten Eintrag;
- den eigenen kanonischen Eintragsdigest.

Die Werte stammen ausschliesslich aus der zugehoerigen vollstaendigen
Formation. Rohpixel, PCM, Posewerte und fachliche Rollen werden nicht
gespeichert.

### `SlotApplicabilityEvidenceV1`

Pro visuellem PPB-Slot existiert innerhalb desselben privaten
Memoryzustands genau eine Evidenzrolle mit:

- Slot-ID und Slotgenerationsdigest;
- aktuellem Slot-, Prototyp- und Supportdigest;
- null bis vier geordneten `AssignedFormEvidenceV1`-Eintraegen;
- erstem und letztem gebundenen PPB-Schritt;
- Anzahl aller Formationen dieser Slotgeneration;
- Evidenzstatus;
- kanonischem Evidenzdigest.

Die hoechstens vier Eintraege sind die vier zeitlich juengsten vollstaendigen
Formationen, die der reale PPB-Uebergang dieser Slotgeneration zugeordnet hat.
Bei einem fuenften und jedem spaeteren `MATCHED`-Uebergang wird der aelteste
Eintrag entfernt und der neue angehaengt. Die Gesamtanzahl bleibt separat
gebunden, ohne fruehere Deskriptorwerte aufzubewahren.

### `LearnedSlotEnvelopeV1`

Die Huelle ist eine reine read-only Projektion aus genau einem gueltigen
`SlotApplicabilityEvidenceV1`. Sie enthaelt:

- Slot-ID, Slotgenerations-, Slot- und Evidenzdigest;
- Evidenzanzahl;
- ein 144-dimensionales Zentroid;
- den Zentroiddigest;
- genau einen nichtnegativen Radius;
- die geordneten Trainingsabstaende;
- den Huelle-Digest.

Die Huelle ist kein persistenter zweiter Wertespeicher. Zentroid, Abstaende
und Radius werden bei der Projektion aus den gebundenen Eintraegen erneut
berechnet und gegen ihre Digests geprueft.

## Atomare Fortschreibung

Die bestehende PPB-Funktion bleibt unveraendert und liefert aus immutablem
Prestate einen vorgeschlagenen Poststate. Ein privater S2-ME-Koordinator
bildet daraus zusammen mit der vorgeschlagenen Evidenzfortschreibung genau
einen neuen visuellen Slow-Gesamtzustand.

Es gelten folgende Uebergaenge:

| PPB-Uebergang | Evidenzuebergang |
| --- | --- |
| `CREATED` | neue Slotgeneration, vorherige Evidenz leer, aktueller Deskriptor erster Eintrag |
| `MATCHED` | aktuelle Generation validieren, aktuellen Deskriptor an FIFO mit Kapazitaet vier anhaengen |
| `REPLACED` | alte Generation samt aller Evidenz loeschen, neue Generation mit aktuellem Deskriptor beginnen |

Fehlt eine notwendige Bindung oder scheitert die Evidenzbildung, wird weder
der vorgeschlagene PPB-Poststate noch ein Evidenzteil veroeffentlicht. Die
Atomaritaet betrifft ausschliesslich visuellen PPB-Slot und dessen direkt
zugeordnete Evidenz. B4, Fast, auditive PPB-Bank und Feld erhalten keine neue
Kopplung.

Ein read-only Teilblick erzeugt niemals einen Evidenzeintrag. Er darf weder
FIFO, Zentroid noch Radius erweitern, ersetzen oder korrigieren.

## Homogenitaet und Fail-Closed-Regeln

Eine Slotgeneration ist nur homogen, wenn fuer jeden gespeicherten Eintrag
gleich sind:

- Slot-ID und Slotgenerationsdigest;
- Profil-, Geometrie-, Masken- und Deskriptorschema;
- Dimension und kanonische Positionen;
- Quellenclock des fortlaufenden Wahrnehmungsstroms;
- die durch PPB-Beleg und Formation nachgewiesene Slotzuordnung.

PPB-Schritte und Quellfenster muessen strikt fortschreiten. Unterschiedliche
Quellpayloads und unterschiedliche Formwerte sind ausdruecklich zulaessig;
sie bilden die zu lernende Variation.

Fehlende, doppelte, vertauschte, fremde oder nachtraeglich rekonstruierte
Eintraege sowie eine unterbrochene Slotgeneration stoppen fail-closed. Ein
stabiler Slot ohne vollstaendige prospektive Evidenz darf nicht mit
`ABSENT_VALID` gleichgesetzt werden. Er ergibt
`ABSTAINED_APPLICABILITY_EVIDENCE_UNAVAILABLE` und keine Teilhuelle.

Historische PPB-Slots erhalten keine rueckwirkend erzeugte Evidenz.

## Deterministische Huelle

Eine Huelle ist nur auswertbar, wenn:

- der PPB-Slot belegt und nach der unveraenderten Konfiguration stabil ist;
- mindestens `stable_after` gueltige Eintraege derselben Generation vorliegen;
- hoechstens vier Eintraege vorhanden sind;
- alle Integritaets- und Homogenitaetsbindungen bestehen.

Fuer `n` Eintraege `x_1 ... x_n` mit je 144 Werten gilt komponentenweise in
fest gebundener Binary64-Reihenfolge:

```text
centroid[j] = fsum(x_i[j] fuer i = 1...n) / n
distance[i] = fsum(abs(x_i[j] - centroid[j]) fuer j = 0...143) / 144
radius      = max(distance[1...n])
```

Es gibt keinen Zuschlag, kein Epsilon, keine Rundung, keine Quantisierung und
keine nachtraegliche Erweiterung. Die geordnete Eintragskette wird gedigestet;
eine Umordnung ist daher trotz mathematisch gleichem Zentroid unzulaessig.

Ein spaeteres Zwei-Blick-Formsignal ist fuer den Slot genau dann anwendbar,
wenn sein nach denselben Regeln gebildeter 144-Werte-Deskriptor einen
`mean_L1`-Abstand `<= radius` zum Zentroid besitzt.

Werden null Slot-Huellen getroffen, wird enthalten. Werden mehrere
Slot-Huellen getroffen, wird ebenfalls enthalten. Eine Rangfolge nach Abstand
ist verboten.

## Prospektiver Korpus

Vor jedem Rezeptor- oder Memoryaufruf muss genau ein neuer kleiner
`PresealedSlotApplicabilityCorpusPlanV1` kanonisch versiegelt werden.

Der Plan bindet mindestens:

- zwei unabhaengig erzeugte visuelle Wahrnehmungsfamilien;
- je vier vollstaendige Trainingsvarianten;
- je zwei vollstaendig zurueckgehaltene bekannte Varianten;
- mindestens vier unbekannte Formen;
- mindestens zwei mehrdeutige Zwischenformen;
- neun unabhaengige Druckereignisse zur spaeteren Entfernung aus B4 und Fast;
- fuer jeden Prueffall zwei feste, zeitlich geordnete 96er-Blicke;
- Generatorversion, Seeds, Transformationsparameter und kanonische
  Quellpayload-Digests;
- einen unveraenderlichen Train-/Holdout-Split;
- eine neutrale Ereignisreihenfolge ohne fachliche Rollen.

Korpusgenerator und Versiegelung duerfen Rezeptoren, Memoryschwellen,
Deskriptorabstaende und erwartete Entscheidungen nicht importieren oder
abfragen. Nach der Versiegelung darf keine Quelle ersetzt, neu erzeugt,
ausgeschlossen oder an gemessene Abstaende angepasst werden.

Familien-, Bekanntheits-, Unbekanntheits- und Mehrdeutigkeitsrollen existieren
nur in einer getrennten Evaluationswurzel. Diese wird erst nach vollstaendiger
Laufaufzeichnung an den Ausfuehrungsbeleg gebunden.

## Funktions- und Falsifikationsmatrix

Der spaetere Einmallauf muss mindestens folgende Beobachtungen getrennt
ausweisen:

| Klasse im nachgelagerten Auswerter | Zulaessiger Laufbefund |
| --- | --- |
| zurueckgehaltene bekannte Variante | genau eine gelernte Slot-Huelle oder konservative Enthaltung |
| unbekannte Form | Enthaltung erwartet; jede Zulassung ist Fehlzulassung |
| mehrdeutige Zwischenform | Enthaltung erwartet; jede Zulassung ist Fehlzulassung |
| unvereinbares Blickpaar | Enthaltung vor jeder Huelle |
| fehlende/uneinheitliche Evidenz | fail-closed ohne Kandidatenprojektion |
| ersetzter Slot | ausschliesslich Evidenz der neuen Slotgeneration sichtbar |

Ein positiver S2-ME-Befund verlangt gemeinsam:

- mindestens eine nie trainierte bekannte Variante wird durch genau eine aus
  realer Slotgeschichte gelernte Huelle zugelassen;
- unbekannte und mehrdeutige Formen werden nicht zugelassen;
- kein Teilblick veraendert Memory oder Evidenz;
- nach Slotersetzung ist kein Digest und kein Deskriptor der alten Generation
  erreichbar;
- Produktionsregel und unabhaengige Direktberechnung stimmen vollstaendig
  ueberein.

Jede technisch vollstaendige Abweichung ist ein regulaerer Funktionsbefund.
Insbesondere werden konservative Enthaltungen nicht als Infrastrukturfehler
umgedeutet. Eine Fehlzulassung falsifiziert die gebundene sichere
Anwendbarkeitsregel fuer diesen Korpus.

## Baselines

Die Pflichtbaseline implementiert unabhaengig:

- dieselbe FIFO-Auswahl der letzten vier realen Zuordnungen;
- dieselbe Zentroid- und Radiusformel;
- denselben vollstaendigen Slotscan;
- dieselbe Enthaltung bei null oder mehreren Treffern.

Gemeinsame Scan-, Zentroid-, Radius- oder Entscheidungshilfen sind verboten.
Die historische externe S2-LZ-Huelle darf nur nachgelagert diagnostisch
berichtet werden. Sie ist weder Laufelternteil noch Erfolgskriterium.

## Ressourcenobergrenzen

Fuer die bestehende visuelle Kapazitaet von vier Slow-Slots gilt:

- hoechstens `4 * 4 = 16` gespeicherte Evidenzeintraege;
- genau `16 * 144 = 2.304` gespeicherte Deskriptorwerte;
- hoechstens `18.432` Byte numerischer Float64-Evidenzzustand;
- keine persistente Duplikation der `4 * 144` Zentroidwerte;
- hoechstens `4.608` Deskriptorterme fuer die Rekonstruktion aller vier
  Zentren und Radien;
- hoechstens `576` weitere Terme fuer einen vollstaendigen Vier-Slot-Scan;
- insgesamt hoechstens `5.184` Deskriptor-Rechenpositionen pro Funktionsarm
  und Teilblickpaar.

Administrative IDs, Digests, Zaehler und kanonische Huelle sind getrennt zu
budgetieren. Eine spaetere Implementierung muss vor Ausfuehrung eine konkrete
Artefaktgrenze materialisieren; Rohpixel, PCM und vollstaendige
Rezeptorobjekte duerfen darin nicht dupliziert werden.

## Digestgraph

Die einzige zulaessige Richtung lautet:

```text
Quellpayloaddigest
-> Rezeptorzustandsdigest
-> maskenkonditionierter Formdeskriptordigest
-> Formationseingangs- und PPB-Prestate-Digest
-> PPB-Uebergangsbeleg
-> zugeordneter Evidenzeintrag
-> Slotgenerationsevidenz
-> gelernte read-only Huelle
-> spaeteres Zwei-Blick-Signal
-> Slotentscheidung
-> Ergebnisbeleg
-> getrennte Evaluation
```

Kein Sollwert, Holdoutstatus, spaeterer Blick oder Auswertungsbefund darf eine
fruehere Kante beeinflussen.

## Implementierungsgrenze

S2-ME gibt noch keine Implementierung oder Ausfuehrung frei. Vor einer
Implementierung ist statisch zu bestaetigen, dass der vorab versiegelte Korpus
und jede vollstaendige Formation die benoetigten Quellen-, Masken-,
Deskriptor- und PPB-Zuordnungsbelege prospektiv liefern koennen.

Erst danach sind ein kleiner privater Slot-Evidenzadapter, eine unabhaengige
Baseline und neutrale Vertragstests zulaessig. S2-MD, fortlaufende Zeit und
allgemeines Zwei-Blick-Routing bleiben bis zu einem bestandenen realen S2-ME-
Funktionslauf gesperrt.

Die README wird nicht als Forschungsjournal erweitert.

## Gebundener Quellstand

Audit- und Vertragsbasis ist Commit:

```text
9c2934076d92e54094b2ab1cecb045575ad02dea
```

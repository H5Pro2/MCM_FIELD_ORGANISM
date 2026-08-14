# K2/F3: Implementierungs- und Falsifikationsscheiben

Stand: 2026-08-05

Status:

- statische Vorregistrierung;
- keine Codeaenderung;
- keine Ausfuehrung und kein Test;
- keine Freigabe eines AV-Forschungslaufs;
- keine Memory-, Organisations-, Topologie-, Semantik- oder KI-Behauptung.

## 1. Zweck

Der K2/F3-Weg darf nicht als ein grosser Umbau implementiert werden. Sonst
waere bei einer Abweichung nicht mehr trennbar, ob Zustandsschema,
Kantenphysik, numerische Integration oder Weltkontakt die Ursache ist.

Diese Vorregistrierung zerlegt den Weg in drei nacheinander gesperrte
Scheiben:

```text
A: Zustand + Snapshot + P0-Vertraeglichkeit
                         |
                         v
B: reine F3-Rechte-Seite + mathematische Invarianten
                         |
                         v
C: aktiver gemeinsamer S/H/M-Integrator
```

Eine spaetere Scheibe darf erst beginnen, wenn alle Eintritts- und
Abnahmekriterien der vorherigen Scheibe erfuellt sind.

## 2. Festgelegte Eigentumsgrenze von M

M wird als unveraenderliche Substratkomponente innerhalb desselben
`SharedMCMField` gefuehrt. Die Komponente enthaelt eine kanonisch nach
`neuron_id` geordnete Folge nichtnegativer M-Werte und den festen Armvertrag.

M wird nicht aufgenommen in:

- `MCMNeuron`;
- `MCMNeuronOutput`;
- `MCMFieldPerception`;
- `MCMFieldSample`;
- Rezeptorframes oder Rezeptortransformationen;
- Beobachter oder Berichte als versteckter Laufzeitzustand.

Diese Entscheidung haelt die bestehende allgemeine S/H-Transition stabil und
verhindert einen frei verwendbaren M-Musterleser. Die F3-Naturfunktion ist
der einzige spaetere Zugriff auf benachbarte M-Werte.

## 3. Gemeinsame Sperren fuer alle Scheiben

In keiner Scheibe erlaubt sind:

- Labels, Reward, Aufgabenloesung oder Bedeutungszuweisung;
- zustands- oder verlaufsabhaengige Parameterumschaltung;
- gelernte, gewichtete oder zielgerichtete Topologie;
- ein separater Verlaufsspeicher;
- Normalisierung oder Clipping von M nach einer fehlerhaften Fortentwicklung;
- ein M-Musterleser ausserhalb der festen F3-Rechte-Seite;
- Aenderungen an Browser-, Video- oder Audio-Decodern;
- Memory-, Praegungs-, Organisations- oder KI-Claims.

Software-Vertragstests der Scheiben sind spaeter technische Nachweise, keine
Forschungsevidenz fuer organismische Eigenschaften.

## 4. Scheibe A: Zustand, Snapshot und P0

### 4.1 Forschungsfrage

Kann M als vollstaendige ortsgleiche Komponente in dieselbe unveraenderliche
Feld- und Wiederaufnahmegrenze aufgenommen werden, ohne den bestehenden
S/H-Laufzeitpfad zu veraendern?

### 4.2 Kleinster spaeterer Aenderungsumfang

Vorgesehene Verantwortungen:

1. neuer reiner Substratzustandsvertrag, beispielsweise in
   `mcm_substrate_state.py`;
2. optionale, aber explizit validierte Substratkomponente im
   `SharedMCMField`;
3. Snapshot-Schema 2 mit M, Armvertrag, Gesamtmasse und Kantenidentitaet;
4. unveraenderte Lesbarkeit und Bedeutung von Snapshot-Schema 1;
5. ausdrueckliche Migration von Schema 1 nach Schema 2;
6. kanonischer S/H-Projektionsdigest;
7. P0-Routing auf die bestehenden exakten S/H-Funktionen.

Noch nicht Teil von A:

- F3-Flussberechnung;
- aktive M-Bewegung;
- numerische S/H/M-Integration;
- AV-Forschungslaeufe.

### 4.3 Konstruktionsinvarianten

Ein Schema-2-Feld ist nur gueltig, wenn:

```text
M-neuron_ids == layer.neuron_ids
M-neuron_ids sind eindeutig und kanonisch geordnet
jeder M-Wert ist endlich und >= 0
sum(M) == deklarierte Gesamtmasse innerhalb reiner Parse-Toleranz
Armparameter sind vollstaendig und unveraenderlich
Kantenidentitaet passt zur Feldgeometrie
```

Im ersten Korridor sind nur eine zusammenhaengende Nachbarschaft,
`M_total = 1` und die gleichfoermige Initialisierung `M_i = 1/N` erlaubt.

### 4.4 Vorregistrierte technische Pruefungen

Die spaetere Testaenderung muss mindestens nachweisen:

1. Bestehende Schema-1-Fixtures liefern weiterhin denselben JSON-Inhalt und
   Digest.
2. Bestehende `MCMNeuron`-, Layer- und Sample-Rollen bleiben identisch.
3. Schema 2 roundtript mit identischem vollstaendigem Digest.
4. Restore eines Schema-2-Feldes erhaelt S, H, M, Armvertrag, Kantenidentitaet
   und naechste Zeitgrenze.
5. Fehlende, unbekannte, doppelte, negative oder nichtendliche M-Werte werden
   abgelehnt.
6. Eine falsche Gesamtmasse oder Kantenidentitaet wird abgelehnt.
7. Schema 1 wird nie automatisch mit M angereichert.
8. Die ausdrueckliche Migration erzeugt genau die deklarierte
   gleichfoermige Initialreferenz.
9. P0 erzeugt fuer synchrone Schritte denselben S/H-Projektionsdigest wie der
   bestehende Pfad.
10. P0 erzeugt fuer asynchrone Punktkontakte denselben S/H-Projektionsdigest
    wie der bestehende Pfad.
11. P0-Restore erzeugt beim naechsten Kontakt denselben S/H-Zustand wie die
    ununterbrochene bestehende Laufzeit.
12. Beobachter koennen den unveraenderlichen Snapshot nicht veraendern und
    halten keine versteckte Historie im Feld.

### 4.5 Bestehende Testgrenzen, an die A spaeter anschliesst

- `tests/test_mcm_neuron.py`
- `tests/test_mcm_neuron_layer.py`
- `tests/test_receptor_distributor_and_shared_field.py`
- `tests/test_neutral_fast_afterimage.py`
- `tests/test_neutral_asynchronous_field_runtime.py`
- `tests/test_neutral_field_session.py`
- `tests/test_passive_field_resume_control.py`

Bestehende Tests werden erweitert, nicht durch eine getrennte zweite
Feldtestwelt ersetzt.

### 4.6 Abbruchkriterien A

A wird nicht freigegeben, wenn:

- ein bestehender Schema-1-Digest geaendert werden muss;
- M in allgemeine Wahrnehmungssamples gelangen muss;
- P0 einen neuen numerischen Integrator benoetigt;
- Restore Armparameter ergaenzt oder aus Zustand ableitet;
- eine Mutation oder versteckte Historie erforderlich wird;
- alte S/H-Ergebnisse nur ungefaehr statt exakt erhalten bleiben.

## 5. Scheibe B: reine F3-Rechte-Seite

### 5.1 Eintrittstor

B bleibt gesperrt, bis A vollstaendig gruen ist. Ein Schema- oder
P0-Kompatibilitaetsfehler darf nicht in B repariert werden.

### 5.2 Forschungsfrage

Kann die mathematische F3-Kantenform als reine deterministische Funktion
implementiert werden, die aus einem aktuellen S/M-Zustand genau ein C/R-Paar
bildet und ihre analytischen Invarianten numerisch nachvollziehbar erhaelt?

### 5.3 Kleinster spaeterer Aenderungsumfang

Eine neue reine Funktion erhaelt nur:

```text
kanonische ungerichtete Kanten
aktuelles S
aktuelles M
fester F3-Armvertrag
```

und gibt nur aus:

```text
C = lokale M-Mengenraten
R = daran gebundene additive S-Rueckarbeit
```

Die Funktion erhaelt keine Weltsequenz, keine Labels, keine Phase, keinen
vorherigen Bericht und keinen Zugriff auf Snapshots ausser den aktuellen
Zustandsvektoren.

### 5.4 Vorregistrierte algebraische Pruefungen

Fuer feste, kleine technische Feldzustaende muessen spaeter gelten:

1. `sum(C) = 0` bis zur vorregistrierten Gleitkommatoleranz.
2. Jede gerichtete Rate ist bei `abs(kappa) <= 1/2` nichtnegativ.
3. Bei `lambda_sm = 0` sind C und R exakt Null.
4. Bei `eta = 0` ist R exakt Null, C aber unveraendert.
5. Bei `kappa = 0` bleibt nur zustandsneutrale M-Diffusion.
6. Bei gleichfoermigem M und nichtkonstantem S entsteht fuer
   `lambda_sm > 0`, `kappa != 0` ein gerichteter M-Transport.
7. Bei konstantem S und gleichfoermigem M sind C und R Null.
8. Eine Umkehr der Kantenaufzaehlungsreihenfolge aendert C/R nicht.
9. Eine gemeinsame Permutation von Knoten, Kanten, S und M permutiert das
   Ergebnis nur entsprechend.
10. An `S_i = -1` oder `S_i = 1` ist die F3-Rueckarbeit am betreffenden Ort
    exakt Null.
11. C wird genau einmal aus demselben S/M-Zustand gebildet und fuer dM sowie
    R wiederverwendet.
12. Ungueltige Parameter, Graphen, Dimensionen und nichtendliche Werte werden
    vor der Berechnung abgelehnt.

Diese kleinen Zustandsvektoren sind mathematische Software-Fixtures und keine
kuenstlichen Bedeutungs- oder Trainingswelten.

### 5.5 Gegenimplementierungen

B muss mindestens gegen diese absichtlich getrennten Formen pruefbar sein:

- `eta = 0`: Transport ohne Rueckwirkung;
- `kappa = 0`: zustandsneutrale Diffusion;
- Vorzeichenumkehr von `kappa`;
- konstante lineare Kreuzdiffusion;
- eine verbotene getrennte M-Lesefunktion als Architektur-Negativkontrolle.

Die Negativkontrolle wird nicht in die produktive Feldlaufzeit eingebaut.

### 5.6 Abbruchkriterien B

B wird verworfen oder korrigiert, wenn:

- Erhaltung von Kantenreihenfolge oder Summationsreihenfolge abhaengt;
- Nichtnegativitaet nur durch nachtraegliches Clipping entsteht;
- R ohne denselben realisierten C-Wert berechnet wird;
- eine Welt-, Verlaufs- oder Phaseninformation benoetigt wird;
- eine zweite Nachbarschaft fuer M eingefuehrt werden muss;
- ein algebraischer Nullfall nicht exakt Null ist.

## 6. Scheibe C: aktiver S/H/M-Integrator

### 6.1 Eintrittstor

C bleibt gesperrt, bis A und B vollstaendig gruen sind. Vor C ist zusaetzlich
eine statische Auswahl des Integratorverfahrens, seiner Toleranzen und seiner
Abbruchgrenzen erforderlich.

### 6.2 Forschungsfrage

Kann die vorhandene kontinuierliche S/H-Dynamik zusammen mit C/R als ein
gemeinsames nichtlineares Anfangswertproblem zwischen unveraenderten
Rezeptor-Ereignisgrenzen integriert werden, ohne numerische Artefakte als
Feldwirkung auszugeben?

### 6.3 Kleinster spaeterer Aenderungsumfang

C darf nur ergaenzen:

1. Zusammenstellung und Zerlegung eines kanonischen Zustandsvektors
   `(S,H,M)`;
2. gemeinsame Rechte-Seite aus bestehendem `F_current`, bestehendem
   `F_afterimage` und dem in B geprueften C/R;
3. Integration zwischen bereits vorhandenen Ereignisgrenzen;
4. atomare Rueckgabe eines neuen unveraenderlichen Gesamtfeldes;
5. technische Diagnosewerte fuer Erhaltung, Randverletzung und Konvergenz.

Rezeptorereignisse bleiben unveraendert. Ein Ereignis darf direkt S, aber
nicht M veraendern. Danach darf die kontinuierliche F3-Dynamik auf das neue S
reagieren.

### 6.4 Vorregistrierte technische Pruefklassen

Vor einem AV-Forschungslauf muessen spaeter mindestens bestehen:

1. P0 bleibt weiterhin auf dem alten Exaktpfad und umgeht C vollstaendig.
2. P1 mit `eta = 0` stimmt in S/H mit der einseitigen Baseline ueberein,
   waehrend M transportiert werden kann.
3. P1 erhaelt M-Gesamtmasse innerhalb einer vorab festgelegten Toleranz.
4. Kein M-Wert wird negativ; Verletzung fuehrt zum Abbruch.
5. S und H bleiben in ihrem gueltigen Intervall; Verletzung fuehrt zum
   Abbruch statt zu verborgenem Clipping.
6. Wiederholung mit identischen Eingaben und Integratorparametern ist
   deterministisch.
7. Snapshot-Restore an einer Ereignisgrenze stimmt mit dem ununterbrochenen
   Pfad innerhalb der festgelegten numerischen Toleranz ueberein.
8. Gleichzeitige Rezeptorereignisse sind deklarationsreihenfolgeneutral.
9. Zukuenftige Ereignisse koennen einen frueheren Praefix nicht veraendern.
10. Verfeinerungen `h`, `h/2` und `h/4` zeigen eine vorregistrierte
    Konvergenzordnung oder der Lauf wird verworfen.
11. Ein Effekt, der unter Verfeinerung verschwindet oder sein Vorzeichen
    unkontrolliert wechselt, gilt als numerisches Artefakt.
12. Grob-/Fein-Segmente werden nicht auf Bitgleichheit verpflichtet; ihre
    Abweichung muss aber zur gewaehlten Methode und Toleranz passen.

### 6.5 Erste zulaessige Daten nach technischer Abnahme

Erst nach erfolgreicher technischer Abnahme von C darf eine bereits
kontrollierte, reproduzierbare AV-Rezeptorfolge verwendet werden. Der erste
Lauf darf keine neue Medienquelle einfuehren. P0, P1 und die relevanten
Ablationen erhalten exakt dieselbe Rezeptorereignisfolge.

Der erste Lauf untersucht nur:

```text
Entsteht reproduzierbarer M-Transport?
Ist die daran gebundene S-Rueckwirkung kausal von eta abhaengig?
Bleibt die Wirkung unter Zeitverfeinerung erhalten?
```

Er untersucht noch nicht Memory, Praegung, Verdichtung oder Vergessen.

### 6.6 Abbruchkriterien C

C oder ein darauf beruhender Lauf wird gestoppt, wenn:

- P0 nicht mehr exakt der alte S/H-Pfad ist;
- Masse nur durch Renormalisierung erhalten wird;
- negative M-Werte geclippt werden;
- Resultate stark von willkuerlicher Schrittteilung abhaengen;
- Restore eine andere kausale Fortsetzung erzeugt;
- ein Effekt bei `eta = 0` bestehen bleibt und dennoch als Rueckwirkung
  bezeichnet wird;
- AV-Inhalte, Labels oder Ergebniswissen Parameter bestimmen;
- aus technischer Kopplung bereits ein Memory- oder Organisationsclaim
  abgeleitet wird.

## 7. Freigabematrix

| Scheibe | Darf beginnen, wenn | Darf freigeben |
|---|---|---|
| A | diese Vorregistrierung statisch konsistent ist | nur Zustandsschema, Restore und P0-Kompatibilitaet |
| B | A vollstaendig abgenommen ist | nur reine C/R-Funktion und Invarianten |
| C | A und B abgenommen sowie Integrator vorregistriert sind | nur technische gekoppelte Laufzeit |
| AV-Kausallauf | C technisch abgenommen ist | nur Evidenz fuer oder gegen F3-Transport und Rueckwirkung |
| Memory-Forschung | wiederholte AV-Kausalevidenz mit Gegenbaselines besteht | erst dann Praegungs-/Loesungsfragen |

Keine Freigabe springt eine Zeile dieser Matrix vor.

## 8. Verwendete Projektquellen

Fachliche Vertraege:

- `docs/K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md`
- `docs/K2_F3_STATISCHE_IMPLEMENTIERUNGSSPEZIFIKATION.md`
- `docs/NULLPFAD_KORREKTURVERTRAG_GEKOPPELTE_SUBSTRATPHYSIK.md`
- `docs/KORREKTURVERTRAG_DIGITALE_NATURREKURRENZ.md`

Statisch gelesene Architektur:

- `mcm_field_organism/mcm_neuron.py`
- `mcm_field_organism/mcm_neuron_layer.py`
- `mcm_field_organism/shared_mcm_field.py`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`
- `mcm_field_organism/neutral_field_session.py`
- `mcm_field_organism/passive_field_resume_control.py`

Statisch inventarisierte bestehende Testgrenzen:

- `tests/test_mcm_neuron.py`
- `tests/test_mcm_neuron_layer.py`
- `tests/test_receptor_distributor_and_shared_field.py`
- `tests/test_neutral_fast_afterimage.py`
- `tests/test_neutral_asynchronous_field_runtime.py`
- `tests/test_neutral_field_session.py`
- `tests/test_passive_field_resume_control.py`

## 9. Ergebnis

Der F3-Umbau ist in drei kausal trennbare und einzeln falsifizierbare
Scheiben zerlegt. Der aktuelle Architekturstand erlaubt Scheibe A, ohne den
bestehenden allgemeinen Neuron-, Sample- oder S/H-Transitionsvertrag zu
erweitern. Damit bleibt der neue Weg klein und rueckpruefbar.

Noch ist keine Scheibe implementiert oder ausgefuehrt. Der anschliessende
[Integratorfamilien-Audit](K2_F3_INTEGRATORFAMILIEN_AUDIT.md) hat bedingt ein
ereignisausgerichtetes SSPRK(3,3) unter einer gemeinsamen
Forward-Euler-Invariantengrenze gewaehlt. Der naechste zulaessige Schritt ist
der exakte API-, Schema-2-, Migrations- und P0-Projektionsvertrag fuer
Scheibe A, weiterhin vor jeder Codefreigabe.

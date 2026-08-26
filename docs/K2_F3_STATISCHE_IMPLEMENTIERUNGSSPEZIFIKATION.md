# K2/F3: statische Implementierungsspezifikation

Stand: 2026-08-05

Status:

- statische Architekturspezifikation;
- keine Implementierung;
- keine Ausfuehrung und kein Test;
- keine Memory-, Organisations-, Topologie-, Semantik- oder KI-Behauptung.

Diese Spezifikation uebersetzt den
[K2-mathematischen F3-Minimalvertrag](K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md)
in einen kleinsten moeglichen Anschluss an die vorhandene Laufzeitarchitektur.
Sie gibt noch keine Codeaenderung frei.

## 1. Forschungsfrage

Kann der eine konservierte, ortsgleiche Substratzustand `M` so in die
bestehende gemeinsame MCM-Feldlaufzeit aufgenommen werden, dass

1. `S`, `H` und `M` eine einzige atomare Zustandsgrenze bilden,
2. die F3-Fluesse nur vorhandene lokale Feldnachbarschaften verwenden,
3. der K2-Nullarm den bisherigen `S/H`-Pfad exakt beibehaelt,
4. ein aktiver Arm keine externe Musterlesung oder Phasenlogik erhaelt und
5. Snapshot, Wiederaufnahme und Gegenbaselines kausal vollstaendig bleiben?

## 2. Vorgefundene Anschlussstellen

| Bestehende Stelle | Heutige Funktion | Erforderliche spaetere Erweiterung |
|---|---|---|
| `mcm_neuron.py` | lokaler Zustand `activation`, `afterimage` | bleibt unveraendert; kein allgemeiner M-Lesepfad |
| `mcm_neuron_layer.py` | atomarer Neuronenausgang und lokale S/H-Samples | bleibt fuer allgemeine S/H-Transitionen unveraendert |
| `shared_mcm_field.py` | ein gemeinsames Feld, Snapshot und Restore | ortsgleiche Substratkomponente, Snapshot-Schema fuer `M` und festen Armvertrag |
| `neutral_local_field_substrate.py` | exakte lineare `S/H`-Fortschreibung | eigener gekoppelter F3-Pfad fuer `S/H/M` |
| `neutral_asynchronous_field_runtime.py` | Ereignisgrenzen fuer AV-Rezeptorkontakte | gemeinsame Integration zwischen denselben Ereignisgrenzen |
| `neutral_field_session.py` | zusammenhaengende Fenster und Beobachter | unveraenderte aeussere Sitzungsgrenze, aber vollstaendiger F3-Snapshot |

Die bestehende Architektur besitzt bereits Feldgeometrie, lokale
Nachbarschaft, atomare Schritte, einen Organismus-Takt sowie serialisierbare
Laufzeitgrenzen. Es fehlt kein zweites Feldsystem, sondern genau eine weitere
ortsgleiche Zustandskomponente innerhalb des bestehenden gemeinsamen
Feldobjekts.

## 3. Verbindliche Zustandsentscheidung

Der spaetere F3-Zustand eines Feldortes ist:

```text
X_i = (S_i, H_i, M_i)
```

mit:

```text
-1 <= S_i <= 1
-1 <= H_i <= 1
 0 <= M_i <= M_total
sum_i M_i = M_total
```

`M_i` darf nicht in einer separaten Datenbank, einem Beobachter, einem
Analysebericht oder einem nachgelagerten Memory-Modul liegen. Sonst waere die
beabsichtigte Rueckwirkung keine innere Feld-Substrat-Dynamik.

`M_i` wird zugleich weder in `MCMNeuron` noch als neuer Rezeptor- oder
Wahrnehmungswert in `MCMFieldSample` freigegeben. Eine unveraenderliche
Substratkomponente im `SharedMCMField` ordnet jedem vorhandenen `neuron_id`
genau einen M-Wert zu. Nur die fest definierte F3-Kantenphysik darf die
aktuellen M-Werte zweier benachbarter Feldorte gemeinsam verwenden. Dadurch
entsteht kein allgemeiner M-Musterleser neben der Naturdynamik.

Fuer den ersten Implementierungskorridor wird nur eine zusammenhaengende
Feldnachbarschaft zugelassen. Die Initialreferenz ist:

```text
M_total = 1
M_i(0) = 1 / N
```

Dabei ist `N` die Zahl der Feldorte. Ein nicht zusammenhaengender Graph wird
im ersten Korridor abgelehnt und nicht durch implizite Teilfeldregeln
interpretiert.

## 4. Fester Armvertrag

Ein neuer unveraenderlicher technischer Vertrag muss mindestens enthalten:

```text
arm_id
lambda_sm_per_second
kappa
eta
initial_total_mass
```

Gueltigkeit:

```text
lambda_sm_per_second >= 0
abs(kappa) <= 1/2
eta >= 0
initial_total_mass = 1 fuer den ersten Korridor
```

Alle Werte werden vor dem ersten Schritt festgelegt. Kein Wert darf innerhalb
eines Lebenslaufs aufgrund von Zustand, Weltkontakt, Verlauf, Ergebnis oder
Beobachterausgabe umgeschaltet werden.

## 5. Eine kanonische Kantenmenge

Die F3-Kanten werden aus derselben symmetrischen Nachbarschaft gewonnen, die
bereits die lokale S-Ausbreitung traegt. Jede ungerichtete Kante `{i,j}` wird
genau einmal in kanonischer Reihenfolge inventarisiert.

Im ersten Korridor gilt:

```text
w_ij = 1 fuer jede vorhandene lokale Nachbarschaftskante
```

Nicht erlaubt sind:

- neu gelernte Kanten;
- zustandsabhaengige Kanten;
- semantische Kantenklassen;
- gerichtete Zusatzkanten;
- eine Zieltopologie;
- unterschiedliche Kantenmengen fuer S und M.

Asymmetrie, Selbstkanten, doppelte Kanten oder ein nicht zusammenhaengender
Graph sind harte Vertragsfehler.

## 6. Atomare F3-Rechte-Seite

An jedem Auswertungspunkt des aktiven kontinuierlichen Arms werden aus
demselben unveraenderten Eingabezustand `(S,H,M)` zuerst alle gerichteten
Raten und dann genau einmal `C` berechnet:

```text
q_i_to_j = lambda_sm * w_ij * M_i * (1 + kappa * (S_j - S_i))
q_j_to_i = lambda_sm * w_ij * M_j * (1 - kappa * (S_j - S_i))

C_i = sum_j(q_j_to_i - q_i_to_j)
R_i = -eta * (1 - S_i^2) * C_i / M_total
```

Danach entsteht eine einzige gemeinsame Ableitung:

```text
dS_i/dt = F_current_i(S, world_contact) + R_i
dH_i/dt = F_afterimage_i(S, H)
dM_i/dt = C_i
```

`C` darf nicht einmal fuer M und ein zweites Mal aus einem bereits
aktualisierten Zustand fuer S berechnet werden. Es gibt keine Reihenfolge
`erst M, dann S` oder `erst S, dann M`, sondern nur eine atomare
Rechte-Seite.

Die vorhandene kontinuierliche Dissipation bleibt Bestandteil von
`F_current` und `F_afterimage`. F3 darf weder Rezeptorwerte noch
Rezeptorverstaerkung, Nachbarschaft, Zeitkonstanten oder Dissipationsraten
veraendern.

## 7. Integrationsgrenze

### 7.1 Nullarm P0

Bei `lambda_sm = 0` gilt exakt:

```text
C = 0
R = 0
M(t) = M(0)
```

P0 muss deshalb den vorhandenen exakten linearen `S/H`-Integrator direkt
verwenden. Er darf nicht durch einen neuen numerischen F3-Integrator
nachgebildet werden. Damit bleibt die `S/H`-Projektion des alten Pfades
bitgleich erhalten.

Der vollstaendige neue Snapshot kann wegen des zusaetzlichen M-Zustands einen
anderen Digest besitzen. Fuer den Nullpfad ist daher zusaetzlich ein
kanonischer `S/H`-Projektionsdigest erforderlich.

### 7.2 Aktiver Arm P1

Bei `lambda_sm > 0` ist die Dynamik nichtlinear. Der bisherige spektrale
Exaktschritt fuer das lineare `S/H`-System kann nicht als Exaktschritt fuer
F3 ausgegeben werden.

P1 muss `S`, `H` und `M` gemeinsam zwischen zwei bereits vorhandenen
Rezeptor-Ereignisgrenzen integrieren. Ein punktfoermiger Rezeptorkontakt
veraendert an seiner Ereignisgrenze weiterhin nur S nach dem bestehenden
Rezeptorvertrag; M wird durch diesen externen Sprung nicht direkt geaendert.
Die anschliessende kontinuierliche Entwicklung darf unmittelbar auf den
veraenderten S-Zustand reagieren.

Der spaetere Integrator muss:

- deterministisch konfiguriert sein;
- dieselbe atomare Rechte-Seite fuer alle Komponenten verwenden;
- Zeitverfeinerung und Konvergenz pruefbar machen;
- Massenerhaltung und Nichtnegativitaet innerhalb vorregistrierter Toleranzen
  kontrollieren;
- bei Vertragsverletzung abbrechen statt M nachtraeglich zu normalisieren;
- keine Grob-/Fein-Gleichheit versprechen, die fuer eine nichtlineare
  numerische Integration mathematisch nicht begruendet ist.

Eine konkrete Integratorbibliothek und Toleranz werden in diesem Dokument
noch nicht festgelegt.

## 8. Snapshot- und Wiederaufnahmevertrag

Das bestehende Snapshot-Schema 1 bleibt ein historischer `S/H`-Vertrag und
darf nicht stillschweigend umgedeutet werden.

Ein spaeteres Schema 2 muss mindestens serialisieren:

- alle bisherigen Feld-, Geometrie-, Dock-, Zeit- und Wahrnehmungsrollen;
- die Substratmasse je Feldort als kanonisch nach `neuron_id` geordnete
  Feldkomponente;
- den festen F3-Armvertrag;
- `M_total` und die kanonische Kanteninventar-Identitaet.

Ein Schema-1-Snapshot darf nur ueber eine ausdrueckliche, separat pruefbare
Migration mit deklarierter gleichfoermiger M-Initialisierung in Schema 2
ueberfuehrt werden. Restore darf keine Parameter ergaenzen, neu waehlen oder
aus Daten ableiten.

Nach Restore muessen gelten:

```text
vollstaendiger Schema-2-Digest identisch
S/H/M-Zustand identisch
Armvertrag identisch
naechste Ereignisgrenze identisch
```

## 9. Minimaler spaeterer Aenderungsumfang

Die erste Implementierung darf nur diese Verantwortungen beruehren:

1. Substratzustandsvalidierung und kanonische Serialisierung;
2. Einbindung der Substratkomponente in das unveraenderliche gemeinsame Feld,
   ohne M in Neuronen, Transitionen oder Feldsamples aufzunehmen;
3. gemeinsamen Feld-Snapshot und Restore;
4. kanonisches Kanteninventar;
5. reine F3-Rechte-Seite;
6. P0-Routing auf den bestehenden Exaktpfad;
7. P1-Integration zwischen vorhandenen Ereignisgrenzen;
8. bestehende Session-Wiederaufnahme ohne neuen Verlaufsspeicher.

Nicht Teil dieses Umfangs sind Browser-, Video- oder Audio-Decoder,
Rezeptorreduktion, Datenbanken, Embeddings, ein Memory-Modul, ein Effektor,
eine Sprachebene oder eine neue Topologie.

## 10. Verbindliche Gegenbaselines

Jede spaetere Ausfuehrungsplanung muss mindestens getrennte Arme fuer diese
Interventionen vorsehen:

| Arm | Aenderung | Gepruefte Ursache |
|---|---|---|
| P0 | `lambda_sm = 0` | exakter alter S/H-Nullpfad |
| P1 | F3 aktiv, gleichfoermiges M | gesamte gekoppelte Naturhypothese |
| B-kappa | `kappa = 0` | S-gradientenabhaengiger M-Transport |
| B-eta | `eta = 0` | Rueckwirkung des realisierten M-Transports auf S |
| B-sign | Vorzeichen von `kappa` gespiegelt | Richtungsabhaengigkeit |
| B-linear | konstante lineare Kreuzdiffusion | Notwendigkeit der F3-Form |
| B-reader | gleicher M-Transport plus separater Musterleser | Ausschluss externer Musterablesung |
| B-swap | M-Zustaende zwischen Wiederaufnahmen getauscht | Kausalitaet des lokalen M-Zustands |

Die Arme erhalten dieselben kontrollierten AV-Rezeptorfolgen. Es werden keine
Labels, Rewards, Aufgabenloesungen oder Bedeutungszuweisungen verwendet.

## 11. Abbruchbedingungen vor jeder Behauptung

Der F3-Weg wird technisch korrigiert oder verworfen, wenn mindestens eines
der folgenden Ereignisse eintritt:

- P0 weicht in der `S/H`-Projektion vom alten Pfad ab;
- M-Masse entsteht oder verschwindet ausserhalb der vorregistrierten
  numerischen Toleranz;
- M wird negativ oder nachtraeglich normalisiert/geclippt;
- S/H/M werden nicht atomar fortgeschrieben;
- Restore veraendert Zustand, Armvertrag oder naechste Ereignisgrenze;
- eine Wirkung bleibt bei `eta = 0` unveraendert und wird trotzdem als
  Substratrueckwirkung bezeichnet;
- ein Befund benoetigt Musterleser, Labels, Phasenregeln oder Zieltopologie;
- nur ein Integrationsartefakt statt einer zeitverfeinerungsstabilen Wirkung
  vorliegt.

## 12. Ergebnis

Statisch ist ein kleiner Anschluss an die bestehende Architektur moeglich.
Der entscheidende Umbau ist kein separates Memory-System, sondern die
Aufnahme von `M` als drittem ortsgleichem Zustand in dieselbe atomare
Feldgrenze wie `S` und `H`.

Noch nicht nachgewiesen sind:

- numerische Realisierbarkeit im vorhandenen Runtimepfad;
- stabile kausale Rueckwirkung unter kontrolliertem AV-Weltkontakt;
- Praegung, Verdichtung, Vergessen oder Wiederverwendung;
- Memory, innere Organisation, Semantik, Topologie oder KI.

Die kleinsten Implementierungs- und Falsifikationsscheiben sind inzwischen
im
[Scheibenvertrag](K2_F3_IMPLEMENTIERUNGS_UND_FALSIFIKATIONSSCHEIBEN.md)
vorregistriert. Der anschliessende
[Integratorfamilien-Audit](K2_F3_INTEGRATORFAMILIEN_AUDIT.md) waehlt bedingt
SSPRK(3,3) unter einer gemeinsamen Forward-Euler-Invariantengrenze. Vor Code
bleibt der exakte API-, Schema-2-, Migrations- und P0-Projektionsvertrag von
Scheibe A auszuarbeiten.

# W7-AF: Vertrag fuer passive CAP-Messuebergabe

## Entscheidung

`PASSIVE_CAP_MEASUREMENT_HANDOFF_CONTRACT_BOUND`

W7-AF bindet statisch, wie aus den vorhandenen W7-AE-CAP-Zustaenden spaeter
rollenreine W7-O/W7-P-Messdaten entstehen duerfen. Der Vertrag misst noch
nichts, fuehrt keine Probe aus und bewertet keinen Pfad.

## 1. Festgestellte Ausfuehrungsgrenze

Die 35 vorhandenen W7-AE-Probeaeste belegen technische Fortsetzbarkeit und
Isolation. Sie sind noch keine zulaessigen W7-O-Kausalmessproben:

- ihre S/H-Anfangszustaende entsprechen dem jeweiligen Hauptcheckpoint und
  sind zwischen Pfaden nicht angeglichen;
- W7-AE bindet Anfang, Ende und Runtime-Diagnostik, aber keine passiven
  S/H/M-Zwischensamples an Rezeptorabschlussgrenzen;
- `probe_SH_trajectory_l2` und `probe_observation_ticks` lassen sich deshalb
  nicht aus den vorhandenen Endpunkten rekonstruieren;
- ein Endpunktabstand darf nicht als Trajektorienmessung umbenannt werden.

Die vorhandenen W7-AE-Proben bleiben unveraenderte technische
Kontinuitaetsproben. Sie duerfen weder nachtraeglich als Kausalmessungen
ausgegeben noch fuer W7-O-Feldvergleiche verwendet werden.

## 2. Unveraenderliche Eingangsbindung

Eine spaetere Messuebergabe bindet vor jeder Messkopie:

- W7-M-Matrix-, Regions- und Runtime-Konfigurationsdigest;
- W7-Y-Gesamtplan- und Pfadplandigests;
- W7-AA-P0-, W7-AC-Observer- und W7-AE-CAP-Gesamtverbrauchsdigests;
- genau sieben CAP-Pfade und Checkpoints 0 bis 4;
- den jeweiligen W7-AE-Hauptcheckpointzustand;
- den zugeordneten W7-Y-Probesegment- und Quelldigest;
- `C_site = 2/84`, Gesamtmasse `1.0` und das feste Kanteninventar.

Keine Bindung darf nach Sichtung eines Messwerts erneuert oder angepasst
werden.

## 3. Drei getrennte Messflaechen

### 3.1 Technische Kontinuitaet

Direkt aus W7-AE duerfen nur bereits gebundene technische Rollen gelesen
werden:

- Feld-, Produktions- und Fortsetzungsbindungsdigests;
- Segmentintervall und zugewiesene Ereignisanzahl;
- Validierungsanzahl;
- maximale lokale Masse;
- kleinste freie lokale Kapazitaet;
- maximaler Kapazitaetsueberschuss;
- Massen-, Geometrie- und Kanteninventarkontrolle.

Diese Rollen sind keine Probe-S/H-Wirkung und kein Funktionsbefund.

### 3.2 CAP-Ressourcenmessung

Auf unveraenderten W7-AE-Hauptcheckpointzustaenden darf passiv gemessen
werden:

- vollstaendiger M-Vektor nur im Arbeitsspeicher;
- `M_R` fuer die eingefrorenen W7-M-Regionen `R_A`, `R_B` und `R_0`;
- `F_R` fuer dieselben Regionen;
- Gesamtmasse, gesamte freie Kapazitaet und Bilanzrest;
- kleinstes und groesstes lokales M;
- kleinste lokale freie Kapazitaet.

`measure_w7m_regional_capacity` ist die einzige vorhandene regionale
Lesefunktion. Ihr Ergebnis darf nichts an Feld, Hauptkette oder Probe
zurueckgeben. W7-P-`W7PCapacityMeasurement` bleibt die CAP-exklusive
Gesamthuelle; regionale Werte benoetigen in W7-AG eine getrennte
digestgebundene Erweiterung und duerfen nicht in freie Textfelder ausweichen.

### 3.3 Kausale Feldmessung

W7-P-`W7PFieldMeasurement` darf fuer CAP erst nach der getrennten
Messkopienprozedur aus Abschnitt 4 erzeugt werden. Zulaessige Rollen bleiben:

- `probe_S_linf`;
- `probe_H_linf`;
- `probe_SH_trajectory_l2`;
- `probe_observation_ticks`.

Observermessungen aus W7-AC bleiben auf ihrer eigenen Messflaeche. Ihre
absoluten Werte duerfen CAP-Feld- oder Ressourcenrollen nicht ersetzen.

## 4. Getrennte Fast-State-Messkopie

Fuer jeden der 35 Hauptcheckpoints wird spaeter zusaetzlich zu der bereits
vorhandenen W7-AE-Probe genau eine Messkopie erzeugt:

1. Der vollstaendige CAP-Hauptcheckpointzustand wird tief kopiert.
2. Auf einer abgeschlossenen Kopie setzt `align_w7m_fast_state`
   ausschliesslich S und H auf den gemeinsamen Nullzustand.
3. M, Substratarm, Gesamtmasse, Kapazitaet, Geometrie, Kanteninventar,
   Pfadbindung und Checkpointtick bleiben unveraendert.
4. Fuer den geaenderten Snapshot wird durch die vorhandene W7-M-Funktion eine
   neue
   passende Fortsetzungsbindung erzeugen.
5. Nur diese angeglichene Kopie verarbeitet das unveraenderte W7-Y-
   Probesegment desselben Checkpoints.
6. Messendzustand und Samples verbleiben ausschliesslich im Messast.

Die bereits vorhandene W7-AE-Probe wird nicht ersetzt, neu gebunden oder
fortgesetzt. Messast, technische Probe und Hauptpfad sind drei getrennte
Rollen.

U/Checkpoint 0 ist die einzige Initialrolle. Dieses Feld besitzt bereits
S = H = 0, aber noch keine abgeschlossene Distribution. Seine Messkopie wird
deshalb nur tief kopiert und bleibt bindungslos. `align_w7m_fast_state` darf
dort nicht aufgerufen und es darf keine kuenstliche Bindung erzeugt werden.
Die erste Messprobe ist wie bei W7-AE ein Initialadvance.

## 5. P0-Gegenbaseline

Ein absoluter CAP/P0-Probevergleich ist nur zulaessig, wenn auch P0 mit
demselben Nullzustand fuer S und H, demselben Checkpointtick, derselben
Neuronenreihenfolge und demselben W7-Y-Probesegment startet.

Die vorhandenen W7-AA-Proben starten aus ihren jeweiligen P0-
Hauptcheckpointzustaenden und sind deshalb ebenfalls nur technische
Fortsetzungsproben. W7-AG muss fuer P0 getrennte messungsgebundene
Nullstartkopien erzeugen oder den Feldvergleich explizit als noch nicht
ausfuehrbar markieren. CAP darf nie gegen unangepasste W7-AA-Proben verglichen
werden.

P0 besitzt kein M und darf keine Ressourcenmessung erhalten.

## 6. Passive Trajektorienbeobachtung

Die vorhandene Basis-F3-Runtime besitzt bereits einen privaten passiven
`_state_observer`, der an Rezeptorabschlussgrenzen Kopien von S, H und M
liefert. Der kapazitaetsbegrenzte W7-K-Adapter reicht diesen Observer derzeit
nicht durch.

W7-AG darf den W7-K-Transientadapter ausschliesslich um eine optionale private
Observerweitergabe ergaenzen. Fuer sie gelten:

- Observerargumente sind Kopien und nicht schreibbar in die Runtime;
- Rueckgabewert muss `None` sein;
- Beobachtung veraendert weder Integration noch Validierungszaehler,
  Snapshot, Bindung oder Produktionsdigest;
- ohne Observer bleibt der vorhandene W7-AE-Pfad exakt unveraendert;
- beobachtet werden nur bereits vorhandene Abschlussgrenzen und der
  Segmentendtick;
- keine Interpolation, Nachabtastung oder nachtraegliche Tickauswahl.

Eine Implementierung muss denselben CAP-Endsnapshot mit und ohne passiven
Observer bitgleich nachweisen.

## 7. Messdefinitionen

Nach angeglichenem S/H-Nullstart gelten fuer einen Messast:

- `probe_S_linf`: groesste absolute S-Komponente ueber alle gebundenen
  Beobachtungsticks;
- `probe_H_linf`: groesste absolute H-Komponente ueber alle gebundenen
  Beobachtungsticks;
- `probe_SH_trajectory_l2`: Quadratwurzel aus der Summe der quadrierten S-
  und H-Komponenten ueber exakt dieselben Ticks und dieselbe
  Neuronenreihenfolge;
- `probe_observation_ticks`: streng steigende tatsaechliche
  Rezeptorabschlussgrenzen einschliesslich Segmentende ohne Duplikat.

Diese Definition ist eine diskrete technische Norm auf den vorhandenen
Abschlussgrenzen. Sie ist keine kontinuierliche Zeitintegralnorm und keine
Feldzeit.

## 8. Messresultat- und Digestrollen

Ein spaeteres CAP-Messcheckpointresultat bindet mindestens:

- W7-AE-CAP-Pfad- und Hauptcheckpointdigest;
- Hauptfeldsnapshot- und Hauptbindungsdigest;
- Digest der angeglichenen Messkopie und ihrer erneuerten Bindung;
- unveraenderten W7-Y-Probesegmentdigest;
- geordnete Beobachtungsticks und einen Digest der S/H/M-Samples;
- W7-P-Feldmessung;
- W7-P-Kapazitaetsmessung und regionales W7-M-Ledger vor der Probe;
- Messendfeld- und Messendbindungsdigest;
- Kennzeichen `returns_to_main = false`;
- kanonischen Messcheckpointdigest.

Der globale `cap_measurement_handoff_digest` bindet genau 35
Messcheckpointdigests in W7-Y-Pfad- und Checkpointreihenfolge sowie die
unveraenderten W7-AA-, W7-AC- und W7-AE-Gesamtdigests. Er enthaelt keine
Pfadkontraste, Rangfolge oder Entscheidung.

## 9. Rueckwirkungsgegenkontrollen

Eine spaetere Implementierung muss mindestens pruefen:

1. **Observerpassivitaet:** CAP-Endfeld und Bindung sind mit und ohne
   Trajektorienobserver bitgleich.
2. **Messreihenfolge:** kanonische und umgekehrte Messcheckpointreihenfolge
   liefern je Rolle dieselben Digests.
3. **Dreifachtrennung:** Hauptzustand, vorhandene W7-AE-Probe und neue
   Messkopie teilen keine veraenderbaren Feldteile.
4. **Fast-State-Abgleich:** alle Messkopien starten mit exakt S = H = 0,
   waehrend ihr M-Vektor dem jeweiligen Hauptcheckpoint entspricht; die drei
   U/Checkpoint-0-Kopien bleiben initial und bindungslos.
5. **Eingangspassivitaet:** W7-AA-, W7-AC- und W7-AE-Gesamtdigests bleiben
   unveraendert.

## 10. Nicht freigegebene Auswertung

W7-AF gibt insbesondere noch nicht frei:

- AB/AG/BA/BG/UA/UB/UG-Kontraste;
- dimensionslose Lebenszyklusprofile;
- Freisetzungs-, Beanspruchungs- oder Wiederverwendungsentscheidungen;
- M-Neutralisierung, M-Transplantation, ETA0, KAPPA0 oder SIGN;
- CONST-V-, F3-, LIN- oder MOB-Ausfuehrungen;
- numerische Boden- oder Fuenf-Prozent-Entscheidungen;
- Feldfunktions-, Memory- oder andere Forschungsclaims.

Diese Rollen benoetigen nach der reinen Messuebergabe einen weiteren
statischen Auswertungsvertrag.

## 11. Pflichtkontrollen

W7-AG muss mindestens pruefen:

- genau 35 getrennte CAP-Messkopien;
- vollstaendige Pfad- und Checkpointbelegung;
- S/H-Nullabgleich nur im Messast;
- unveraendertes M bei der Angleichung;
- erneuerte snapshotgenaue Fortsetzungsbindung fuer abgeschlossene Felder
  und Bindungslosigkeit nur bei U/Checkpoint 0;
- exakte W7-Y-Probe und additive Quellenautorisierung;
- streng steigende tatsaechliche Beobachtungsticks;
- korrekte Feld- und CAP-exklusive Ressourcenrollen;
- regionale Bilanzschliessung;
- alle Gegenkontrollen aus Abschnitt 9;
- deterministischen Gesamtmessuebergabedigest;
- fehlende Exporte aus Paketwurzel und `current_api`;
- keine Reports, Browserstarts oder Laufmarker.

## 12. Harte Stopplinien

Die Implementierung muss stoppen, wenn:

- eine vorhandene W7-AE-Probe als angeglichene Kausalmessprobe ausgegeben
  wird;
- S/H im Hauptpfad oder in der technischen Probe veraendert werden;
- M beim Fast-State-Abgleich veraendert wird;
- Trajektorienrollen aus Anfang und Ende geschaetzt werden;
- ein Observer Integration, Feld, Bindung oder Digest veraendert;
- P0 eine M- oder Kapazitaetsrolle erhaelt;
- Observerwerte als CAP-Feld- oder Ressourcenwirkung erscheinen;
- Messwerte bereits verglichen, gerankt oder interpretiert werden;
- ein Report oder Forschungslauf erzeugt wird.

## 13. Aussagegrenze

W7-AF ist nur ein statischer Messuebergabevertrag und korrigiert keine
bestehenden Ergebnisse. Es wurde keine Messkopie erzeugt und kein Sample
erfasst. Daraus folgen keine Feldfunktion, kein Memory, keine Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## 14. Verwendete Quellen

- `docs/W7L_VORREGISTRIERUNG_KAPAZITAETSFUNKTION_UND_GEGENBASELINES.md`
- `docs/W7M_IMPLEMENTIERUNG_IN_MEMORY_KAPAZITAETSFUNKTIONSMATRIX_ADAPTER.md`
- `docs/W7O_MESSVERTRAG_FELDKAUSALITAET_UND_OBSERVERBASELINES.md`
- `docs/W7P_IMPLEMENTIERUNG_IN_MEMORY_MESSKOMPOSITOR.md`
- `docs/W7AE_IMPLEMENTIERUNG_CAP_SIEBENPFAD_VERBRAUCHER.md`
- `mcm_field_organism/capacity_limited_mcm_f3_runtime.py`
- `mcm_field_organism/mcm_f3_runtime.py`
- `mcm_field_organism/w7m_capacity_function_matrix.py`
- `mcm_field_organism/w7p_measurement_compositor.py`
- `mcm_field_organism/w7ae_cap_seven_path_consumer.py`

## 15. Naechster Schritt

W7-AG darf die optionale passive Observerweitergabe, getrennte angeglichene
CAP-Messkopien und ihre rein rollenbezogenen Vertragstests implementieren.
Die vorhandenen W7-AE-Produkte muessen bitgleich bleiben. P0-
Nullstartmesskopien duerfen nur implementiert werden, wenn ihre getrennte
Zustandsbindung ohne Aenderung von W7-AA moeglich ist; andernfalls bleibt der
absolute CAP/P0-Vergleich gesperrt. Keine Pfadauswertung, Intervention, kein
Browser, Report oder Forschungslauf.

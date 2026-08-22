# S1-VF: MPZ-1 statischer Anatomie-, Ursachen- und Bilanzvollstaendigkeitsaudit

## Freigabe und Grenze

S1-VF setzt die Anschlussfreigabe aus S1-VE ausschliesslich als statischen
Audit um. Geprueft wird, ob fuer `MPZ-1` innerhalb des vorhandenen lokalen
Audio-Video-Feldpfads eine widerspruchsfreie, begrenzte und vollstaendig
bilanzierbare Anatomie beschrieben werden kann.

S1-VF enthaelt:

- keine Gleichung und keinen Zahlenwert;
- kein Uebergangsgesetz und keine Wirkungsfunktion;
- keine Implementierung und keine Fixture;
- keine Runtime-, API- oder Snapshotaenderung;
- keinen Test, Comparatorlauf oder Feldlauf;
- keinen Befund einer Memory- oder Wiedererkennungsfunktion.

## Vorhandene Feldanatomie

Der aktive Audio-Video-Pfad besitzt bereits:

- getrennte reduzierte auditive und visuelle Rezeptorzustaende;
- je einen festen Dock pro Modalitaet;
- eine zweidimensionale, vorgegebene Feldgeometrie;
- eine auditive Dockreihe direkt neben der ersten visuellen Dockreihe;
- lokale orthogonale Nachbarschaften;
- einen neutralen Aktivierungszustand S und optionalen schnellen Nachhall H;
- eine kausal geordnete, asynchrone Uebergabe abgeschlossener
  Rezeptorzustaende.

Die Docks, Nachbarschaften und Ausbreitungswege sind technische Anatomie. Sie
werden durch Wahrnehmung weder erzeugt noch umgebaut.

Der `ReceptorDistributor` enthaelt ausdruecklich keine Fusion, Gewichte oder
Zustandsfortschreibung. Der aktive Feldkern enthaelt ausser S und H keinen
perzeptiven Kandidatenzustand. MPZ-1 muss deshalb privat und vollstaendig
getrennt von beiden Bestandsrollen bleiben.

## Begrenzter lokaler Pruefkorridor

Der erste zulaessige Korridor besteht ausschliesslich aus den bereits
vorhandenen Nachbarschaftsmotiven an der direkten Audio-Video-Dockgrenze:

```text
auditive Dockposition
        |
vorhandene orthogonale Nachbarschaftskante
        |
visuelle Dockposition der ersten visuellen Reihe
```

Ein Motiv ist nur dann zulaessig, wenn beide Endpunkte in der bestehenden
Geometrie direkte Nachbarn sind. Es darf keine virtuelle Fernkante, keine
neue Topologie und keine nach einem Versuchsarm gewaehlte Zuordnung geben.

Visuelle Dockpositionen ohne direkte auditive Nachbarschaft gehoeren nicht in
den ersten Korridor. Eine spaetere Ausdehnung auf das ganze Feld ist nicht
durch S1-VF freigegeben.

## Lokale Ursachenbindung

Die einzige fuer MPZ-1 zulaessige Bildungsquelle ist lokale Feldarbeit an
einem festen Grenzmotiv. Sie liegt nur vor, wenn innerhalb der normalen
kausalen Feldfortsetzung Einfluesse beider angrenzender Dockseiten im selben
lokalen Motiv wirksam werden.

Dies kann anatomisch auf zwei Weisen erreichbar sein:

- beide reduzierten Rezeptorkontakte tragen im selben Feldintervall lokal bei;
- ein frischer lokaler Beitrag trifft auf eine noch vorhandene lokale S/H-Lage
  der anderen Dockseite.

Die Ursache wird ausschliesslich aus lokalen Feld- und Kontaktrollen gelesen.
Unzulaessig sind Modalitaetslabels als Schaltcode, Snapshot-IDs, Fixture-Rollen
wie `A1` oder `V1`, ein externes Paarungsflag, ein globales Zeitfenster ohne
lokalen Feldkontakt oder ein nachtraeglicher Comparatorentscheid.

S und H sind damit moegliche lokale Quellen einer Bildungsinteraktion, aber
nicht der MPZ-1-Zustand selbst. Wenn ein spaeteres Uebergangsgesetz lediglich
S, H oder deren Produkt fortschreibt, greift die S1-VE-Stoppregel.

## Private Kandidatenanatomie

S1-VF laesst pro festem Grenzmotiv nur eine endliche private Traegermenge zu.
Die Anzahl muss vor einer spaeteren Implementierung fest und positiv sein;
S1-VF setzt keinen Wert.

Jeder Traeger besitzt genau folgende anatomische Rollen:

1. **verfuegbar:** Der Traeger enthaelt keine perzeptive Disposition und kann
   durch zulaessige lokale Feldarbeit beansprucht werden.
2. **formend:** Der Traeger ist einem begrenzten lokalen Feldmuster
   zugeordnet, besitzt aber noch keine stabilisierte Rueckwirkungsrolle.
3. **stabilisiert:** Der Traeger enthaelt eine begrenzte lokale
   Prototypdisposition und darf spaeter ausschliesslich am selben Grenzmotiv
   an einer Kandidatenrueckwirkung teilnehmen.
4. **loesend:** Die fruehere Disposition darf nicht mehr rueckwirken; der
   Traeger befindet sich in der vollstaendigen lokalen Freigabe.

Diese Rollen sind kein Uebergangsgesetz. S1-VF legt weder fest, wann ein
Traeger die Rolle wechselt, noch wie eine Prototypdisposition gebildet,
verglichen oder aktualisiert wird.

## Inhalt eines Traegers

Ein formender oder stabilisierter Traeger darf nur eine feste, lokal begrenzte
Darstellung des Grenzmotivs enthalten. Die Darstellung muss:

- aus normal erreichter lokaler Feldgeschichte stammen;
- eine vorab feste Dimension besitzen;
- auf den Wertebereich des Feldkerns begrenzt sein;
- unabhaengig von Semantik, Woertern, Objekten und Armrollen sein;
- kleiner sein als die vollstaendige auditive und visuelle Rezeptorhistorie;
- ohne Rohframes, Audiosamples, Ereignisliste oder Zeitstempelwarteschlange
  auskommen.

Die Darstellung darf keine neue Rezeptorgeometrie erfinden. Sie darf nur die
lokalen Endpunkt- und Nachbarschaftsrollen des festen Grenzmotivs verwenden.

Eine einzelne gleitende Paarstatistik ist keine ausreichende
Kandidatenanatomie. MPZ-1 bindet zusaetzlich eine endliche Menge konkurrierender
Traeger, eindeutige lokale Eigentuemlichkeit, Freigabe und Wiederverwendung.
Ob diese Zusatzrollen funktional ueber eine staerkere Statistikbaseline
hinausgehen, ist in S1-VF noch nicht entschieden.

## Bilanzvollstaendigkeit

Fuer jedes Grenzmotiv gilt eine rein anatomische Erhaltungsregel:

- Die Gesamtzahl seiner privaten Traeger ist fest.
- Jeder Traeger gehoert zu genau einer der vier Rollen.
- Ein Traeger kann nicht gleichzeitig mehreren Grenzmotiven gehoeren.
- Eine Rollenveraenderung darf keinen Traeger erzeugen oder vernichten.
- Nach vollstaendiger Loesung muss derselbe Traeger wieder als verfuegbar
  bilanzierbar sein.
- Prototypinhalt ist nur in formender oder stabilisierter Rolle zulaessig.
- Nur stabilisierte Traeger duerfen spaeter eine Kandidatenrueckwirkung
  besitzen.

Die Summe der vier Rollenmengen muss zu jedem auditierbaren Zeitpunkt exakt
der vorab festgelegten lokalen Traegermenge entsprechen. Dies ist eine
Anatomieidentitaet und keine dynamische Gleichung.

## Lokale Eigentuemlichkeit und Atomizitaet

Der Kandidatenzustand gehoert dem festen Grenzmotiv, nicht einem einzelnen
Rezeptorframe, einem globalen Versuch oder dem Comparator. Ein Traegerwechsel
muss spaeter gemeinsam mit genau einem Feldschritt atomar entschieden werden.

S1-VF erlaubt keine teilweise sichtbare Zwischenlage. Entweder sind Feld- und
Kandidatenvorzustand unveraendert, oder ein vollstaendiger spaeterer Schritt
liegt vor. Eine oeffentliche API- oder Snapshotrolle folgt daraus nicht.

Der Kandidat-OFF-Zustand enthaelt an jedem Grenzmotiv nur verfuegbare Traeger
ohne Prototypinhalt und ohne Rueckwirkung. Der bestehende Feldkern muss in
diesem Zustand unveraendert bleiben.

## Verbotene und ungueltige Zustaende

Fail-closed ungueltig sind insbesondere:

- ein Traeger ohne eindeutige Rolle oder mit mehreren Rollen;
- negative, nicht endliche oder dynamisch wachsende Traegerzahl;
- ein Traeger mit mehreren lokalen Eigentuemern;
- Prototypinhalt in verfuegbarer oder vollstaendig geloester Rolle;
- ein formender Traeger mit Feldrueckwirkung;
- ein stabilisierter Traeger ohne begrenzten lokalen Inhalt;
- gespeicherte Rohdaten, vollstaendige Eingabefolgen oder Replayzeiger;
- gespeicherte Objekt-, Wort-, Bedeutungs- oder Klassenkennung;
- ein externer Paarcode, Armname oder erwarteter Ergebniswert;
- eine Fernbeziehung ohne vorhandenen lokalen Nachbarschaftspfad;
- ein Zustand, der nur ein Alias fuer S, H, Snapshot oder Comparatoroutput ist;
- stilles Clipping, Loeschen oder Reset ausserhalb der lokalen Bilanz;
- eine Kandidatenrolle im oeffentlichen Feldsnapshot;
- eine Rueckwirkung im Kandidat-OFF-Zustand.

## Strukturelle Abgrenzung

### Gegen S/H und Nachhall

S/H bleibt der aktive Feldvorzustand und eine moegliche Bildungsquelle. Der
private Traegerbestand ist anatomisch getrennt, endlich und nach einer
konstruktiven S/H-Angleichung weiterhin vollstaendig auditierbar. Eine
spaetere Wirkung ist damit anatomisch darstellbar, aber noch nicht belegt.

### Gegen Replay

MPZ-1 besitzt keine Folge, keinen Puffer und keinen Zeiger auf fruehere
Rezeptorzustaende. Ein lokaler Prototyp ist fest dimensioniert und darf keine
vollstaendige Historie rekonstruierbar machen.

### Gegen Fixed Adapter

Die Traegerrollen sind durch lokale Feldgeschichte erreichbar und nicht vor
dem Verlauf fest eingestellt. Ohne ein spaeteres gueltiges Uebergangsgesetz
ist diese Abgrenzung noch keine Funktionsprognose.

### Gegen gleitende Statistik

Eine einzelne getrennte oder gemeinsame gleitende Statistik besitzt keine
diskreten konkurrierenden lokalen Traeger mit Eigentuemlichkeit, Freigabe und
Wiederverwendung. Eine staerkere begrenzte Prototypbank kann diese Anatomie
jedoch moeglicherweise reproduzieren und bleibt deshalb verpflichtende
Gegenbaseline fuer den naechsten Audit.

### Gegen DTS-1 und Ressourcenledger

Die vier Rollen allein sind vollstaendig durch Ressourceninfrastruktur
darstellbar und daher kein Kandidatenbefund. Die offene MPZ-1-Frage liegt nur
in der paarungsabhaengigen lokalen Prototypbildung und spaeteren Feldwirkung.
Reduziert sich diese auf das Ledger, wird MPZ-1 gestoppt.

### Gegen ACM-1H

MPZ-1 darf keinen vorhandenen ACM-Relationszustand oder ACM-Adapter verwenden.
Der erste Korridor besitzt genau ein festes Grenzmotiv und keine Beziehung
zwischen zwei benachbarten Kanten. Wird spaeter ein solcher Relationsadapter
benoetigt, greift die S1-VE-Stoppregel.

## Vollstaendigkeitsmatrix

| S1-VE-Bedingung | S1-VF-Bindung | Status |
|---|---|---|
| lokale Ursache | lokale Feldarbeit am vorhandenen Audio-Video-Grenzmotiv, ohne externen Paarcode | anatomisch gebunden |
| Bilanz oder Ressourcengrenze | feste lokale Traegermenge mit vier ausschliesslichen Rollen | anatomisch gebunden |
| erreichbare Feldgeschichte | nur normaler Rezeptor-, Dock- und Feldpfad | anatomisch gebunden |
| eigene Feldprognose | spaetere paarungsspezifische Rueckwirkung nach S/H-Angleichung | aus S1-VE uebernommen, dynamisch offen |
| staerkste Gegenbaseline | begrenzte gemeinsame Statistik und konkurrenzfaehige Prototypbank | fuer Folgeaudit gebunden |
| klare Stoppbedingung | Reduktion auf S/H, Replay, Statistik, DTS oder ACM beendet MPZ-1 | gebunden |

Die Anatomie ist damit statisch widerspruchsfrei beschreibbar. Nicht geklaert
ist, ob ein lokales Uebergangsgesetz ohne gesetzte Paarlogik existiert und ob
die resultierende Wirkung eine begrenzte konkurrenzfaehige Prototypbaseline
uebertrifft.

## Auditentscheidung

```text
S1_VF_EXISTING_CROSS_DOCK_LOCAL_MOTIF_AVAILABLE
S1_VF_LOCAL_FIELD_WORK_SOURCE_BOUND
S1_VF_FIXED_PRIVATE_CARRIER_SET_BOUND
S1_VF_AVAILABLE_FORMING_STABILIZED_RELEASING_ROLES_EXCLUSIVE
S1_VF_LOCAL_CARRIER_BALANCE_COMPLETE
S1_VF_NO_RAW_DATA_NO_SEQUENCE_NO_LABEL_STATE
S1_VF_OFF_PATH_REMAINS_EXISTING_FIELD_CORE
S1_VF_ANATOMY_CONDITIONALLY_ADMISSIBLE
S1_VF_TRANSITION_CAUSE_AND_BASELINE_NONREDUCTION_STILL_OPEN
S1_VF_NO_FUNCTION_FINDING
S1_VF_NO_EQUATION_NO_PARAMETER_NO_IMPLEMENTATION_NO_TEST_NO_RUN
```

S1-VF laesst MPZ-1 nur anatomisch zum naechsten statischen Gate zu. Es liegt
kein Befund vor, dass die Rollen gebildet werden, dass ein Prototyp spaeter
wirkt oder dass eine technische Wiedererkennung moeglich ist.

## Genau ein naechster Schritt

Der einzige fachlich begruendete Anschluss ist:

```text
S1-VG - statischer MPZ-1-Uebergangsquellen- und
        Baseline-Nichtduplizierungsaudit
```

S1-VG darf ausschliesslich pruefen:

- ob jeder Rollenwechsel eine lokale, endogene Quelle und Senke besitzt;
- ob Prototypbildung ohne externen Paarcode und ohne Rohhistorie definierbar
  ist;
- ob Abschwaechung, Aktualisierung, Konflikt und Freigabe anatomisch
  unterschiedliche Ursachen besitzen;
- ob eine begrenzte konkurrenzfaehige gemeinsame Prototypbaseline die gesamte
  MPZ-1-Prognose bereits strukturell reproduziert.

S1-VG darf keine Gleichung, Parameter, Implementierung, Fixture, Runtime-,
API- oder Snapshotaenderung und keinen Test- oder Feldlauf enthalten. Wenn
keine nicht duplizierte Uebergangsursache verbleibt, wird MPZ-1 dort gestoppt.

## Projektgrundlagen

- [S1-VE Kandidaten- und Falsifikationsvertrag](S1VE_MPZ1_STATISCHER_KANDIDATEN_UND_FALSIFIKATIONSVERTRAG.md)
- [Gemeinsamer Audio-Video-Feldkontakt](architektur/026_GEMEINSAMER_AUDIO_VIDEO_FELDKONTAKT.md)
- [Rezeptorvertrag und Dockgrenze](architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md)
- [Aktive Audio-Video-Feldgeometrie](../mcm_field_organism/audio_video_field_geometry.py)
- [Aktiver neutraler Feldkern](../mcm_field_organism/neutral_local_field_substrate.py)
- [Rezeptorenverteiler](../mcm_field_organism/receptor_distributor.py)
- [DTS-1 Ressourcenanatomie-Baseline](S1HI_DTS1_DISKRETE_RESSOURCENANATOMIE_UND_ERHALTUNGSIDENTITAET.md)
- [ACM-1H terminaler Zweigabschluss](S1UL_ACM1H_STATISCHER_ZWEIGABSCHLUSS_UND_KONSOLIDIERUNGSAUDIT.md)

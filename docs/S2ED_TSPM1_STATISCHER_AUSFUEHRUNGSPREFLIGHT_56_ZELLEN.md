# S2-ED: Statischer Ausfuehrungspreflight des 56-Zellen-Vergleichs

## Auftrag und Ergebnis

Gepruefter Quellstand: `7cefe7d16d037a8108d90f2fbcc3202b209c0a89`.
Grundlage sind die ausdrueckliche S2-ED-Freigabe, S2-EC und die gebundenen
Vergleichsvertraege S2-DQ/DR/DT/DU/DV samt S2-DS- und S2-DX-Abnahmen.
Die aelteren Richtungsangaben im Forschungsweg und in der README erweitern
diesen Auftrag nicht.

**`BLOCKED_STATIC_EXECUTION_PREFLIGHT`: fuenf offene Bindungen.**

Die 56-Zellen-Ausfuehrung bleibt gesperrt. Das ist keine funktionale
Entscheidung ueber TSPM-1. Der in S2-EC abgenommene einmalige Abschluss der
51 synthetischen Vertragstests bleibt bestehen. Tests auf Vertragstreue
ersetzen nicht die hier geforderte Pruefung der Vergleichsmethodik.

Es wurden nur Quelltexte, AST, JSON und Git-Objekte gelesen und Dateihashes
bzw. kanonische Vertragsdigests nachgerechnet. Keine Projektimporte,
Registrybildung, Zustandsfunktion, Tests, Comparator- oder Zellaufrufe.
Keine Laufnummer; keine Code-, API-, Snapshot- oder Feldpfadaenderung.

## Statisch bestaetigter Bestand

- Die literalen H1-H7-Geschichten und acht Arme bilden 56 geplante Zellen.
  Pro Arm sind 42 Bildungseingaben und 18 Proben vorgesehen; ueber acht
  Arme sind das 336 Bildungsschritte und 144 Proben, keine ausgefuehrten
  Aufrufe. B0 ignoriert die Eingaben absichtlich.
- Die gemeinsamen Traeger besitzen acht auditive und 18 visuelle Werte.
  Beide PPB-Arme verwenden unveraendertes PPB-1. B1_DIRECT verarbeitet
  alle Originalframes; B1_BUDGET_MATCHED nur die vorab gebundenen Indizes.
  Deren Anzahl ist ueber die sieben Geschichten 19 pro Modalitaet,
  gegenueber 42 im Direktarm. Das sind getrennte Vergleichsrollen, keine
  nachtraegliche Angleichung an beobachtete TSPM-Ergebnisse.
- Das gemeinsame Speichermaximum betraegt 269 logische 64-Bit-Woerter.
  Die Armbelegungen 269/0/176/176/264/29/255/269 bleiben darunter.
  Dies ist ein funktionales Ressourcenmodell, keine Messung des realen
  Python-Speichers. Gleiches Maximum bedeutet nicht gleicher Verbrauch.
- Die gemeinsamen Operationsgrenzen lauten 293 funktionale Schreibwerte
  je Bildung, 234 Distanzterme je Bildung bzw. Probe und null funktionale
  Probeschreibwerte. Die Herkunft dieser Grenzen ist gebunden; der
  Verbrauchsnachweis ist wegen ED-B02 noch nicht ausreichend.
- Eingabefolge, Probeindizes und synthetische Zeitfenster sind armgleich.
  Die Zeitbasis ist die gebundene Expositionsfolge, keine gemessene
  Wanduhr-Haltedauer. Insbesondere liest H2 nach Bildung 1 einen
  eingefrorenen Zwischenstand mit einem Probezeitfenster hinter dem
  geplanten Bildungshorizont. Die Probe fuehrt die Bildungsuhr nicht
  fort; daraus darf kein realzeitlicher Haltedauerbefund entstehen.
- R0 besitzt eigene generische Fast- und Zwei-Ebenen-Zustaende sowie
  eigene Bildungs- und Abrufzweige. Diese verwenden keine TSPM-Typen
  oder TSPM-Operatoren. Die gemeinsame Nutzung des unveraenderten PPB-1
  ist Bestandteil der Reduktionsbaseline. Die vollstaendige bisher
  gebundene R0-Projektion bleibt erhalten; ihre Ergebnisgleichheit wurde
  hier nicht ausgefuehrt oder behauptet.
- Acht kanonische Vertragsdigests stimmen. Die sieben erfassten Quellen
  stimmen mit dem S2-EB-Quellstand ueberein. Seit diesem Stand sind nur
  sieben Dokumentations-/Ergebnisdateien hinzugekommen.

## ED-B01: Funktionsvergleich verlangt teilweise die Kandidatenarchitektur

Quellen: Vergleichsmodul `probe_s2dr_arm` ab Zeile 1361,
`_predicate_vector` ab Zeile 1928; S2-DT `predicate_projection` und
S2-DU `predicate_corrections`.

P1 fordert neben Wiedererkennung `fast_recognized`. P2 verlangt
`fast_recognized is False`, zwei Slow-Befunde und Prototypdigests.
P3 verlangt ebenfalls eine bestimmte Fast-/Slow-Verteilung. Diese
Diagnostik ist fuer TSPM-1 sinnvoll, wird aber unveraendert als
Funktionspunktzahl auf alle einfachen Baselines angewendet.

Die B1-Arme liefern fuer die nicht vorhandene Fast-Rolle `None`.
Deshalb kann selbst ein erfolgreicher spaeter PPB-Abruf P2 nicht
erfuellen: `None is False` ist falsch. B2/B3/B4 liefern keine
Slow-Rollen und koennen P2/P3 unabhaengig von ihren Abrufwerten nicht
erfuellen. Eine bessere Punktzahl kann somit allein die gewaehlte
Zwei-Ebenen-Architektur belohnen, statt einen funktionalen Vorteil zu
zeigen. Das ist eine Luecke der bisherigen Vertragsprojektion, nicht
nur ein Implementierungsfehler.

Zusaetzlich prueft P4 nur zwei positive Abrufe, nicht die in S2-DT
geforderten armbezogenen Verdraengungsrelationen. P5 prueft die
H7-Boolfolge, aber nicht selbst alle gebundenen Fehler-/Ledgerrollen.
H6 geht nicht in P1-P5 ein; seine Rolle als gesonderter Kapazitaetsbefund
oder zwingendes Gueltigkeitsgate muss eindeutig bleiben.

Erforderlich ist eine statische Trennung zwischen armneutralem
Funktionsresultat und armbezogener Mechanismusdiagnostik. Erfolgswerte
duerfen nicht durch Umbenennen fehlender Fast-/Slow-Rollen erzeugt
werden. Die Zuordnung jeder Geschichte zu Funktion, Diagnostik oder
Gueltigkeitsgate muss vor der Ausfuehrung feststehen.

## ED-B02: Gemeinsame Grenzen, aber kein einheitlicher Verbrauchsnachweis

Quellen: Vergleichsmodul Zeilen 1194, 1240, 1270, 1530 und 1590;
PPB-1 `advance_ppb1_bank` ab Zeile 575;
TSPM-1 `probe_tspm1_read_only` ab Zeile 2928.

Beide PPB-Bildungsarme melden `(176, 0)`, obwohl der unveraenderte
PPB-Kern fuer belegte Slots Distanzen berechnet. TSPM-1 und R0 melden
pauschal `(293, 234)` und bei Proben 234, waehrend B2/B4 Distanzterme
belegungsabhaengig zaehlen. Grenzwerte, obere Kostenabschaetzungen und
tatsaechliche Verbrauchswerte sind damit nicht einheitlich getrennt.

Der TSPM-Probezweig ruft nach seinem Kernabruf beide Slow-Proben zur
S1WU-Belegbindung erneut auf. Ob diese Arbeit als funktionaler Aufwand
oder gesonderter Belegaufwand gilt, ist im aktuellen Zaehler nicht
nachvollziehbar. Ein korrekter Grenzwert im Receipt behebt diese Luecke
nicht. Es wird hier weder eine konkrete Budgetueberschreitung noch
ein gemessener Kostenvorteil behauptet.

Vor Ausfuehrung sind Zaehlereinheit, Umfang, Herleitung und Trennung
von funktionalem Aufwand und Belegaufwand fuer alle Arme widerspruchsfrei
zu binden. Die bestehenden Grenzen duerfen nicht stillschweigend
erhoeht oder als gemessene Verbraeuche ausgegeben werden.

## ED-B03: Tie- und Entscheidungsregeln sind unvollstaendig

Quellen: S2-DT `simple_baseline_rank` und `decision_priority`;
Vergleichsmodul `_decision_from_vectors`, Zeilen 1979-1998.

S2-DT bindet die Rangfolge Punktzahl, Fehlersumme, Aufnahmelatenz,
funktionale Schreibwerte und Arm-ID. Der Code verwendet nur Punktzahl,
Fehlersumme und Arm-ID; die zwei mittleren Kostenrollen fehlen.

Zudem wird Gleichheit zur staerksten einfachen Baseline vor der
Vollstaendigkeit der Kandidatenpraedikate als
`FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS` eingeordnet. Rein statisch
folgt daraus: Auch identische unvollstaendige oder vollstaendig falsche
Praedikatvektoren koennen diesen Namen erhalten. S2-DQ nennt diese
Reihenfolge, S2-DT nennt dagegen Funktionsungueltigkeit vor Erklaerung.
Die Ausfuehrung darf diesen Vertragswiderspruch nicht entscheiden.

Erforderlich sind eine eindeutige Prioritaet fuer methodische
Gueltigkeit, Funktionsgueltigkeit und Reduktion sowie die vollstaendige
Tie-Bindung. Gleiches Scheitern darf nicht als gueltige Funktion gelten.
Das ist eine statische Kontrollflussableitung, keine Vergleichsauswertung.

## ED-B04: Der Gesamtvergleich nimmt keine vollstaendige Quellkette ab

Quellen: Vergleichsmodul `_source_blob_digests` ab Zeile 517,
`validate_s2dr_cell_result` ab Zeile 1659 und
`compare_s2dr_results` ab Zeile 2028.

Der Comparator prueft 56 eindeutige Zell-IDs und die Zuordnung des
Plandigests, nimmt aber den extern uebergebenen Registrydigest nur
syntaktisch ab. Er rekonstruiert nicht die gesamte Registrybindung
und ruft den relationalen Zellvalidator nicht auf. Die Datentraeger
sind zwar eingefroren, enthalten aber veraenderbare Payload-Dictionaries;
die Konstruktorpruefung ersetzt daher keine erneute Abnahme am
Vergleichseingang. Selbstkonsistente Digests allein belegen ausserdem
keine tatsaechliche Owner-Ausfuehrung.

Der Zellvalidator bindet viele Ergebnisrelationen, aber keinen erwarteten
Owner aus einer Matrixreservierung an `receipt.owner_id`. Die
`consumption_id` des Owners fehlt im Zellreceipt. Unter
`source_blob_digests` stehen Hashes von Traeger-/Paarliteralen, nicht
die Hashes des ausgefuehrten Quellcodes. Die separat vorhandenen
S2-EB-Quellbelege sind kein Ausfuehrungsmanifest der spaeteren Matrix.

Erforderlich ist die vollstaendige, vorab gebundene Kette von
Quellmanifest und Registry ueber reservierte Owner und Zellresultate
bis zum Comparator. Sie muss exakt die erwarteten 7-mal-8 Rollen,
die gebundene Reihenfolge, Quellen, Payloads und Receipts abnehmen.
Neue Digestrollen duerfen nicht zirkulaer werden. Hier wird noch
keine neue Signatur oder Implementierung festgelegt.

## ED-B05: Einmaligkeit und atomare Publikation enden derzeit im Speicher

Quellen: Vergleichsmodul `S2DRCellOwner`, Zeilen 1731-1905;
S2-DR `runner_entrypoint_allowed=false`;
S2-DQ `matrix.exactly_once_per_cell` und `atomic_total_publication`.

Lock und Ownerstatus verhindern einen zweiten Aufruf desselben
Owner-Objekts. Ein neu erzeugtes Objekt besitzt jedoch wieder den
Status FRESH. Es existiert kein angebundener dauerhafter Matrixversuch,
der Neustarts, zweite Prozesse und Wiederverwendung nach Abbruch sperrt.
Die Suche nach den Zellowner-/Comparator-Verwendungen findet nur die
zwei privaten Implementierungs-/Testdateien. Ein Matrixpublisher wurde
bisher ausdruecklich nicht implementiert; sein Fehlen ist keine
nachtraegliche Verletzung der alten Implementierungsfreigabe.

Erwartete S2DR-Fehler setzen den Owner auf FAILED. Andere Ausnahmen
verlassen den inneren Handler, ohne diesen terminalen Status zu setzen;
das Objekt bleibt BUSY. Es gibt dabei keine regulaere Teilausgabe,
aber noch keinen dauerhaften, eindeutig terminalen Abbruchbeleg.

Erforderlich ist ein statischer Vertrag fuer dauerhafte Reservierung
vor der ersten Zelle, unwiderruflichen Verbrauch auch bei Absturz,
keine Wiederaufnahme/Retry und einen eindeutigen Abbruchbeleg.
Erfolg darf erst nach Abnahme aller 56 Zellen und des Comparators
atomar veroeffentlicht werden. Teilbelege duerfen nur als fehlgeschlagener
Versuch erscheinen, niemals als vollstaendiger Vergleich. Diese
Aufzeichnung ist Versuchsmetadatum, keine Persistenzfunktion des
Memory-Kerns. Ausfuehrung und Publisherimplementierung sind nicht freigegeben.

## Grenze der Wahrnehmungsrepraesentation

`_joint_values` (Zeile 904) und `_sequence` (Zeile 927) wiederholen
je einen Skalar ueber alle acht auditiven bzw. 18 visuellen Traeger.
Damit besitzt die Eingabefamilie trotz 26 Komponenten nur zwei frei
variierte Amplituden. H1-H7 koennen auf dieser Grundlage Aufnahme,
Wiederholung, Konflikte, Kapazitaet und spaeteren Abruf untersuchen,
aber keine allgemeine Qualitaet raeumlicher, spektraler oder relationaler
Wahrnehmungsrepraesentationen bewerten.

Das Auswertungskriterium bleibt erhalten, mit dem aktuellen Status
**`NOT_ASSESSED_BY_BOUND_FIXTURES`**. Es wird weder als bestanden noch
als widerlegt gewertet. Eine spaetere Aussage hierzu braeuchte eine
eigene vorab gebundene Operationalisierung. S2-ED erweitert weder die
Fixtures noch die Matrix und fuehrt keine neue Memory-Funktion ein.

## Konsequenz und naechster Schritt

Die Richtung bleibt eine private technische Zwei-Zeitskalen-Memory-
Architektur mit unveraendertem PPB-1 und unabhaengiger R0-Gegenbaseline.
Keine neue Kandidatenmechanik und kein MCM-spezifischer Wirksamkeitsbefund.

Als genau naechster Schritt wird **S2-EE: statischer Korrektur- und
Ausfuehrungsbindungsvertrag fuer ED-B01 bis ED-B05** vorgeschlagen.
Er muss den architekturneutralen Funktionsvergleich, zaehlbare Kosten,
vollstaendige Tie-/Gueltigkeitsregeln und die dauerhafte Belegkette
zusammenhaengend schliessen. Keine stillschweigende Reparatur im Lauf.
Danach ist S2-ED am korrigierten Vertrag erneut statisch abzunehmen;
Implementierung, Tests und Einmalausfuehrung benoetigen weiterhin ihre
jeweilige gesonderte Freigabe.

# MCM_FIELD_ORGANISM

`MCM_FIELD_ORGANISM` entwickelt ein technisches audiovisuelles
MCM-Wahrnehmungssystem mit gemeinsamen Rezeptoren, einem dynamischen Feld und
einer davon getrennten perzeptiven Zwei-Bereich-Memory.

Faehigkeiten werden nur benannt, wenn sie durch vorab gebundene,
reproduzierbare Befunde gestuetzt sind. Bekannte Engineeringverfahren bleiben
der verbindliche Vergleichsmassstab.

## Systemstand

```text
kanonische RGB-/PCM-Quelle
-> auditive und visuelle Rezeptoren
-> 336 reduzierte Wahrnehmungswerte
   |-> MCM-Feldkontakt
   `-> atomare Zwei-Bereich-Memory
       -> read-only Teilhinweisabruf
       -> Kontexthypothese oder Enthaltung
```

Das Default-Live-Profil erzeugt `288` visuelle und `48` auditive Werte.
Feld und Memory erhalten unabhaengige Geschwisterprojektionen desselben
Wahrnehmungszustands. Rohbilder, PCM-Fenster und Feldsnapshots werden nicht als
Memoryinhalt gespeichert.

Die Memory besitzt genau zwei oeffentliche Bereiche:

- `A_RECENT`: B4-Inhalte und Kurzfolge mit interner Fast-Spur;
- `B_STABLE`: getrennte auditive und visuelle stabile Prototypen.

Bestaetigt sind ein nichttrivialer AV-Feldpfad, wiederholungsabhaengige
Verdichtung, kontrolliertes Vergessen, begrenzte Holdout-Generalisation sowie
visueller und auditiver Teilhinweisabruf. Rollenfreie AV-Stroeme koennen mehrere
Erfahrungen bilden und bei fehlendem, unpassendem oder mehrdeutigem Kontext
kontrolliert enthalten. Alle Abruf- und Kontextoperationen bleiben read-only;
Kontext wirkt nicht in Feld oder Memory zurueck.

Die Funktionen werden durch Slotscans, L1-Vergleiche, adaptive Prototypbildung
und transparente Entscheidungstabellen erklaert. Das ist ein technischer
Memory- und Kontextnutzen, aber kein Nachweis besonderer MCM-Speicherphysik.

## Abgeschlossen: auditiver Maskenvergleich NP/NQ/NR

Der Vergleich der festen zusammenhaengenden und verteilten 24-Band-Sicht
ist geschlossen. Die folgenden Zahlen stammen ausschliesslich aus den
vorhandenen Befunden; fuer diese Konsolidierung wurde nichts neu berechnet.

- [S2-NP: Rezeptorevidenz ohne Memory](reports/s2np/s2np-coverage-corpus-comparison-20260907-01/BEFUND.md):
  begrenzter, regelabhaengiger Vorteil der verteilten Sicht. Eine falsche
  Quellenbeziehung entfiel in zwei Panels, bekannte Beziehungen blieben
  erhalten. Die getrennte 48-Band-Diagnose war keine garantierte Obergrenze;
  insbesondere beeinflusst auch die Mittelung die Slow-Anwendbarkeit.
- [S2-NQ: Transfer an real gebildeter Memory](reports/s2nq/s2nq-real-mask-memory-transfer-20260908-01/BEFUND.md):
  Wiederverwendung der bereits untersuchten NP-Quellen, keine unabhaengige
  Korpusbestaetigung. Je vier richtige A- und B-Abrufe blieben erhalten,
  darunter jeweils drei variierte Hinweise. Zwei Fehlzulassungen derselben
  Kontrollquelle in zwei Geschichten entfielen, nicht zwei unabhaengige
  Kontrollquellen. Beziehungserhaltung und richtige oeffentliche Abrufe
  hatten getrennte Nenner.
- [S2-NR: unabhaengig vorversiegelter neuer Runtime-Strom](reports/s2nr/s2nr-mask-runtime-transfer-20260908-01/BEFUND.md):
  technisch gueltig, funktional negativer Transfer. Zielspuren blieben
  gespeichert und anwendbar. Zusaetzliche Konkurrententreffer verhinderten
  zwei richtige eindeutige Abrufe; A- und B-Erhaltung jeweils
  `N/D/R/L = 1/1/0/1`. Hinzu kam eine Fehlzulassung vor Zielbildung.
  Bei e18 traf auch der stabile Zielslot; die Enthaltung wegen Mehrdeutigkeit
  belegt keine Unbekanntheitserkennung. Feld und Memory waren zwischen den
  Armen identisch. Gescheitert ist hier die Selektivitaet der Sicht, nicht
  die Speicherbildung oder technische Runtime.

**Keine allgemeine Ersatzregel:** Der NP/NQ-Vorteil bleibt quellenbegrenzt;
NR beweist umgekehrt keine allgemeine Ueberlegenheit der zusammenhaengenden
Sicht. Beide Masken bleiben untersuchte Forschungskonfigurationen. Keine
bevorzugte verteilte Runtimekonfiguration, keine Aenderung historischer
Defaults. Keine Wiederholung, Maskenoptimierung, Schwellenanpassung oder
B-Priorisierung. Gates bleiben `False`; historische Belege unveraendert.

**Offene Evidenzfrage:** Wie laesst sich ausreichende auditive Evidenz fuer
einen eindeutigen Abruf bestimmen, ohne relevante Konkurrenz durch eine
feste Teilansicht zu uebersehen? Dies ist noch keine Freigabe fuer Vollsicht,
Maskenvereinigung, automatische Sichtwahl oder einen neuen Versuch.

## Private Minimalruntime: konsolidierter Stand nach S2-NG

Dieser Abschnitt bewahrt die damalige Regelentscheidung im historischen
Ausgangsprofil; er begruendet keine bevorzugte verteilte Maske. Fuer den
abgeschlossenen Halbprofil-Maskenvergleich gilt die Einordnung oben.

Die ausfuehrbare private Oberflaeche ist
[`MinimalMCMRuntime336`](tools/_s2mr_private_minimal_mcm_runtime.py):
`process_once`, `snapshot`, `close`. S2-MS bestaetigte den gemeinsamen
Ereignispfad. Vollstaendige AV-Ereignisse erzeugen unabhaengigen Feldkontakt
und genau eine atomare B4-/TSPM-Formation; Teilhinweise erzeugen Feldkontakt
und read-only Abruf. Nur B4/TSPM ist atomar, nicht Feld und Memory gemeinsam.
Kontext bleibt eine getrennte auditive oder visuelle Hypothese.

[`RuntimeComparison`](tools/_s2ng_private_runtime_comparison.py) komponiert
zwei getrennte Runtime-, Feld-, Memory- und Ownerinstanzen mit denselben
unveraenderlichen Eingaben. `AudioRuleBindingV1` bindet Regel-ID, Bandplan,
Konfiguration und Implementierungshashes vor dem ersten Ereignis.

**Bevorzugte Forschungskonfiguration fuer kommende begrenzte Versuche:**
ausdruecklich vorab gebundenes `ALL_BANDS_24`, ausschliesslich fuer auditive
B4-/Fast-Anwendbarkeit (`max(delta_0..23) <= 0.2`). Der unveraenderte
Referenzarm bleibt `HISTORICAL_SUM_L1_24` mit historischem `sum(...)/24`,
nicht `statistics.mean`. Auditory-Slow, Visualpfad, Memorybildung und
Feldkontakt bleiben unveraendert. Keine automatische Regelwahl, kein
Fallback, keine B-Bevorzugung und keine Aenderung historischer Defaults.
Das ist keine allgemeine Produktumstellung oder neue Lernregel.

Zwei getrennte Belege tragen diese private Forschungsentscheidung:

- [S2-NF: Erhaltung unter realer Konkurrenz](reports/s2nf/s2nf-real-retention-under-competition-20260906-01/BEFUND.md):
  `D/R/L = 4/4/0`, davon drei tatsaechlich veraenderte Hinweise;
  eine Fehlzulassung verhindert. Die Partialaddition verliert dagegen ihre
  Zielanwendbarkeit bei bereits mehrdeutiger Referenz. Keine allgemeine
  Verlustfreiheit.
- [S2-NG: Runtime-Transfer](reports/s2ng/s2ng-real-runtime-comparison-20260906-01/BEFUND.md):
  zwei neue richtige auditive B-Abrufe, keine Fehlzulassung; Feld und Memory
  armweise identisch. Auditiv `D=0`: Erhaltung nicht geprueft. Visuell
  `D/R/L = 2/2/0`. Die unbekannte auditive Probe bleibt mehrdeutig; dies ist
  keine nachgewiesene Unbekanntheitserkennung. Direktbaselines erklaeren alles.

S2-NG ist abgeschlossen; kein weiterer NG-Lauf. Der archivierte
[Einmalaufrufer](reports/s2ng/run_runtime_comparison_once.py) dokumentiert die
ausgefuehrte Anbindung, ist aber kein wiederzuverwendender Startbefehl.
Der [S2-NH-Plan fuer unabhaengige Quellen](docs/S2NH_UNABHAENGIGER_AV_RUNTIME_TRANSFERPLAN.md)
ist inzwischen rezeptorfrei vorversiegelt. Seine private Materialisierungs-
und Runtime-Anbindung ist [neutral mit 20/20 qualifiziert](reports/s2nh/s2nh-runtime-binding-qualification-20260906-01/BEFUND.md).
Ein fortgefuehrter HearingPath, native Zeitbindungen, die explizite NH-Felduhr,
fruehe Read-only-Hinweise und getrennte Auswertung sind technisch geprueft.
Keine versiegelten NH-Payloads wurden dabei materialisiert. Der danach
einmalig freigegebene [reale NH-Lauf](reports/s2nh/s2nh-runtime-comparison-20260907-01/BEFUND.md)
stoppte bei e02/`nh-a01` mit `ReceptorContractError` in der Materialisierung:
`NOT_EVALUABLE`, bevor Runtimes, Memoryformationen oder Feldkontakte
gestartet wurden. Der Fehlerbeleg wurde einmal read-only verifiziert;
kein Retry und keine Quellenanpassung. Alle Hauptgates sind geschlossen.
Ein NH-Transfer- oder Erhaltungsbefund liegt weiterhin nicht vor.

## Forschungsgrenze

Ein vorab versiegeltes, unabhaengig erzeugtes AV-Korpus zeigt, dass der Pfad
noch nicht robust auf ungefilterte Varianten uebertraegt:

- Blockmittelung komprimiert unterschiedliche visuelle Texturen unter die
  bestehende Slow-Schwelle und vermischt ihre Prototypen.
- Vollvektorvergleich und exakter maskierter Positionsscan besitzen dort keine
  kompatible visuelle Anwendbarkeitsgrenze.
- Audio trennt die Familien besser, bleibt durch breite B4-/Fast-Treffermengen
  und einzelne Druckaktualisierungen jedoch mehrdeutig.

Das System enthaelt sich dabei korrekt. Ein breiterer Formenvergleich zeigt,
dass die bestehenden 288 Blockmittelwerte raeumliche Struktur tragen. Der
maskenkonditionierte Pose-/Formvergleich verbessert eine verteilte 96-Werte-
Sicht deutlich. Zwei zeitlich getrennte 96er-Sichten reduzieren
Fehlzulassungen durch Konsens und ihre 192er-Vereinigung erreicht auf dem
prospektiven Formkorpus die Vollform-Obergrenze. Ein getrennter Open-Set-
Vergleich weist unbekannte, zwischenliegende und quellinkompatible Evidenz
ohne Fehlzulassung ab. Diese Zwei-Blick-Evidenz ist als fluechtige interne
`A_RECENT`-Funktion qualifiziert; sie wird nach der Auswertung verworfen und
nicht an `B_STABLE` uebergeben. Gegen real gebildete visuelle `B_STABLE`-Slots
liess sie auf dem versiegelten Korpus `5/6` bekannte Holdouts zu und wies alle
`14` unbekannten, mehrdeutigen oder inkompatiblen Faelle ohne Fehlzulassung ab.
In einem rollenfreien Lebenszyklus enthielt derselbe Teilhinweis vor der
Erfahrung und wurde nach realer Stabilisierung kontrolliert aus `B_STABLE`
zugelassen; unbekannte und widerspruechliche Hinweise enthielten weiterhin.
Diese Zwei-Blick-/Formbefunde bleiben extern kalibrierte Versuche; sie sind
keine selbst erlernte allgemeine Anwendbarkeitshuelle der Minimalruntime.
S2-ME/S2-MI werden durch die auditive Regelanbindung nicht entsperrt.

## Aussagegrenzen

Nicht belegt sind semantisches Verstehen, automatische Erinnerungsauswahl,
offene Welt, allgemeine Langzeit-Memory, autonome Handlung oder Feldrueckwirkung
innerer Kontexte. Die Simulation ist als Quellenreferenz qualifiziert;
Quellengleichheit zwischen zwei realen digitalen oder physischen Quellen ist
noch nicht nachgewiesen.

## Dokumentation

- [Gemeinsames MCM-Feld](docs/architektur/024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md)
- [Rezeptorvertrag und Dockgrenze](docs/architektur/025_REZEPTORVERTRAG_UND_DOCKGRENZE.md)
- [336-Werte-Memorybefund](docs/S2JX_DEFAULT_LIVE_MEMORY_FUNKTIONSBEFUND.md)
- [Rollenfreier Wahrnehmungsstrom](docs/S2LL_ROLLENFREIER_WAHRNEHMUNGSSTROM_PROZESSOR_VERTRAG.md)
- [Vorab versiegeltes AV-Korpus](docs/S2LS_VORAB_EINGEFRORENES_AV_TRAIN_HOLDOUT_KORPUS_VERTRAG.md)
- [Read-only Ursachenbefund](docs/S2LS_READONLY_URSACHENBEFUND.md)
- [Fluechtige A_RECENT-Zwei-Blick-Integration](docs/S2MA_FLUECHTIGE_A_RECENT_ZWEI_BLICK_INTEGRATION.md)
- [Zwei-Blick-Abruf gegen B_STABLE](docs/S2MB_BSTABLE_ZWEI_BLICK_KONTEXTABRUF.md)
- [Rollenfreier Lernlebenszyklus](docs/S2MC_ROLLENFREIER_LERNLEBENSZYKLUS_VERTRAG.md)

Historische Vertraege und Laufbelege bleiben unter `docs/` und `reports/`.
Die README ist eine kompakte Projektuebersicht, kein Forschungsjournal.

Vorarbeiten aus [MINI_DIO](https://github.com/H5Pro2/MINI_DIO) und der
[Mental-Core-Matrix](https://github.com/H5Pro2/Mental-Core-Matrix-MCM) sind
Forschungsreferenzen und gelten nicht automatisch als Evidenz dieses Projekts.

# S2-AN: Statischer PPB-1-Bildungsverbrauchsvertrag

## Auftrag und Grenze

S2-AN definiert ausschliesslich statisch, wie eine abgenommene private Audio-/
Videohuelle kontrolliert durch die bestehenden PPB-1-Lebenszyklusschritte
verarbeitet werden koennte. Es wurden keine Typen oder Funktionen
implementiert und keine Zustands-, Probe-, Baseline- oder Feldfunktion
ausgefuehrt.

Der Verbraucher ist eine Engineeringkopplung des vorhandenen PPB-1-Kerns. Er
fuehrt keine neue Speicherregel und keine neue Feldursache ein.

## Frische Vorzustaende

Audio und Video beginnen jeweils mit dem exakten frischen Bankzustand ihrer
vorhandenen Browserprofil-Config: null akzeptierte Schritte, kein Quellclock,
kein letzter Endtick und ausschliesslich freie Slots. Vorbelegte oder
fortgesetzte Bankzustaende sind fuer diesen ersten Bildungsablauf unzulaessig.

Damit stammt die gesamte spaetere Bankgeschichte nachweislich aus genau der
gebundenen Aktivbatch-Huelle.

## Einmalverbrauch

Eine private Autorisierung bindet Consumption-ID, Huellendigest,
Profilbindingdigest und beide frischen Vorzustandsdigests. Sie beginnt im
Zustand `AUTHORIZED` mit Nutzungszaehler null und darf nur gemeinsam mit einem
vollstaendigen Ergebnis in `CONSUMED` mit Zaehler eins uebergehen.

Die reine Zustandsuebergabe besitzt keinen versteckten globalen Ledger. Ein
spaeterer privater atomarer Besitzer muss stets den aktuellen
Autorisierungszustand liefern und die Wiederverwendung eines alten
`AUTHORIZED`-Objekts verhindern. Ist diese Besitzgrenze nicht materialisierbar,
wird der Verbraucher gestoppt.

## Deterministische Reihenfolge

Alle Audio- und Videoframes werden gemeinsam nach Feldfenster-Endtick,
Feldfenster-Starttick, Modalitaetsrang und Snapshot-ID geordnet. Bei Gleichstand
steht Audio vor Video. Die vorhandene Reihenfolge innerhalb jeder Modalitaet
muss erhalten bleiben.

Quellticks verschiedener Modalitaeten werden nicht verglichen. Frames,
Feldzeit und Werte werden weder umgeschrieben noch neu getaktet. Jeder
Provenienzdigest darf genau einmal im Ablauf vorkommen.

## PPB-1-Schritte und Atomaritaet

Jeder geplante Eintrag ruft ausschliesslich
`advance_s1wq_perceptual_state` fuer seine Modalitaet auf. Der Vorzustand ist
der letzte lokale Nachzustand derselben Bank. Eingabe-, Vorzustands-,
Nachzustands- und Transitiondigest muessen lueckenlos zusammenpassen.

Audio- und Videonachzustand, alle Transitionrecords, Ergebnisreceipt und
verbrauchte Autorisierung werden erst gemeinsam zurueckgegeben. Bei einem
Fehler darf kein Teilergebnis sichtbar werden.

## Vergleichs- und Claim-Grenze

Fuer einen spaeteren Funktionsvergleich bleiben sieben Arme gebunden: PPB-1,
kein Zustand, reduziertes Replay als Diagnostik, statische Prototypbank,
gleitender Zustand oder Nachhall, Attraktor und begrenztes Reservoir. Alle
Arme muessen dieselbe reduzierte Geschichte und vorregistrierte Kapazitaets-,
Zustandsbyte- und Aufrufbudgets erhalten.

Ein korrekt ausgefuehrter Verbraucher wuerde nur die technische Bildung einer
Bankgeschichte bestaetigen. Ereigniszaehler, Stabilisierung, Digests oder neue
Nachzustaende sind fuer sich kein funktionaler Speicher- oder Memory-Befund.

## Naechster Schritt

S2-AO soll Vollstaendigkeit, Nichtzirkularitaet, Einmalverbrauch und
Materialisierbarkeit statisch pruefen. Erst danach kann eine private
Implementierung erwogen werden.

Maschinenlesbarer Vertrag:
[S2AN_STATISCHER_PRIVATER_AKTIVBATCH_ZU_PPB1_BILDUNGSVERBRAUCHS_FUNKTIONS_PROVENIENZ_UND_FALSIFIKATIONSVERTRAG_V1.json](S2AN_STATISCHER_PRIVATER_AKTIVBATCH_ZU_PPB1_BILDUNGSVERBRAUCHS_FUNKTIONS_PROVENIENZ_UND_FALSIFIKATIONSVERTRAG_V1.json).

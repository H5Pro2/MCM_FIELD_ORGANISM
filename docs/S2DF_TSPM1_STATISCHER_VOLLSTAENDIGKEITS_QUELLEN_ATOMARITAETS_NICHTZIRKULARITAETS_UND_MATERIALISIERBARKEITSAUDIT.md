# S2-DF: TSPM-1 statischer Implementierungspreflight

## Auftrag und Grenze

S2-DF auditiert ausschliesslich statisch den S2-DE-Vertrag. Geprueft werden
Fast-Slots, Match, Aktualisierung, Ablauf, LRU, Teilassoziationskonflikte,
Originalquellenkonsolidierung, atomare PPB-1-Uebergabe, getrennte Befunde,
read-only Abruf, Digests, Einmaligkeit, Nichtzirkularitaet und eindeutige
Materialisierbarkeit.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe- oder
Runnerfunktion aufgerufen, keine Tests ausgefuehrt und keine Implementierung
geaendert. PPB-1, API, Paketexporte und Feldpfad bleiben unveraendert.

## Bestandene Vertragsbereiche

### Fast-Mechanik

Die funktionalen Kernregeln sind widerspruchsfrei gebunden:

- endliche konfigurierbare Kapazitaet und feste Slotreihenfolge;
- getrennte auditive und visuelle normalisierte L1-Distanzen;
- gemeinsamer Match nur bei zwei bestandenen Modalitaetsschwellen;
- eindeutiger Matchrang aus Maximaldistanz, Distanzsumme und Slot-ID;
- getrennte komponentenweise Aktualisierung mit einem gebundenen Faktor;
- gesaettigter Support und schrittbasierter Ablauf;
- freie Slots vor LRU-Ersatz und eindeutiger LRU-Rang;
- atomarer Ersatz beider Modalitaeten.

Die Regeln reichen aus, um die mathematische Fast-Zustandsfortschreibung
festzulegen.

### Teilassoziationskonflikt

Ein Match nur einer Modalitaet darf keinen vorhandenen Slot einseitig
veraendern. Stattdessen entsteht eine neue gemeinsame Bindung oder bei voller
Kapazitaet ein atomarer gemeinsamer Ersatz. Diese Abgrenzung ist korrekt und
nicht zirkulaer.

### Konsolidierungsursprung und PPB-1

Konsolidierung ist auf `FAST_UPDATED` ab der Supportgrenze beschraenkt. Der
Vertrag erlaubt genau einen auditiven und einen visuellen PPB-1-Aufruf je
berechtigter aktueller Exposition. Als Eingaben sind ausschliesslich die zwei
aktuellen Originalframes erlaubt. Fast-Werte, alte Eintraege, Receipts,
Rekonstruktionen und Schleifen ueber Fast-Slots sind ausgeschlossen.

Die beiden bestehenden `advance_ppb1_bank`-Aufrufe sind rein. Deshalb kann
der Koordinator beide lokalen Ergebnisse pruefen, bevor ein Composite-
Nachzustand sichtbar wird. PPB-1 muss dafuer nicht geaendert werden.

### Ergebnis- und Abruftrennung

Kurzfristige Aufnahme, noch nicht bereite Aktualisierung,
Konsolidierungscommit und die zwei PPB-Stabilitaetsrollen sind fachlich
getrennt. Der read-only Abruf besitzt die eindeutige Prioritaet:

```text
beide PPB-Befunde positiv -> SLOW_PPB1_CONTEXT
sonst gemeinsamer Fast-Match -> FAST_ASSOCIATIVE_CONTEXT
sonst -> NO_COMPLETE_CONTEXT
```

Eine frische PPB-1-Bank erzeugt `SLOW_UNAVAILABLE` ohne unzulaessigen
S1-WU-Aufruf. Die Probe liefert keinen Nachzustand und keine Prototypwerte.

## Blocker 1: Quell- und Probehuellen fehlen in der Typenanatomie

S2-DE verwendet `TSPM1BoundExposure`, fuehrt diesen Typ aber nicht unter den
acht erlaubten privaten Typen. Fuer die kausal spaetere audiovisuelle Probe
wird lediglich eine "gebundene Probe" genannt; ein Typ, seine
Quellprojektion und sein Digestpayload fehlen vollstaendig.

Damit sind Konstruktoren, exakte Typpruefungen und die Unterscheidung von
Bildungs- und Probequellen nicht eindeutig implementierbar. Vor
Implementierung muessen mindestens `TSPM1BoundExposure` und
`TSPM1BoundProbe` mit kanonischen Feldern gebunden werden.

## Blocker 2: Gesamt-Konfigurationsbindung ist unvollstaendig

`TSPM1FastConfig` soll Traegerdimensionen aus zwei PPB-1-Konfigurationen
uebernehmen. Der Vertrag bindet jedoch keinen TSPM-1-Gesamtkonfigurationstyp,
der folgende Identitaeten atomar zusammenhaelt:

- Fast-Konfigurationsdigest;
- auditiver PPB-1-Konfigurationsdigest;
- visueller PPB-1-Konfigurationsdigest;
- Profilbinding- und Vertragsdigest;
- Modalitaet, Geometrie und Traegerinventare.

Ohne diese Huelle kann ein strukturell gueltiger Fast-Zustand mit anderen,
ebenfalls einzeln gueltigen PPB-1-Konfigurationen kombiniert werden. Die
spaetere Composite-Pruefung besitzt dafuer keine kanonische Sollidentitaet.

## Blocker 3: Owner und Aufrufflaeche sind nicht materialisiert

Der Owner hat Status und Lock, aber seine Autorisierungsfelder und seine
Bindung an genau einen Composite-Vorzustand und genau eine Exposition sind
nicht festgelegt. Ebenfalls fehlen:

- Owner-Snapshottyp und kanonischer Statuspayload;
- Erzeugungs- und Einmaligkeitsidentitaeten;
- genaue `consume_once`-Signatur;
- Initialzustandsfunktion und Fast-Uebergangssignatur;
- Composite-Generations- und Parentdigestpruefung;
- Fehlercodes und Prioritaet fuer Busy, Terminal, Quelle und Atomaritaet.

Damit kann das geforderte Retry-Verbot nicht eindeutig und gegen
Parallelaufrufe pruefbar implementiert werden.

## Blocker 4: Slot- und Receiptinvarianten sind mehrdeutig

Fuer freie und belegte Fast-Slots fehlen exakte Formbedingungen. Insbesondere
ist nicht gebunden, wann Support, letzte Auswahl, Konsolidierungszahl und
letzter Konsolidierungsexpositionsdigest `None`, `0` oder positiv sein
muessen und wie sie bei Erzeugung, nicht bereitem Match, Commit, Ablauf und
Ersatz fortgeschrieben werden.

Ablauf kann mehrere Slots in demselben Schritt freigeben und gleichzeitig
mit `FAST_CREATED`, `FAST_UPDATED` oder `FAST_REPLACED` auftreten.
`FAST_EXPIRED` steht dennoch in derselben Ereignismenge wie diese
Primaerereignisse. Es fehlt die verbindliche Trennung zwischen:

- genau einem Primaerereignis;
- optionalem `PARTIAL_ASSOCIATION_CONFLICT`-Flag;
- geordneter Menge abgelaufener Slotdigests;
- optionalem ersetztem Slotdigest;
- genau einem Konsolidierungsstatus.

Ohne diese Trennung sind Receiptkonstruktion und Digestpayload nicht
eindeutig.

## Blocker 5: Originalobjekt- und Probeaufrufbindung ist nicht exakt

Der Vertrag verbietet rekonstruierte Frames, legt aber nicht fest, wie die
Implementierung beweist, dass die an PPB-1 uebergebenen Objekte exakt die in
den beiden Timed-Frame-Bindings enthaltenen `frame`-Objekte sind. Eine reine
Werte- oder Digestgleichheit wuerde auch eine Rekonstruktion akzeptieren.

Fuer den S1-WU-Abruf fehlen ausserdem die zwei deterministisch aus dem
Probequellendigest abgeleiteten `probe_id`-Rollen. Extern gewaehlt duerfen
diese IDs keine verdeckte Auswahl- oder Ergebnisinformation tragen.

## Nichtzirkularitaetsbefund

Die vorgesehene Informationsrichtung ist nicht zirkulaer:

```text
aktuelle Originalexposition -> Fast-Schritt -> Berechtigung
-> aktuelle Originalexposition -> unveraendertes PPB-1
```

Weder PPB-Readout noch spaetere Probe bestimmen rueckwirkend den Fast-Match
oder die Berechtigung. Dieser Befund besteht. Die fehlenden Quelltypen und
Objektidentitaetsregeln verhindern jedoch noch den statischen Nachweis, dass
eine spaetere Implementierung diese Richtung zwingend einhalten muss.

## Entscheidung

S2-DF besteht nicht. Die funktionale Architektur ist konsistent, aber der
Vertrag ist noch nicht eindeutig materialisierbar:

`BLOCK_TSPM1_IMPLEMENTATION_FIVE_STATIC_MATERIALIZATION_BINDINGS_OPEN`

Es liegt kein fachlicher Stopp von TSPM-1 vor. Die fuenf Blocker betreffen
ausschliesslich Typ-, Quellen-, Owner-, Receipt- und Aufrufbindung. Private
Implementierung und synthetische Tests bleiben gesperrt.

## Naechster Schritt

S2-DG darf ausschliesslich als statische Vertragskorrektur die fuenf offenen
Bindungen schliessen. Es darf noch keinen Code, Test, Zustandsaufruf oder
Feldpfad erzeugen. Danach ist ein erneuter statischer Implementierungspreflight
erforderlich.

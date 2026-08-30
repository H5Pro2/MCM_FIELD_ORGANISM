# S2-GH: Korrigierte Grenze der A/B-Projektion

## Auftrag

S2-GH korrigiert die Projektionsgrenze fuer den privaten
Zwei-Bereich-Kontextverbraucher. Verlustfreiheit gilt kuenftig fuer alle im
qualifizierten S2-GC-Bundle vorhandenen oeffentlichen Kontextinformationen,
nicht fuer interne Speicherzustaende oder historische Forschungsevidenz, die
dieses Bundle bewusst nicht ausgibt.

Der einzige spaetere Eingang lautet wieder:

```text
validiertes S2-GC PerceptualContextBundle
```

Es gibt keinen S2-FS-Sidecar, keine dritte Belegquelle und keine
Rekonstruktion aus S2-FZ-Erwartungen.

## Vertragskorrektur und historische Einordnung

S2-GH aendert folgende Grenzen ausdruecklich:

1. Die S2-GD-Forderung, instabile Slow-Supports in der A/B-Kontextprojektion
   zu erhalten, wird fuer diese Schnittstelle aufgehoben.
2. Der in S2-GF gebundene kombinierte Bundle-/Finding-Eingang wird fuer die
   A/B-Kontextprojektion nicht weiterverfolgt.
3. S2-GG bleibt als korrekter Materialisierungsstopp dieses kombinierten
   Diagnoseeingangs erhalten.
4. S2-GC, S2-FS, das Drei-Rollen-Bundle und ihre Befunde bleiben technisch
   unveraendert.
5. S2-FZ bleibt die unabhaengige Forschungs- und Diagnoseevidenz fuer den
   Unterschied zwischen stabilisiertem Support `3` und instabilem Support
   `1`.

Damit wird S2-GD nicht still uminterpretiert. Seine zu starke
Verlustfreiheitsforderung wird durch S2-GH fuer den Kontextverbraucher
explizit ersetzt.

## Gebundene Grundlage

Technischer Ausgangsstand:

`be4f312080b2be668c6b82942adb9122a7e650d1`

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| Qualifiziertes S2-GC-Bundle | `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| S2-GC-Qualifikation | `docs/S2GC_EINMALIGE_BUNDLE_WIEDERHOLUNGSQUALIFIKATION.md` | `2b94ba7f830588202aeea6c815b1f8d7fc73eada5ca2500b944ee287f2b435b8` |
| Urspruenglicher Zwei-Bereich-Vertrag | `docs/S2GD_STATISCHER_ZWEI_BEREICH_ABBILDUNGS_MIGRATIONS_UND_FALSIFIKATIONSVERTRAG.md` | `f55afa69782275b6697841ac24d3d03d7a8a256f2fd993e78f53825c582ea7e2` |
| Nicht weiterverfolgter kombinierter Eingang | `docs/S2GF_STATISCHER_VERTRAG_VALIDATED_TWO_AREA_PROJECTION_INPUT.md` | `b482a1e2784359cf076ee141c4a502b03630a61d121ee01e99df014741549df0` |
| Materialisierungsstopp des kombinierten Eingangs | `docs/S2GG_STATISCHER_MATERIALISIERBARKEITSAUDIT_VALIDATED_TWO_AREA_PROJECTION_INPUT.md` | `3e6f78d0cf59cf6a78a997df11afb49e9eca487d83db1c3b377e40f552b362d9` |

## Begriff der oeffentlichen Kontextinformation

"Oeffentlich" bezeichnet in S2-GH ausschliesslich die sichtbaren Felder der
spaeteren privaten Kontextschnittstelle. Es bedeutet keine oeffentliche
Projekt-API und keine Produktionsintegration.

Funktional zu erhalten sind alle im S2-GC-Bundle vorhandenen Informationen:

- Bundle-, Vertrags-, Binding-, Konfigurations-, Composite-Zustands-, Probe-
  und Quelldigest;
- identische Vor- und Nachzustandsdigests;
- Rollenstatus und Abwesenheitsgrund fuer `B4_RECENT`, `TSPM_FAST` und
  `TSPM_SLOW`;
- vorhandene Kandidaten und ihre Komponenten;
- reduzierte Werte, Quellenidentitaet und Quelldigest;
- native und funktionale Distanzen, soweit im Bundle vorhanden;
- vorhandener Support, Stabilitaet, letzter Auswahlschritt und
  B4-Bildungsindex;
- B4-Kurzfolgenstatus und alle vorhandenen Folgenreferenzen;
- Ressourcenledger;
- `automatic_selection = None`.

Nicht Teil dieser Schnittstelle sind:

- nicht ausgewaehlte B4-, Fast- oder Slow-Slots;
- instabile Slow-Supports, die das Bundle nicht als Kandidat ausgibt;
- vollstaendige interne Bank- oder Fast-Zustaende;
- Konsolidierungsreceipts und historische Formationsfolgen;
- S2-FZ-Fixture-IDs, Sollwerte oder Recorderereignisse.

Das Weglassen dieser Diagnoseinformationen ist keine funktionale
Verluststelle der Kontextprojektion, weil sie nicht zum zugelassenen Eingang
gehoeren.

## Exakte Zwei-Bereich-Abbildung

Die spaetere Projektion erzeugt exakt zwei oeffentliche Bereichsbefunde in
kanonischer Reihenfolge:

```text
A_RECENT
B_STABLE
```

Die Reihenfolge dient nur der deterministischen Serialisierung und ist keine
Prioritaet.

### `A_RECENT`

`A_RECENT` enthaelt drei getrennte interne Teilrollen:

1. `recent_content`: unveraenderte Referenz auf das Rollenfinding
   `B4_RECENT`;
2. `fast_internal`: unveraenderte Referenz auf das Rollenfinding
   `TSPM_FAST`;
3. `short_sequence`: unveraenderter B4-Kurzfolgenbefund des Bundles.

Dabei gilt:

- B4 und Fast werden weder verschmolzen noch dedupliziert;
- gleiche Werte aus beiden Quellen bleiben getrennt;
- Fast ist keine dritte oeffentliche Memory-Ebene;
- nur B4 darf `formation_index` und Kurzfolgenreferenzen tragen;
- A erzeugt keine neue Auswahl zwischen B4 und Fast;
- `ABSENT_VALID` bleibt mit demselben Abwesenheitsgrund erhalten.

### `B_STABLE`

`B_STABLE` bildet ausschliesslich das Rollenfinding `TSPM_SLOW` ab:

- `AVAILABLE_COMPLETE`: beide vorhandenen stabilen Slow-Komponenten;
- `AVAILABLE_PARTIAL`: genau die vorhandene stabile Modalitaet;
- `ABSENT_VALID`: kein Kandidat und unveraenderter Abwesenheitsgrund.

Auditive und visuelle Komponenten bleiben getrennt. Ohne gespeicherte
Relationsidentitaet bleibt
`CROSS_MODAL_RELATION_NOT_REPRESENTED` unveraendert. B enthaelt keine
Reihenfolge, keinen B4-Index und keine Fast-Position.

Bei `NO_STABLE_SLOW_MATCH` lautet die A/B-Ausgabe ausschliesslich:

```text
B_STABLE.status = ABSENT_VALID
B_STABLE.absence_reason = NO_STABLE_SLOW_MATCH
B_STABLE.candidate = None
```

Es werden weder Support `1` noch ein anderer Support, Slot oder eine Ursache
hinzuerfunden.

## S2-FZ bleibt unabhaengige Diagnoseevidenz

S2-FZ bestaetigt fuer seine gebundene Geschichte:

- P1 mit auditivem und visuellem Support `3`, stabil und spaeter abrufbar;
- P2 mit auditivem und visuellem Support `1`, instabil und spaeter nicht
  abrufbar.

Die A/B-Kontextprojektion muss diesen Versuch nicht erneut rekonstruieren.
Sie bildet nur den jeweils vorhandenen S2-GC-Kontextbefund ab:

- ein vorhandener stabiler P1-Kandidat kann nach `B_STABLE` gelangen;
- ein fuer die aktuelle Probe nicht vorhandener stabiler P2-Kandidat bleibt
  `ABSENT_VALID`.

Die Aussage ueber P2-Support `1` verbleibt im S2-FZ-Befund. Sie wird weder
geloescht noch in die Kontextschnittstelle kopiert.

## Vorgesehene private Datenrollen

Eine spaetere Implementierung darf ausschliesslich folgende neue
unveraenderliche Rollen materialisieren:

1. `AreaARecentFinding` mit B4-, Fast- und Kurzfolgenfindingdigest;
2. `AreaBStableFinding` mit dem unveraenderten Slow-Rollenfinding;
3. `TwoAreaContextResourceLedger` fuer Eingangsvalidierung, zwei
   Rollenprojektionen, Digests und Ausgabe;
4. `TwoAreaContextBundle` mit genau zwei Bereichsfindings,
   Vor-/Nachzustandsdigest und `automatic_selection = None`.

Die vorhandenen S2-GC-Kandidaten und Komponenten sollen referenziert oder
unveraendert eingebettet werden. Sie duerfen nicht neu berechnet oder unter
neuen Distanz- oder Matchregeln erzeugt werden.

## Eingangsvalidierung

Vor jeder Projektion muss gelten:

1. exakter privater Typ `PerceptualContextBundle`;
2. korrektes S2-GC-Schema und gebundener S2-GA-Vertragsdigest;
3. kanonisch gueltiger Bundledigest;
4. exakt drei Rollen in der Reihenfolge `B4_RECENT`, `TSPM_FAST`,
   `TSPM_SLOW`;
5. gueltige Rollenfinding- und Kandidatendigests;
6. gueltige Komponentenformen, Dimensionen und Digests;
7. gueltiger Kurzfolgenfindingdigest mit hoechstens neun Referenzen;
8. gueltiges S2-GC-Ressourcenledger;
9. `prestate_digest == poststate_digest == composite_state_digest`;
10. `automatic_selection is None`;
11. hoechstens drei bestehende Kandidaten und vier Komponenten;
12. keine unbekannten, doppelten oder zusaetzlichen Rollen.

Die Projektion darf keine Speicher-, Probe-, Match-, Distanz- oder
Fortschreibungsfunktion aufrufen. Sie validiert und ordnet nur bereits im
Bundle vorhandene, digestgebundene Daten.

## Determinismus und Ressourcen

Die A/B-Projektion ist endlich begrenzt:

- genau zwei oeffentliche Bereiche;
- hoechstens die drei vorhandenen S2-GC-Kandidaten;
- hoechstens die vier vorhandenen Komponenten;
- hoechstens 78 vorhandene reduzierte Werte;
- hoechstens neun vorhandene B4-Folgenreferenzen;
- keine zweite Wertekopie, sofern unveraenderliche Referenzen genuegen;
- keine Historie und keine neue Memory-Kapazitaet.

Das neue Ledger zaehlt mindestens:

- Bundle-, Rollen-, Kandidaten-, Komponenten- und Sequenzvalidierungen;
- zwei Bereichsprojektionen;
- referenzierte Kandidaten, Komponenten, Werte und Folgenreferenzen;
- validierte und neu gebildete Digests;
- Ausgabefelder.

Bei identischem Bundle muessen Payload, Ledger und Ergebnisdigest bytegleich
sein. Zeit, Zufall, Prozessidentitaet oder Dictionary-Reihenfolge duerfen das
Ergebnis nicht beeinflussen.

## Fail-Closed- und Falsifikationsregeln

Keine A/B-Ausgabe entsteht bei:

- beschaedigtem oder fremdem Bundledigest;
- Rollenverlust, Rollenverdopplung oder falscher Rollenreihenfolge;
- abweichendem Kandidaten-, Komponenten-, Quellen- oder Wertedigest;
- ungueltiger Dimension oder Ressourcenueberschreitung;
- B4-Kurzfolge ausserhalb von `A_RECENT`;
- Slow-Reihenfolge oder B4-Bildungsindex in `B_STABLE`;
- Fast als drittem oeffentlichen Bereich;
- Verschmelzung gleicher B4- und Fast-Inhalte;
- stabilem B-Kandidaten bei `ABSENT_VALID`;
- erfundenem Support, Slot oder Distanz bei `NO_STABLE_SLOW_MATCH`;
- automatischer Auswahl, Rangfolge oder Gesamtwertung;
- veraendertem Vor-/Nachzustandsdigest;
- Speicher-, Probe-, Rekonstruktions-, Kontextnutzungs- oder Feldaufruf;
- unvollstaendigem Ressourcenledger.

Die Projektion ist funktional falsifiziert, wenn irgendeine im S2-GC-Bundle
sichtbare Kontextinformation in A/B fehlt oder veraendert erscheint. Sie ist
nicht dadurch falsifiziert, dass interne, vom Bundle nicht bereitgestellte
Diagnoseevidenz fehlt.

## Ausgeschlossene Richtungen

S2-GH erlaubt nicht:

- Wiederaufnahme des kombinierten S2-GF-Eingangs fuer diese Projektion;
- Erweiterung oder Neuqualifikation des S2-GC-Bundles;
- neue S2-FS-Belege oder Speicherabfragen;
- Rekonstruktion instabiler Supports;
- physische Zusammenlegung von B4 und Fast;
- A-nach-B-Zustandsuebertragung;
- Kontextverwendung, automatische Auswahl oder Feldrueckwirkung;
- API-, Snapshot- oder Produktionsintegration.

Eine detailliertere prospektive Konsolidierungsevidenz kann spaeter fuer eine
neue Forschungsfrage definiert werden. Sie ist keine Voraussetzung dieser
Kontextschnittstelle.

## Entscheidung

Die korrigierte A/B-Projektion ist statisch materialisierbar, weil alle fuer
sie erforderlichen oeffentlichen Informationen bereits kanonisch im
qualifizierten S2-GC-Bundle vorliegen. Die zuvor festgestellte
Nichtmaterialisierbarkeit des kombinierten Diagnoseeingangs bleibt korrekt,
ist fuer diese enger definierte Funktion aber nicht mehr entscheidend.

S2-GH-Abschluss:

`PASS_S2GH_STATIC_FUNCTIONALLY_LOSSLESS_DIAGNOSTICALLY_BOUNDED_AB_PROJECTION_CONTRACT_BOUND`

Eine Implementierung, die 14 Tests und ein `unittest`-Aufruf benoetigen eine
neue ausdrueckliche Freigabe. Der spaetere Kontextnutzen bleibt danach
getrennt gegen `CURRENT_PERCEPTION_ONLY` zu kontrahieren.

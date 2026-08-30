# S2-GF: Vertrag fuer ValidatedTwoAreaProjectionInput

## Auftrag und Status

S2-GF korrigiert ausschliesslich die statische Eingangsgrenze der spaeteren
A/B-Schattenprojektion. Der kombinierte Eingang bindet ein unveraendertes,
validiertes S2-GC-Bundle an genau den validierten S2-FS-read-only-Befund, aus
dem es erzeugt wurde.

```text
ValidatedTwoAreaProjectionInput
= validiertes S2-GC PerceptualContextBundle
+ exakt zugehoeriger validierter S2-FS B4TSPM1ReadOnlyFinding
+ vollstaendige relationale Quellen-, Owner- und Digestbindung
```

S2-GF implementiert und prueft diesen Eingang noch nicht. S2-GE bleibt bis zu
einem bestandenen separaten Materialisierbarkeitsaudit gesperrt.

## Gebundene Grundlage

Technischer Ausgangsstand:

`385877e22c14eb7af364ae83169f693d6311e215`

| Rolle | Quelle | SHA-256 |
| --- | --- | --- |
| S2-GC-Bundle und Projektionsbindung | `tools/_s2gb_private_perceptual_context_bundle.py` | `0fba7b0323fe772c481eb5261b9640e4a5b00d7da3ceb1a7e0f81c6d9f54bf49` |
| S2-FS-read-only-Befund | `tools/_s2fs_b4_tspm1_private_coordinator.py` | `95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0` |
| Zwei-Bereich-Vertrag | `docs/S2GD_STATISCHER_ZWEI_BEREICH_ABBILDUNGS_MIGRATIONS_UND_FALSIFIKATIONSVERTRAG.md` | `f55afa69782275b6697841ac24d3d03d7a8a256f2fd993e78f53825c582ea7e2` |
| Festgestellte Eingangsluecke | `docs/S2GE_MATERIALISIERUNGSSTOPP_INSTABILE_SLOW_EVIDENZ.md` | `421b888da2f958f59d7dc231ed30dedf0dc576b7b0d3e8784b043dee0657ef3a` |

Das S2-GC-Bundle, sein Schema und seine Qualifikation bleiben unveraendert.
Der S2-FS-Befund wird nicht zu einem zusaetzlichen Memory-Bereich.

## Autoritaetsgrenzen

### S2-GC-Bundle

Das Bundle ist alleinige Autoritaet fuer:

- die drei vorhandenen Rollenbefunde;
- oeffentliche Kandidaten und gueltige Abwesenheit;
- Kandidatenwerte, Distanzen, Supports und Quellen, soweit sie im Bundle
  vorhanden sind;
- B4-Kurzfolge;
- die spaetere Zuordnung von B4 und Fast zu `A_RECENT`;
- die spaetere Zuordnung stabiler Slow-Kandidaten zu `B_STABLE`;
- die Abwesenheit automatischer Auswahl.

Der Zusatzbefund darf keinen dieser Werte ersetzen, ergaenzen oder
ueberstimmen.

### S2-FS-read-only-Befund

Der S2-FS-Befund darf ausschliesslich die im Bundle fehlende interne
Slow-Stabilisierungsevidenz bereitstellen:

- Modalitaet;
- Bank- und Slotidentitaet;
- Prototypwertedigest und reduzierte Prototypwerte;
- Support;
- Stabilitaet;
- letzter Auswahlschritt;
- native Distanz;
- Bank- und Zustandsdigest.

Nur Slots mit `stable == False` duerfen ueber diesen Zusatzweg in die interne
`stabilization_evidence` gelangen. Sie erzeugen niemals einen
`B_STABLE`-Kandidaten, veraendern keine Verfuegbarkeit und beeinflussen keine
Auswahl oder Rangfolge.

Stabile Slow-Befunde des S2-FS-Findings dienen ausschliesslich dem relationalen
Abgleich mit dem Bundle. Sie duerfen nicht als zweite Kandidatenquelle
projiziert werden.

## Statische Datenanatomie

### `S2GFSourceRelationBinding`

Die vollstaendige relationale Bindung muss die bereits vorhandene
`PerceptualContextProjectionBinding` inhaltlich erhalten:

- Konfigurationsdigest;
- Composite-Zustandsdigest;
- Probendigest und Probe-Wertedigest;
- auditive und visuelle Quelldigests;
- auditive und visuelle Geometrieidentitaet;
- gemeinsame Clock-Identitaet;
- Start und Ende des gebundenen Zeitfensters;
- Quelldigest und Projektions-Bindingdigest.

Diese Rolle ist keine dritte Evidenzquelle. Sie ist der vorhandene technische
Nachweis, mit dem das Bundle bereits an Quelle, Probe und Zeit gebunden wurde.
Ohne seine exakten Felder kann der im Bundle gespeicherte `binding_digest`
nicht unabhaengig validiert werden.

### `S2GFCombinedInputOwner`

Bundle und read-only Finding besitzen selbst keine historische Owner-ID. S2-GF
darf deshalb keine Gleichheit frueherer Erzeuger-Owner behaupten.

Stattdessen bindet ein neuer privater Einmal-Owner genau die kombinierte
Validierung:

- `owner_id`, `authorization_id`, `consumption_id`;
- autorisierter Bundle-, Finding-, Quellenrelations- und
  Sequenzevidenzdigest;
- Status `AUTHORIZED`, `CONSUMED` oder `FAILED`;
- genau ein Versuch und hoechstens ein erfolgreicher Verbrauch;
- kein Teilresultat bei Fehler;
- Wiederverwendung immer fail-closed.

"Identischer Owner" bedeutet in S2-GF damit: Genau derselbe prospektiv
autorisierte Einmal-Owner verantwortet die gesamte Bundle-/Finding-Paarung.
Es bedeutet nicht, dass nicht vorhandene historische Ownerfelder
nachtraeglich rekonstruiert werden.

### `ValidatedTwoAreaProjectionInput`

Der kombinierte Eingang enthaelt genau:

1. ein exaktes `PerceptualContextBundle`;
2. ein exaktes `B4TSPM1ReadOnlyFinding`;
3. eine exakte `S2GFSourceRelationBinding`;
4. die aus dem Bundle kanonisch rekonstruierbare
   `ValidatedB4ShortSequenceEvidence`-Identitaet;
5. den autorisierten Owner-Vorzustandsdigest;
6. einen eigenen `relation_digest`;
7. einen eigenen `validated_input_digest`;
8. kein Ergebnis, keinen A/B-Kandidaten und keinen Memory-Zustand.

Die Sequenzevidenz darf nur aus Status, Referenzdigests, beobachtetem
B4-Zustandsdigest, Probendigest und dem bereits im Bundle gespeicherten
`source_evidence_digest` validiert werden. Sie darf nicht aus einem Recorder
oder Versuchsplan ersetzt werden.

## Verbindliche relationale Pruefreihenfolge

Die spaetere Validierung muss vor jeder A/B-Projektion in dieser Reihenfolge
vollstaendig erfolgreich sein:

1. exakte private Typen, Schemas und statische Vertragsdigests;
2. autorisierter, noch unverbrauchter kombinierter Owner;
3. kanonischer Bundle- und Bundledigest;
4. kanonischer S2-FS-Finding- und Findingdigest;
5. vollstaendige `S2GFSourceRelationBinding` und ihr Digest;
6. identischer Konfigurationsdigest in Bundle und Quellenrelation;
7. identischer Composite-Zustandsdigest in Bundle, Finding und
   Quellenrelation;
8. `prestate_digest == poststate_digest == composite_state_digest` fuer
   Bundle und Finding;
9. identischer Probendigest in Bundle, Finding, Quellenrelation und
   Sequenzevidenz;
10. B4-Probewertedigest des Findings identisch zur Quellenrelation;
11. B4-Zustandsdigest des Findings identisch zum beobachteten
    Sequenzzustandsdigest des Bundles;
12. Rollenmenge des Findings exakt `B4_RECENT`, `TSPM_FAST`, `TSPM_SLOW`;
13. vollstaendiger B4-Kandidaten- oder Abwesenheitsabgleich;
14. vollstaendiger Fast-Kandidaten- oder Abwesenheitsabgleich;
15. vollstaendiger stabiler Slow-Kandidaten- oder Abwesenheitsabgleich je
    Modalitaet;
16. Erhebung ausschliesslich der verbleibenden instabilen Slow-Slots als
    interne Pruefevidenz;
17. Eindeutigkeit aller Bank-, Slot-, Quellen- und Komponentendigests;
18. vollstaendige Eingangs-, Relations- und Ressourcenbilanz;
19. atomare Ownerentscheidung und erst danach Veroeffentlichung genau eines
    validierten kombinierten Eingangs.

Ein Fehler in einer frueheren Stufe stoppt die spaeteren Stufen. Es entsteht
weder ein Teilinput noch eine leere Ersatzprojektion.

## Rollenabgleich im Detail

### B4

Wenn das Bundle `B4_RECENT` als verfuegbar meldet, muss sein Kandidat exakt
dem ausgewaehlten B4-Befund des Findings entsprechen:

- Slotidentitaet;
- 26 reduzierte AV-Werte und Wertedigest;
- auditive und visuelle Distanz;
- tatsaechlicher Bildungsindex;
- aus B4-Zustand, Slot, Index und Werten abgeleiteter Quelldigest.

Meldet das Bundle `ABSENT_VALID`, darf das Finding keinen funktional
ausgewaehlten B4-Kandidaten besitzen. B4-Folgenreferenzen muessen weiterhin
vollstaendig gegen die aktuell belegten B4-Quellen pruefbar sein.

### Fast

Wenn das Bundle `TSPM_FAST` als verfuegbar meldet, muessen Slot, gemeinsame
26 AV-Werte, beide Distanzen, Support, letzter Auswahlschritt und aus dem
Fast-Slotdigest abgeleiteter Quelldigest exakt dem Finding entsprechen.

Bei `ABSENT_VALID` darf das Finding keinen funktional ausgewaehlten Fast-Slot
enthalten. Der Zusatzbefund darf keinen anderen Fast-Slot auswaehlen.

### Slow stabil

Jede stabile Bundlekomponente muss genau einem funktional erkannten,
stabilen Slow-Befund derselben Modalitaet entsprechen. Abzugleichen sind:

- Modalitaet, Bank und Slot;
- Prototypwerte und Wertedigest;
- Support, Stabilitaet und letzter Auswahlschritt;
- native und funktional uebernommene Distanz;
- Bankzustands- und Komponentenquelldigest.

Bei `AVAILABLE_PARTIAL` darf genau eine Modalitaet diesen Abgleich bestehen.
Bei `AVAILABLE_COMPLETE` muessen beide bestehen. Der S2-FS-Befund darf keine
zusatzliche stabile oeffentliche Komponente erzeugen.

### Slow instabil

Nach vollstaendig bestandenem oeffentlichem Abgleich duerfen aus den beiden
Slow-Bankfindings alle belegten Slots mit `stable == False` als interne
Pruefevidenz uebernommen werden. Fuer jeden Slot werden die vorhandenen Werte
und Digests unveraendert gebunden. Es erfolgt:

- keine Distanzneuberechnung;
- keine neue Matchentscheidung;
- keine Auswahl eines "besten" instabilen Slots;
- keine Ableitung eines erwarteten Supports;
- keine Projektion nach `B_STABLE`;
- keine Aenderung des Bundle-Abwesenheitsstatus.

Damit kann ein tatsaechlich vorhandener Support `1` erhalten werden, ohne ihn
aus `NO_STABLE_SLOW_MATCH` oder der S2-FZ-Erwartung abzuleiten.

## Digestbeziehung

Der `relation_digest` muss mindestens kanonisch binden:

```text
S2-GF-Schema und Vertragsdigest
Bundle-Digest
S2-FS-Findingdigest
S2-GB-Projektions-Bindingdigest
Bundle-Rollenfindingdigests
B4-Sequenzfinding- und Sequenzevidenzdigest
S2-FS-Ressourcenledgerdigest
Composite-, Probe- und Quelldigest
stabile Komponentenabgleichdigests
instabile Slow-Slotdigests
Owner-Autorisierungs-Vorzustandsdigest
```

Der `validated_input_digest` bindet anschliessend den `relation_digest`, den
terminalen Owner-Nachzustandsdigest und das vollstaendige neue
Ressourcenledger. Keine Digestrolle darf sich selbst direkt oder indirekt
enthalten.

## Ressourcen- und Kapazitaetsgrenze

Der kombinierte Eingang fuehrt keine neue Memory-Kapazitaet ein. Sein Ledger
zaehlt getrennt:

- Bundle- und Findingvalidierung;
- Quellen-, Probe-, Zustand- und Sequenzabgleich;
- drei Rollenabgleiche;
- stabile Komponentenabgleiche;
- Anzahl validierter instabiler Slow-Slots;
- validierte Werte und Digests;
- Owner-, Relations-, Ausgabe- und Ledgerarbeit.

Obergrenzen stammen ausschliesslich aus den bereits validierten B4-, Fast-
und beiden PPB-Bankformen. Der Vertrag darf keine zusaetzlichen Slots,
Kandidaten oder Werte zulassen. Mehrdeutige, doppelte oder ueberzaehlige
Evidenz stoppt fail-closed.

## Fail-Closed-Grenzen

Kein `ValidatedTwoAreaProjectionInput` entsteht bei:

- fehlendem Bundle oder Finding;
- fremdem Bundle-, Finding-, Quellenrelations- oder Sequenzevidenzdigest;
- abweichender Probe, Konfiguration, Quelle, Geometrie, Clock oder Zeitlage;
- abweichendem Composite-, B4-, Fast- oder Slow-Zustandsbezug;
- veraendertem Vor-/Nachzustand;
- fehlender, doppelter, vertauschter oder unbekannter Rolle;
- stabilem Bundlekandidaten ohne identischen stabilen Findingbeleg;
- instabilem Slot, der einen B-Kandidaten oder Verfuegbarkeitswechsel
  erzeugt;
- falscher Modalitaet, Dimension, Distanz, Support- oder Stabilitaetsangabe;
- duplizierter Bank-, Slot-, Quellen- oder Komponentenevidenz;
- unbekanntem, verbrauchtem oder widerspruechlichem Owner;
- unvollstaendigem Ledger oder Ressourcenueberschreitung;
- Label-, Sollwert-, Recorder- oder Erwartungswissen;
- irgendeiner Speicher-, Probe-, Fortschreibungs- oder Feldfunktion.

Fehler erzeugen nur einen privaten terminalen Fehlerbeleg mit Fehlercode,
Owner und Eingangsbelegdigest. Sie erzeugen keinen leeren Ersatzinput.

## Materialisierbarkeitsaudit vor S2-GE

Ein separater statischer Audit muss mindestens klaeren:

1. ob alle Felder der Quellenrelation aus vorhandenen S2-GB-Belegen
   materialisierbar sind;
2. ob Bundle- und Findingbezug ohne erneute Speicherabfrage eindeutig
   validiert werden koennen;
3. ob B4-, Fast- und stabile Slow-Rueckprojektionen vollstaendig sind;
4. ob alle instabilen Slow-Slots endlich und eindeutig erfassbar sind;
5. ob die neue Ownerrolle nur die Paarvalidierung kontrolliert und keinen
   historischen Owner vortaeuscht;
6. ob Relation, Owner und Ledger nichtzirkulaer digestierbar sind;
7. ob exakt ein Finding je Bundle zulaessig bleibt;
8. ob die spaetere A/B-Projektion weiterhin genau zwei oeffentliche Bereiche
   ausgeben kann.

Erst bei bestandenem Audit darf die S2-GE-Implementierungsfreigabe erneut
erteilt werden. Die fruehere S2-GE-Freigabe bleibt durch den dokumentierten
Materialisierungsstopp geschlossen.

## Claim- und Funktionsgrenze

Der kombinierte Eingang ist ein privater Herkunfts- und Validierungsbeleg. Er
ist:

- keine dritte Memory-Ebene;
- kein neuer Kandidat;
- keine Speicherfunktion;
- keine physische A-nach-B-Migration;
- keine Kontextauswahl;
- keine Feldwirkung.

Ein spaeter bestandener S2-GE-Schritt darf nur eine technisch verlustfreie
read-only Zwei-Bereich-Schattenprojektion bestaetigen. Der Nutzen von
`CURRENT_PERCEPTION_PLUS_TWO_AREA_CONTEXT` bleibt danach separat zu
kontrahieren und zu pruefen.

## S2-GF-Abschluss

Der korrigierte kombinierte Eingang ist statisch widerspruchsfrei gebunden,
sofern die Ownergleichheit prospektiv als gemeinsamer Einmal-Owner der
Belegpaarung verstanden wird. Eine historische Ownergleichheit ist aus den
bestehenden read-only Artefakten nicht belegbar und wird nicht behauptet.

Status:

`PASS_S2GF_STATIC_COMBINED_INPUT_SOURCE_ROLE_AND_DIGEST_CONTRACT_BOUND`

Noch nicht freigegeben sind Materialisierungsaudit, Implementierung, Tests,
Ausfuehrung, A/B-Projektion, Kontextverwendung und Feldintegration.

# S1-NZ G2/D3 transiente Zweiintervallanatomie, Ereignisalphabet und Commitgrenze

## Status

S1-NZ bindet ausschliesslich die transiente Anatomie des in S1-NY
ausgewaehlten lokalen Fortsetzungsvergleichs. Gebunden werden Eingangsrollen,
Ereignisalphabet, atomare Commitgrenze, verbotener Persistenzrest und die
konservative D3-Zielprojektion. Der Schritt waehlt keine Umordnungsmenge,
Rate, Schwelle oder Bildungsgleichung und fuehrt nichts aus.

Entscheidung:

```text
G2_D3_TRANSIENT_TWO_INTERVAL_EVENT_ANATOMY_AND_COMMIT_BOUND
```

## Transiente lokale Grenzfigur

Die Vergleichseinheit existiert nur waehrend genau einer atomaren Grenze
zwischen zwei lokalen Kontaktintervallen derselben Kante. Sie besitzt:

```text
current_edge_id
current_field_reference_digest
current_interval_ordinal
current_orientation in {X,Y}
current_interval_closed = true

optional prior_edge_id
optional prior_field_reference_digest
optional prior_interval_ordinal
optional prior_orientation in {X,Y}
optional prior_interval_closed = true
```

Die Rollen werden aus bereits abgeschlossenen reduzierten lokalen
Feldkontakten gelesen. Rohdaten, Rezeptorarrays, S/H-Folgen und Medieninhalte
sind nicht Teil der Grenzfigur.

Die Grenzfigur ist kein D3-Feld und kein persistenter Kandidatenzustand. Sie
wird dem atomaren Vergleich vollstaendig uebergeben und darf nicht in einer
spaeteren Feldzeit erneut gelesen werden.

## Gueltige Intervallnachbarschaft

### Erster Kontakt

Nur beim ersten Intervall einer frischen unabhaengigen Geschichte gilt:

```text
current_interval_ordinal = 0
all prior fields = absent
```

### Folgende Kontakte

Bei vorhandenem Vorgaenger muessen exakt gelten:

```text
current_interval_ordinal = prior_interval_ordinal + 1
prior_interval_closed = true
current_interval_closed = true
prior_edge_id = current_edge_id
prior_field_reference_digest = current_field_reference_digest
```

Uebersprungene, doppelte, rueckwaerts laufende oder nur teilweise
abgeschlossene Intervalle sind ungueltig. Kontakte verschiedener Kanten oder
Feldreferenzen duerfen nicht verglichen werden.

Eine Arm-ID, H0-/H1-Kennung oder Gesamtlaenge der Geschichte ist weder
erforderlich noch zulaessig.

## Endliches Ereignisalphabet

Die Klassifikation besitzt genau drei gueltige Rollen:

```text
NO_PREDECESSOR
LOCAL_CONTINUATION
LOCAL_SWITCH
```

Vollstaendige Tabelle:

| Vorgaenger | Aktuell | Ereignis |
|---|---|---|
| absent | X | `NO_PREDECESSOR` |
| absent | Y | `NO_PREDECESSOR` |
| X | X | `LOCAL_CONTINUATION` |
| Y | Y | `LOCAL_CONTINUATION` |
| X | Y | `LOCAL_SWITCH` |
| Y | X | `LOCAL_SWITCH` |

Es gibt kein Ereignis fuer ein bestimmtes X- oder Y-Label. Nur Gleichheit
gegen Wechsel ist relevant. Unbekannte Orientierungen oder ungueltige
Nachbarschaften erzeugen keinen vierten Sachwert, sondern einen
Fail-Closed-Abbruch.

## Gebundene Ereignismuster der F2-Geschichten

Einschliesslich des ersten Kontakts ergeben sich exakt:

```text
H0_ALTERNATING
= NO_PREDECESSOR, LOCAL_SWITCH, LOCAL_SWITCH, LOCAL_SWITCH

H1_GROUPED
= NO_PREDECESSOR, LOCAL_CONTINUATION, LOCAL_SWITCH, LOCAL_CONTINUATION

H1_MIRRORED
= NO_PREDECESSOR, LOCAL_CONTINUATION, LOCAL_SWITCH, LOCAL_CONTINUATION
```

Diese Muster sind statische Folgen der Tabelle. Sie sind noch keine
Bildungswerte und duerfen nicht als Viererfolge in D3 gespeichert werden.

## Konservative D3-Zielprojektion

Das transiente Ereignis darf spaeter hoechstens die Zulassigkeit einer
Umordnung innerhalb der bereits validierten D3-Unterteilung bestimmen.

Mit einem noch ungebundenen lokalen Umordnungsbetrag `m` gilt anatomisch:

```text
post.free = pre.free
post.blocked = pre.blocked
post.capacity = pre.capacity

post.bound_unconfigured = pre.bound_unconfigured - m
post.bound_configured = pre.bound_configured + m

0.0 <= m <= pre.bound_unconfigured
```

Daraus folgen exakt:

```text
post.bound_unconfigured + post.bound_configured
= pre.bound_unconfigured + pre.bound_configured

post.capacity
= post.free
 + post.bound_unconfigured
 + post.bound_configured
 + post.blocked
```

`m` ist in S1-NZ nur eine Bilanzvariable, kein gewaehlter Betrag und kein
Parameter.

Ereignisgrenzen:

```text
NO_PREDECESSOR   -> m = 0.0
LOCAL_SWITCH     -> m = 0.0
LOCAL_CONTINUATION -> 0.0 <= m <= pre.bound_unconfigured
```

Ein spaeterer Bildungsvertrag muss fuer die F2-Prognose vor Ausfuehrung eine
positive Fortsetzungsumordnung binden. S1-NZ tut dies noch nicht.

## Atomare Commitordnung

Die einzig zulaessige technische Reihenfolge lautet:

```text
1. transiente Grenzfigur vollstaendig entgegennehmen
2. Kante, Feldreferenz, Abschluss und direkte Nachbarschaft validieren
3. genau ein Ereignis klassifizieren
4. D3-Vorzustand separat validieren
5. Ereigniszulassigkeit und konservative Zielprojektion pruefen
6. spaeter optional D3-Nachzustand atomar committen
7. Grenzfigur und Ereignis aus dem Kandidatenpfad vollstaendig verwerfen
8. nur den validierten D3-Nachzustand an die naechste Feldzeit uebergeben
```

Ein partieller D3-Commit vor vollstaendiger Validierung ist verboten. Bei
jedem Fehler bleibt der D3-Vorzustand unveraendert und es entsteht kein
Sachereignis.

## Persistenzgrenze nach Commit

Im Kandidaten- und Feldnachzustand sind nach Schritt 7 ausdruecklich verboten:

- `prior_interval_ordinal` oder `current_interval_ordinal`;
- `prior_orientation` oder `current_orientation`;
- `NO_PREDECESSOR`, `LOCAL_CONTINUATION` oder `LOCAL_SWITCH`;
- Kontaktbytes oder Kontaktdigests;
- Vorgaengerzeiger, Ereignisindex oder Sequenzlaenge;
- H0-, H1-, Spiegel- oder Armkennung;
- Zaehler fuer Fortsetzungen oder Wechsel;
- eine Liste frueherer D3-Zustaende.

Persistieren darf im Kandidatenpfad nur der validierte D3-Ressourcenzustand.
Damit traegt die spaetere O3-Wirkung keine lesbare Kontaktfolge, sondern nur
die konservative lokale Unterteilung.

## Passive Beobachtergrenze

Eine spaetere fokussierte Abnahme darf ausserhalb des Kandidaten- und
Feldpfads einen unveraenderlichen technischen Beobachterbeleg fuer genau eine
Grenze erzeugen. Er darf Validierungsstatus und Ereignisrolle dokumentieren,
aber niemals als Eingabe an D3, O3, Feld, Baseline oder naechste Grenze
zurueckgegeben werden.

Ein solcher externer Beleg ist Testevidenz, kein Kandidatenzustand. Eine
Sammlung von Belegen darf nicht als Replay- oder Bildungsquelle dienen.

## Fail-Closed-Zustaende

Ungueltig sind:

- fehlender Vorgaenger bei `current_interval_ordinal>0`;
- vorhandener Vorgaenger bei `current_interval_ordinal=0`;
- nicht direkt aufeinanderfolgende oder negative Ordinale;
- boolesche Ordinale;
- nicht abgeschlossene Intervalle;
- verschiedene Kanten oder Feldreferenzen;
- leere, unbekannte oder nicht gespiegelte Orientierungsrollen;
- mehr als ein Vorgaenger oder mehr als ein aktueller Kontakt;
- Arm-ID, Zielwert, Reward, Readout oder Ergebniswissen;
- Rohdaten, Kontaktlisten oder Sequenzpuffer;
- D3-Umbuchung bei `NO_PREDECESSOR` oder `LOCAL_SWITCH`;
- negativer oder zu grosser Bilanzbetrag;
- Aenderung von `free`, `blocked`, Kapazitaet oder aggregiertem `bound`;
- Fortbestand eines transienten Feldes nach Commit;
- stille Reparatur, Sortierung, Normalisierung oder Intervallergaenzung.

## Baselinegrenze

Das Ereignisalphabet ist keine exklusive Kandidateninformation. Eine spaetere
faire zustandsbehaftete Adapterbaseline darf dieselbe gueltige transiente
Klassifikation sehen. Sie besitzt jedoch keine D3-Unterteilung und darf keine
verdeckte Kopie davon einfuehren.

DTS-1, T1, Leaky und Integrator erhalten dieselben Intervallgrenzen und
Ereignisrollen, soweit ihre vorregistrierten APIs dies kausal zulassen. Ein
Baselineprofil ohne dieselbe relevante Vorgeschichte ist nicht vergleichbar.

## Erlaubte spaetere Anatomietests

Eine spaetere isolierte Abnahme darf nur pruefen:

- die sechs gueltigen Tabellenfaelle;
- die drei vollstaendigen Vierereignismuster;
- Spiegelinvarianz von X/X gegen Y/Y;
- alle Nachbarschafts-, Identitaets- und Abschlussfehler;
- Nullzulassung fuer ersten Kontakt und Wechsel;
- konservative Zielprojektion fuer einen symbolisch gueltigen Betrag;
- unveraenderten D3-Vorzustand bei Fehler;
- Abwesenheit transienter Rollen im D3-Nachzustand;
- passive, nicht rueckfuehrbare Beobachterbelege;
- Abwesenheit von Feld-, Runner-, Medien-, Netzwerk- und I/O-Pfaden.

Nicht erlaubt sind Betragswahl, Raten-, Schwellen-, Bildungs-, O3-,
Abschwaechungs-, Interferenz- oder Feldwirkungstests.

## Aussagegrenze

S1-NZ bindet nur eine transiente Ereignisanatomie und konservative
Zielprojektion. Es gibt keinen Ereignisvalidator, keine Umordnungsmenge, keine
Bildungsgleichung, keinen gebildeten D3-Zustand, keine Spaetwirkung oder
Feldwirkung, keine Lernfunktion und keinen Befund zur hypothetischen
MCM-Memory.

## Naechster erlaubter Schritt

S1-OA darf ausschliesslich einen statischen Schema-, Digest- und
Fail-Closed-Validatorvertrag fuer die transiente Grenzfigur, das
Ereignisalphabet und einen passiven Einzelgrenzenbeleg binden. Er muss die
Persistenzsperre maschinenlesbar machen.

S1-OA darf noch keinen Validator implementieren, keine Umordnungsmenge, Rate,
Schwelle oder Bildungsgleichung waehlen und keinen Runtime-, Transfer- oder
Feldpfad ausfuehren.

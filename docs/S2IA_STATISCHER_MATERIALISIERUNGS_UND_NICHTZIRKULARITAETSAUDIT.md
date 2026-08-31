# S2-IA - Statischer Materialisierungs- und Nichtzirkularitaetsaudit

## Status

`S2IA_BLOCKED_THREE_MATERIALIZATION_BINDINGS_OPEN`

Der S2-HZ-Zwei-Bereich-Konfliktindikator ist als read-only Engineeringfunktion
grundsaetzlich materialisierbar. Die vorhandenen S2-GI- und S2-GC-Datentypen
stellen die benoetigten A-/B-Kandidaten, Werte und Quelldigests bereit.

Der Audit ist dennoch nicht bestanden. Drei konkrete Bindungen verhindern die
Freigabe einer Implementierung. Es wurden kein Code, keine Tests und keine
Zustandsfunktion ausgefuehrt.

## Gepruefte Quellen

Read-only abgeglichen wurden:

- `docs/S2HZ_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md`;
- `tools/_s2gi_private_two_area_context_projection.py`;
- `tools/_s2gb_private_perceptual_context_bundle.py`;
- `tools/_s2hq_private_role_addressed_context_consumer.py`;
- `tools/_s2hq_private_direct_role_addressed_mask_fill_baseline.py`;
- der abgeschlossene S2-HY-Funktionsbefund.

## Bestandene Teilpruefungen

### Kandidatenmaterialisierung

`TwoAreaContextBundle` enthaelt exakt die kanonischen Bereiche `A_RECENT` und
`B_STABLE` sowie Konfigurations-, Probe-, Quellen-, Composite-Zustands-, Vor-,
Nach- und Bundledigests.

Fuer A sind der oeffentliche `B4_RECENT`-Befund, Kandidat, gemeinsame
AV-Komponente und deren 26 Werte vorhanden. Die 18 visuellen Werte koennen
eindeutig als Werte 8 bis 25 gelesen werden. `fast_internal` ist getrennt und
muss nicht als Ersatz verwendet werden.

Fuer B sind der `TSPM_SLOW`-Befund, Kandidat, stabile visuelle Komponente und
deren 18 Werte vorhanden. `ABSENT_VALID` ist im bestehenden Datentyp ohne
Kandidat eindeutig darstellbar.

Es muss keine Provenienz erfunden und kein Speicher erneut abgefragt werden.

### Maskenvergleich

Die existierende `MaskedVisualProbe` bindet 18 Positionen, davon neun sichtbar
und neun maskiert. Fuer zwei anwendbare Kandidaten lassen sich
`CONSISTENT` und `CONFLICT` ausschliesslich aus den neun moeglichen
Maskenergaenzungen ableiten:

```text
alle neun Ergaenzungswerte gleich  -> CONSISTENT
mindestens ein Wert verschieden    -> CONFLICT
```

Sichtbare Werte werden nur in einem vorgelagerten Anwendbarkeitsbefund
validiert. Sie duerfen weder in den A/B-Ergaenzungsvergleich noch in eine
Sollentscheidung eingehen. Zielwerte sind fuer die Signalerzeugung nicht
erforderlich.

### Symmetrie und Nichtauswahl

Der Statusvergleich ist technisch symmetrisch materialisierbar. Bei
Vertauschung von A und B bleiben `CONSISTENT`, `CONFLICT` und `NO_CONTEXT`
unveraendert; `SINGLE_SOURCE` behaelt seinen Status und vertauscht nur die
transparente Bereichsangabe.

Kein vorhandener Datentyp erzwingt eine Rangfolge. Ein Ergebnis kann
`selected_area`, `recommended_area` und `automatic_selection` verbindlich auf
`None` halten. Eine Verschmelzung oder ein Fallback ist nicht erforderlich.

### Direkte Baseline

Die direkte Baseline kann mit demselben Bundle, derselben Probe, denselben
Bereichskandidaten und derselben Maskenpositionstabelle unabhaengig
materialisiert werden. Sie muss beide Rollen separat lesen und darf weder den
Signalgeber noch dessen Zwischenbefunde uebernehmen.

Der S2-HY-Befund belegt bereits, dass der vorhandene Rollenverbraucher und die
direkte Rollenfuellbaseline bei identischem Rolleninput dieselben Ausgaben
erzeugen. Fuer S2-HZ ist daher eine vollstaendige Reduktion auf direkten
Vergleich erwartbar und methodisch zulaessig.

## Blocker IA-B01 - Statusdomain widerspricht S2-IA

S2-IA bindet:

```text
NO_CONTEXT <=> A == ABSENT_VALID und B == ABSENT_VALID
```

Der aktuelle S2-HZ-Vertrag erlaubt dagegen `NO_CONTEXT`, sobald kein Bereich
`APPLICABLE` ist und beide Bereiche beliebig `ABSENT_VALID` oder
`VISIBLE_CONFLICT` sind. Fall C8 bindet ausdruecklich:

```text
A == VISIBLE_CONFLICT
B == VISIBLE_CONFLICT
-> NO_CONTEXT
```

Dieser Eingang ist technisch erreichbar: Zwei strukturell gueltige Kandidaten
koennen derselben maskierten Probe auf sichtbaren Positionen widersprechen.
Er ist weder zweimal `ABSENT_VALID` noch eine beschaedigte Evidenz.

Damit besitzt die aktuelle Statusfunktion fuer einen gueltigen erreichbaren
Eingang eine nach S2-IA unzulaessige Ausgabe. `NO_CONTEXT` darf diesen Fall
nicht aufnehmen. Der Audit darf weder stillschweigend C8 entfernen noch einen
fuenften regulaeren Status erfinden.

Erforderliche spaetere Korrektur: `NO_CONTEXT` exakt auf zweimal
`ABSENT_VALID` begrenzen und fuer den erreichbaren Null-Anwendbarkeitsfall mit
mindestens einem `VISIBLE_CONFLICT` eine ausdrueckliche Nichtausgabe- oder
Abbruchgrenze ausserhalb der vier regulaeren Statuswerte binden.

## Blocker IA-B02 - Ownerform fehlt

Die bestehenden S2-GI- und S2-GC-Bundles enthalten vollstaendige Quellen- und
Zustandsdigests, aber keine fuer S2-HZ vorgesehene Aufrufownerform. Der
S2-HZ-Vertrag nennt Ownerbruch als `NOT_EVALUABLE`, definiert jedoch nicht:

- exakten privaten Ownertyp;
- Erzeugungsquelle und Anfangszustand;
- Bindung an Probe-, Bundle- und Zustandsdigest;
- atomaren Einmalverbrauch;
- Endzustand bei Erfolg und Fehler;
- Ausschluss einer Wiederverwendung fuer Signalgeber oder Baseline.

Eine Owner-ID darf nicht aus Probeinhalt, erwarteter Klasse oder spaeterem
Ergebnis rekonstruiert werden. Ohne diese Form kann die verlangte Ownerbindung
nicht statisch abgenommen werden.

Erforderliche spaetere Korrektur: zwei getrennte, budgetgleiche private
Einmalowner fuer Signalgeber und Direktbaseline aus einer gemeinsamen
validierten Aufrufbindung ableiten. Kein Arm darf den Owner oder das Ergebnis
des anderen verwenden.

## Blocker IA-B03 - Exakte Ressourcen- und Digestformen offen

S2-HZ bindet sinnvolle endliche Funktionsobergrenzen. Der Vertrag erklaert
jedoch selbst die konkreten Digest- und Serialisierungszahlen als noch offen.
Damit fehlen fuer Signalgeber und Direktbaseline:

- exakte Anzahl und Rolle jedes Digests;
- genaue Felder der beiden Anwendbarkeitsbefunde;
- genaue Felder und kanonische Form des Signals;
- pfadabhaengige Ledgerwerte fuer zwei, einen und keinen Kandidaten;
- identische Baselinebudgets je Statuspfad;
- maximale Objekt- und Receiptgroessen;
- eindeutige Ablehnungsstelle bei Budgetueberschreitung.

Die vorhandenen Obergrenzen beweisen Endlichkeit, aber noch keine
budgetidentische Materialisierung. Eine Implementierung koennte sonst
unbeabsichtigt einen Arm bevorzugen oder nicht aufgezeichnete Hilfsarbeit
verwenden.

Erforderliche spaetere Korrektur: literale Datenformen und exakte Ledger fuer
`CONSISTENT`, `CONFLICT`, A-only, B-only und zweimal `ABSENT_VALID` binden.
Signalgeber und Direktbaseline muessen auf jedem korrespondierenden Pfad
dieselben funktionalen Obergrenzen erhalten; native Kosten sind getrennt zu
berichten.

## Quellen- und Digestgraph

Abgesehen von IA-B02 und IA-B03 ist folgender Graph azyklisch
materialisierbar:

```text
validierte Probe + validiertes S2-GI-Bundle
-> unabhaengiger A-Anwendbarkeitsbefund
-> unabhaengiger B-Anwendbarkeitsbefund
-> Maskenergaenzungsvergleich
-> Signal

dieselben Eingabewurzeln
-> unabhaengige direkte A-/B-Pruefung
-> Baselinesignal

vorab versiegelte Statusmatrix + beide fertigen Signale
-> reiner Auswertungsbefund
```

A- und B-Befund duerfen sich nicht gegenseitig als Eltern verwenden. Der
Sollstatus darf erst nach beiden fertigen Signalen in die Auswertung gelangen.
Beschadigte Typ-, Rollen-, Quellen-, Probe-, Zustands- oder Digestevidenz muss
vor jeder regulaeren Statusausgabe fail-closed stoppen und darf insbesondere
nicht zu `ABSENT_VALID` oder `NO_CONTEXT` werden.

## Erreichbarkeit der Fallmatrix

Statisch erreichbar sind:

- `CONSISTENT`: derselbe visuelle Inhalt ist gleichzeitig A-recent und
  B-stabil;
- `CONFLICT`: S2-HY belegt gleichzeitig verschiedene, zur maskierten Probe
  passende A-/B-Inhalte;
- A-only `SINGLE_SOURCE`: frischer passender A-Inhalt ohne stabilen B-Inhalt;
- B-only `SINGLE_SOURCE`: stabiler B-Inhalt nach Entfernung aus A, abgefragt
  durch seine Voll- beziehungsweise Teilprobe;
- `NO_CONTEXT`: frischer oder nicht passender Zustand mit zweimal
  `ABSENT_VALID`;
- die sichtbaren Konfliktkontrollen C6 bis C8.

Gerade die Erreichbarkeit von C8 macht IA-B01 materiell und verhindert eine
Abnahme durch blosse Einschränkung der Testfixture.

## Auditentscheidung

Der private Konfliktindikator darf noch nicht implementiert werden.

Die fachliche Richtung bleibt tragfaehig: A/B-Kandidaten, Maskenwerte,
Abwesenheiten, Symmetrie und direkte Baseline sind vorhanden und ohne neue
Memory-Ebene nutzbar. Geschlossen werden muessen ausschliesslich:

1. die Statusdomain fuer den doppelten sichtbaren Konflikt;
2. die private atomare Ownerbindung;
3. die exakten Daten-, Digest-, Ledger- und Groessenformen.

Eine spaetere Korrektur darf keine automatische Auswahl, Rangfolge,
Verschmelzung, Speicherabfrage oder Feldwirkung einfuehren. Erst nach ihrer
statischen Abnahme kann S2-IA wiederholt und bei Erfolg die Implementierung
separat freigegeben werden.

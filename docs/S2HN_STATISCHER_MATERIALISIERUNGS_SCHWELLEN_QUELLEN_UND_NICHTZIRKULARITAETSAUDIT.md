# S2-HN: Statischer Materialisierungs-, Schwellen-, Quellen- und Nichtzirkularitaetsaudit

Status: `STATIC_AUDIT_BLOCKED_SIMULTANEOUS_CONTEXT_UNREACHABLE`

## Gegenstand und Grenze

S2-HN prueft den statischen S2-HM-Vertrag gegen die vorhandenen privaten
B4-, TSPM-1-, S2-GC- und S2-GI-Grenzen. Es wurden keine Module importiert,
keine Zustandsfunktion ausgefuehrt, keine Tests angelegt und keine
Implementierung veraendert.

Der Audit stoppt fail-closed. Die beiden Bildungsgeschichten koennen zwar
einen juengsten A-Inhalt und einen stabilisierten B-Inhalt im internen
Speicherzustand erzeugen. Die in S2-HM gebundene gemeinsame Vollprobe kann
diese Inhalte unter der weiterhin verbindlichen visuellen Funktionsschwelle
`44/765` jedoch nicht gleichzeitig als oeffentliche A/B-Kontextkandidaten
bereitstellen.

## 1. Bildung und gleichzeitiger interner Bestand

Die Konfiguration des vorhandenen Pfads bindet:

- B4-Kapazitaet `9`;
- TSPM-Fast-Kapazitaet `3`;
- auditive und visuelle Fast-Matchschwelle `0,2`;
- Konsolidierung ab Fast-Support `2`;
- Fast-Ablauf nach `8` nicht ausgewaehlten Expositionsschritten;
- PPB-Stabilitaet ab Slow-Support `3`.

Fuer H1 und H2 gilt statisch spiegelbildlich:

1. Die erste B-Exposition erzeugt einen Fast-Slot mit Support `1`.
2. Die zweite bis vierte identische B-Exposition aktualisieren denselben
   Fast-Slot. Jede dieser drei Aktualisierungen ist konsolidierungsfaehig.
3. Die drei PPB-Schritte erzeugen und stabilisieren den auditiven und den
   visuellen B-Prototypen bei Support `3`.
4. Der Abstand A gegen B betraegt auditiv `1/4` und visuell `77/255`.
   Beide Werte liegen ueber der jeweiligen Fast-Matchschwelle `1/5`.
5. Die einzelne A-Exposition erzeugt deshalb einen zweiten Fast-Slot. Sie
   ist nicht konsolidierungsfaehig, ruft PPB-1 nicht auf und kann den
   stabilen B-Prototypen weder aktualisieren noch ersetzen.
6. Nach insgesamt fuenf Expositionen sind alle B4-Eintraege vorhanden. A ist
   der juengste B4-Eintrag. Der B-Fast-Slot ist erst einen Schritt alt und
   nicht abgelaufen; die Fast-Kapazitaet ist nicht erschoepft.

Damit sind `A intern vorhanden` und `B intern stabil vorhanden` erreichbar.
Dieser Befund allein erzeugt aber noch keine zwei oeffentlich verfuegbaren
S2-GI-Bereiche fuer dieselbe Probe.

## 2. Verbindliche Distanzrechnung

Die neun abweichenden visuellen Positionen unterscheiden C und F jeweils um
`154/255`. Bei 18 Werten ergibt sich:

```text
d(C,F) = 9 * (154/255) / 18 = 77/255 = 231/765
```

Fuer beide S2-HM-Proberichtungen gilt:

```text
d(Probe,A) = 36/255 = 108/765
d(Probe,B) = 41/255 = 123/765
```

Die aktive read-only Inhaltsauswertung verwendet fuer visuelle
Funktionsbefunde nicht die native TSPM-Fast-Schwelle `1/5`, sondern die
eingefrorene L1-KAL-Schwelle:

```text
44/765 = 0,057516...
```

Somit gilt:

```text
108/765 > 44/765
123/765 > 44/765
```

Die auditive Vollprobe liegt mit `1/8` zwar innerhalb der auditiven
Funktionsschwelle `1/5`. Ein vollstaendiger audiovisueller Treffer verlangt
aber beide Modalitaeten. Der visuelle Bruch ist daher entscheidend.

## 3. Folge fuer die drei Kontextrollen

Der vorhandene S2-FS-read-only-Pfad uebergibt an S2-GC ausschliesslich
funktional ausgewaehlte Quellen:

- `B4_RECENT`: kein Treffer, weil kein B4-Eintrag die visuelle Schwelle
  `44/765` einhaelt;
- `TSPM_FAST`: kein funktionaler Fast-Treffer aus demselben Grund, auch wenn
  die native Fast-Pruefung gegen `0,2` einen Slot finden koennte;
- `TSPM_SLOW`: kein funktionaler stabiler Slow-Treffer, weil auch dessen
  visuelle Funktionsentscheidung `44/765` verwendet. Die native PPB-Schwelle
  `0,05` ist noch enger und hilft ebenfalls nicht.

S2-GC muss diese Rollen folglich als gueltige Abwesenheit abbilden. S2-GI
kann daraus weder einen oeffentlichen A-Kandidaten noch einen oeffentlichen
B-Kandidaten erzeugen. Die in S2-HM verlangte gleichzeitige Belegung ist fuer
die gebundene gemeinsame Vollprobe nicht erreichbar.

Dies ist kein negativer Befund zur bereits bestaetigten Memory-Architektur.
Es ist ein Widerspruch zwischen der S2-HM-Probengeometrie und der bestehenden
Abrufgrenze.

## 4. Rollenfaelle und Budgets

H1 und H2 sind hinsichtlich der vorgesehenen Arbeit spiegelbildlich:

- je fuenf Composite-Formationen;
- je eine gemeinsame Vollprobe;
- je eine S2-GC- und S2-GI-Projektion;
- je zwei explizite Rollenfaelle;
- je Rollenfall ein Verbraucher- und ein unabhaengiger Baselineaufruf mit
  derselben maskierten Probe.

Damit waeren HM-01 bis HM-04 auf Klassen- und Aufrufebene budgetgleich.
Diese Gleichheit behebt den Erreichbarkeitsbruch nicht. Da bereits die
gemeinsame Kontextbereitstellung ausfaellt, duerfen weder Verbraucherbudgets
materialisiert noch eine spaetere Funktionsausgabe vorweggenommen werden.

## 5. Quellen-, Owner- und Digestbindung

Der vorhandene Pfad kann die benoetigte Beweiskette vorwaertsgerichtet und
ohne Zielwerte binden:

```text
literale Rezeptorfixture
-> Rezeptor- und Envelopeprovenienz
-> gebundener Composite-Eingang
-> einmalig verbrauchter Formation-Owner
-> Composite-Nachzustand und Step-Receipt
-> gebundene read-only Vollprobe
-> S2-FS-Finding
-> S2-GC-Bundle
-> S2-GI-Zwei-Bereich-Projektion
-> spaetere explizite Rollenbindung
-> Verbraucher- und Baselineergebnis
-> getrennte Auswertung
```

Jeder Formation-Owner ist an Konfiguration, Vorzustand und Eingabedigest
gebunden und endet nach einem Versuch terminal. Die read-only Probe bindet
Vor- und Nachzustandsdigest identisch. Die explizite Rollenwahl kann erst
nach einer gueltigen S2-GI-Projektion hinzutreten; sie darf keinen Kandidaten
erzeugen und keine automatische Auswahl ersetzen.

Zielwerte, Sollrollen und HM-Zellkennungen duerfen nur in der getrennten
Auswertung liegen. Verbraucher und direkte Baseline duerfen sie nicht als
Eingabe erhalten. Diese Quellen- und Nichtzirkularitaetsanforderung ist
statisch materialisierbar, wird wegen des vorgelagerten Schwellenbruchs aber
nicht zur Implementierung freigegeben.

## 6. Auditentscheidung

| Pruefpunkt | Befund |
|---|---|
| B vor A stabilisiert | bestanden |
| A bei der Probe intern vorhanden | bestanden |
| keine A-Konsolidierung und keine B-Verdraengung | bestanden |
| konkrete Rezeptorwerte und Distanzen | nachgerechnet |
| vier Rollenfaelle strukturell budgetgleich | bestanden |
| Quellen-, Owner- und Digestgraph materialisierbar | bestanden |
| Zielwerte vom Funktionspfad getrennt | bestanden |
| explizite Rolle von automatischer Auswahl getrennt | bestanden |
| A und B gleichzeitig oeffentlich abrufbar | **nicht bestanden** |

Blocker `HN-B01`:

```text
S2-HM bewertet die Vollprobe gegen 0,2.
Die oeffentliche S2-GC/S2-GI-Kontextbereitstellung verlangt visuell 44/765.
Die gebundenen Abstaende 108/765 und 123/765 ueberschreiten diese Grenze.
```

Der geforderte Fail-Closed-Stopp tritt deshalb vor jeder Projektion in einen
rollenadressierten Verbraucher ein. S2-HM bleibt als statischer
Entwicklungsvertrag erhalten, ist in seiner aktuellen Probengeometrie aber
nicht implementierungsfaehig. Der private rollenadressierte Verbraucher ist
nicht freigegeben.

Eine Fortsetzung erfordert eine ausdrueckliche neue fachliche Entscheidung
ueber die Konfliktaufgabe oder die Probenbildung. S2-HN selbst veraendert
weder Schwellen noch Kandidaten, Speichermechanik oder Projektionsregeln.

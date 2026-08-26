# S2-DD: Architekturentscheid fuer eine MCM-kompatible perzeptive Memory

## Auftrag und Einordnung

S2-DD beendet die Suche nach einer besonderen neuen Speicherursache und
trifft stattdessen eine technische Architekturentscheidung. Bewertet werden
bekannte Speicherfamilien danach, wie gut sie reduzierte auditive und
visuelle Wahrnehmungszustaende begrenzt, reproduzierbar und getrennt vom
MCM-Feldkern bilden, aktualisieren, vergessen und spaeter read-only
bereitstellen koennen.

Es wurden keine Projektmodule importiert, keine Zustands-, Probe-, Baseline-
oder Feldfunktion ausgefuehrt und keine Implementierung geaendert. Der
Entscheid ist ein Engineeringbefund und kein neuer MCM-Feld- oder
Memory-Mechanismusbefund.

## Bereits vorhandene Grundlage

PPB-1 stellt bereits zwei getrennte private Baenke fuer reduzierte auditive
und visuelle `ReceptorContactFrame`-Zustaende bereit. Vorhanden sind:

- feste Kapazitaet und stabile Slotidentitaeten;
- normalisierte L1-Zuordnung und Online-Aktualisierung;
- Support- und Stabilitaetsgrenze;
- deterministische Verdraengung und schrittbasierter Ablauf;
- kausal spaetere read-only Probe;
- Digest-, Quellen-, Zeitordnungs- und Fail-Closed-Bindungen;
- strikte Trennung von oeffentlicher API und Feldsnapshot.

PPB-1 ist damit die geeignete langsame Prototyp- und Minimalbaseline. Allein
bildet PPB-1 jedoch neue Einzelvorgaenge unmittelbar in Prototypslots ab. Es
trennt schnelle vorlaeufige Bindung und langsam bestaetigte Stabilisierung
nicht als zwei eigene Speicherrollen.

## Vergleich der vier Architekturpfade

| Architektur | Staerke | Grenze im vorliegenden Projekt | Entscheidung |
| --- | --- | --- | --- |
| PPB-1 allein | klein, vorhanden, begrenzt, deterministisch, read-only pruefbar | keine getrennte schnelle episodische und langsame stabilisierende Rolle | verbindliche Minimalbaseline und langsame Ebene |
| moderne assoziative beziehungsweise Hopfield/BAM-artige Speicherung allein | inhaltsadressierter Abruf und Mustervervollstaendigung | Aktualisierung, Ablauf, Konfliktpolitik und Quellenbindung muessten neu festgelegt werden; keine eigene langsame Stabilisierung | nicht als alleinige Architektur |
| Zwei-Zeitskalen-Modell | trennt schnelle Aufnahme neuer Vorgaenge von langsamer Stabilisierung wiederholter Strukturen | benoetigt einen privaten atomaren Koordinator und eine streng gebundene Konsolidierungsregel | ausgewaehlt |
| begrenzter Reservoirzustand | traegt kurzfristigen zeitlichen Kontext | kein klarer dauerhafter Speicherbestand, Abrufziel und Vergessen sind vom Readout abhaengig | spaetere Kurzzeitbaseline, nicht Hauptspeicher |

Die Auswahl folgt einem technischen Konflikt: Neue Wahrnehmungszustaende
sollen schnell verfuegbar sein, duerfen aber bestaetigte Prototypen nicht bei
jeder Einzelabweichung sofort veraendern. Eine schnelle und eine langsame
Ebene machen diese beiden Rollen getrennt messbar.

## Ausgewaehlter Engineeringpfad: TSPM-1

`TSPM-1` bezeichnet eine **private Two-Scale Perceptual Memory**. Sie besteht
aus genau einer zusammenhaengenden Architektur mit zwei klar getrennten
Zeitskalen:

1. `Fast Associative Store`: begrenzte, kurzlebige und inhaltsadressierbare
   Eintraege fuer gemeinsam exponierte reduzierte auditive und visuelle
   Zustaende. Gespeichert werden keine Rohdaten und keine semantischen Labels.
2. `Slow Prototype Store`: die bestehenden getrennten PPB-1-Baenke fuer
   wiederholt bestaetigte auditive und visuelle Prototypen.
3. `Consolidation Coordinator`: eine private atomare Entscheidung, ob die
   aktuelle originale Exposition aufgrund wiederholter Evidenz auch die
   langsame Ebene fortsetzen darf. Er erzeugt kein synthetisches Replay.
4. `Read-only Resolver`: getrennte Abfrage beider Ebenen und deterministische
   Auswahl eines privaten perzeptiven Kontextbefunds ohne Zustandsaenderung.

Dies ist ein Architekturpfad und keine Sammlung konkurrierender Kandidaten.
Die schnelle assoziative Ebene und PPB-1 haben unterschiedliche technische
Aufgaben innerhalb desselben begrenzten Systems.

## Daten- und Kausalpfad

```text
validierte reduzierte Audio-/Video-Exposition
-> atomare Quellen- und Zeitpruefung
-> begrenzte schnelle Bindung
-> vorab gebundenes Konsolidierungsgate
-> optionaler langsamer PPB-1-Schritt mit der aktuellen Originalexposition
-> getrennte spaetere read-only Probe
-> privater perzeptiver Kontextbefund
```

Der schnelle Zustand darf weder Rohpayload noch Feldsnapshot enthalten. Das
Konsolidierungsgate darf nur die aktuelle validierte Exposition an PPB-1
weiterreichen; es darf keine alte Exposition nachbilden oder als neuen
Rezeptorkontakt ausgeben.

## Erfuellung der Anforderungen

- Auditive und visuelle Zustaende bleiben modalitaetsspezifisch gebunden;
  nur die schnelle Ebene darf eine gemeinsame Expositionsrelation halten.
- Beide Ebenen erhalten feste Kapazitaeten und getrennte Bitbudgets.
- Bildung und Aktualisierung sind atomare, digestgebundene Uebergaenge.
- Die schnelle Ebene verwirft nach fester Ablauf- und Verdraengungsregel;
  die langsame Ebene verwendet die bestehenden PPB-1-Regeln.
- Der Abruf ist vollstaendig read-only und liefert keinen Nachzustand.
- Ein spaeterer innerer Kontext ist ein eigener privater Typ und kein
  Rezeptorinput, Feldsnapshot oder semantischer Zustand.
- Jede Ebene und jeder Gesamtzustand besitzen kanonische Identitaetsdigests.
- Retry, Teilverbrauch, fremde Quellzustaende und gemischte Versuche werden
  fail-closed verworfen.

## Nicht ausgewaehlte Erweiterungen

Eine moderne Hopfield-Schicht wird nicht sofort implementiert. Ihr
inhaltsadressierter Abruf bleibt eine spaetere faire Vergleichs- oder
Ersatzoption fuer den schnellen Store. Ein Reservoir bleibt fuer
kurzfristigen zeitlichen Kontext reserviert. Weder Hopfield noch Reservoir
werden in TSPM-1 verdeckt als zusaetzlicher dritter Speicher aktiviert.

Semantik, Woerter, Objektlabels, Feldrueckwirkung, oeffentliche API,
Produktionspersistenz und Live-Sensorik gehoeren nicht zu diesem Entscheid.

## Vor Implementierung zu bindende Punkte

S2-DD legt noch keine Gleichung oder Parameter fest. Ein spaeterer
Implementierungsvertrag muss mindestens binden:

- exakte schnelle Eintragsanatomie und Gesamtbitbudget;
- Aehnlichkeits-, Gleichstands-, Ablauf- und Opferregel;
- atomare Bildungs- und Konfliktuebergaenge;
- Konsolidierungsevidenz und eindeutige Freigabereihenfolge;
- getrennte Identitaeten fuer Fast-, Slow- und Gesamtzustand;
- read-only Abfrage- und Arbitrierungsregel;
- No-Memory-, PPB-1-only-, assoziative-only- und Reservoirbaseline;
- Negativtests fuer stale, fremde, vertauschte und teilweise verbrauchte
  Quellen.

## Entscheidung und naechste Grenze

`SELECT_TSPM1_BOUNDED_TWO_SCALE_PERCEPTUAL_MEMORY_ENGINEERING_ARCHITECTURE`

TSPM-1 ist genau der eine ausgewaehlte private Engineeringpfad. PPB-1 bleibt
unveraendert die langsame Ebene und Minimalbaseline. Noch freigegeben sind
weder Implementierung noch Tests oder Ausfuehrung.

Der naechste fachlich kleinste Schritt ist S2-DE: ein statischer
Implementierungsvertrag fuer den privaten schnellen Store und den atomaren
Konsolidierungskoordinator. Er darf bestehende PPB-1-Regeln nicht aendern und
noch keinen Feld- oder Produktionspfad oeffnen.

## Technische Referenzen

- McClelland, McNaughton und O'Reilly (1995), Complementary Learning
  Systems: https://doi.org/10.1037/0033-295X.102.3.419
- Ramsauer et al. (2021), Hopfield Networks is All You Need:
  https://openreview.net/forum?id=tL89RnzIiCd
- Jaeger (2001), The Echo State Approach:
  https://doi.org/10.24406/publica-fhg-291111

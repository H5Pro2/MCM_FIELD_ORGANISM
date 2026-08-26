# W1-U: Lokaler Kontrast unter AV-Hintergrundbelastung

Stand: 2026-08-09

Entscheidung: `W1U_UNMODIFIED_FIELD_CONTRAST_RETAINED`

Forschungslauf: nein

Realer Browser gestartet: nein

Adaptive Regulation implementiert: nein

## Auftrag

W1-U prueft, ob eine feste kleine lokale Weltunterscheidung unter steigender
gleichmaessiger Feldbelastung schlechter erhalten bleibt. Jede Beobachtung
vergleicht zwei frische, identisch konfigurierte 26-Neuronen-AV-Felder:

```text
gleichmaessiger Hintergrund
gegen
derselbe Hintergrund + 0.1 lokaler Kontrast
```

Der Kontrast liegt wahlweise am auditiven oder visuellen Kontakt `n4`.
Hintergrundstufen 0.0, 0.5 und 0.9, Belastungsdauern 0.1, 1.0 und 4.0 s sowie
vier feste Baselines ergeben 72 gepaarte Beobachtungen und 144 frische
synthetische Felder.

## Baselines

- `unmodified`: unveraenderte Kontakte und unveraendertes neutrales Feld.
- `fixed_gain_0_5`: Hintergrund und Kontrast werden beide fest halbiert.
- `fixed_leaky_1_0`: feste Afterimage- und Dissipationszeit von 1.0 s.
- `static_clip_0_5`: jeder Kontakt wird vor dem Feld fest auf 0.5 begrenzt.

Keine Baseline liest den Feldzustand zur Anpassung ihrer Eingabe. Es gibt
keine Sensitivitaetsvariable, Zielaktivitaet, Rueckschreibung oder adaptive
Regulation.

## Vier-Sekunden-Befund

| Baseline | Modalitaet | Delta-Linf bei Hintergrund 0.0 | Delta-Linf bei Hintergrund 0.9 |
|---|---|---:|---:|
| unmodified | auditiv | 0.03572712811846953 | 0.03572712811846934 |
| unmodified | visuell | 0.030478396088127427 | 0.030478396088128745 |
| fixed_gain_0_5 | auditiv | 0.017863564059234765 | 0.01786356405923467 |
| fixed_gain_0_5 | visuell | 0.015239198044063713 | 0.015239198044064373 |
| fixed_leaky_1_0 | auditiv | 0.02153553795715956 | 0.021535537957159123 |
| fixed_leaky_1_0 | visuell | 0.019448484988689917 | 0.019448484988689563 |
| static_clip_0_5 | auditiv | 0.03572712811846953 | 0.0 |
| static_clip_0_5 | visuell | 0.030478396088127427 | 0.0 |

Ueber alle Dauern und beide Modalitaeten betraegt der groesste
hintergrundabhaengige Deltafehler des unveraenderten Feldes
`3.344546861683284e-15`. Der lokale Kontrast bleibt damit innerhalb der
gebundenen numerischen Toleranz von `1e-12` erhalten. Auch fester Gain und
festes Leaky-Verhalten bleiben hintergrundinvariant.

Die Clipping-Gegenbaseline loescht den Kontrast bei Hintergrund 0.5 und 0.9
vollstaendig, weil Hintergrund und Kontrast beide schon als 0.5 in das Feld
eintreten. Der Test kann einen echten Kontrastverlust somit erkennen.

## Feldwirkung

Der groesste unveraenderte Hintergrund-Linf bei Stufe 0.9 liegt bei
`0.8835159250001396`. Der lokale Zusatz wirkt aufgrund der vorhandenen
Feldnachbarschaft auch modalitaetsuebergreifend; der groesste gemessene
Cross-Modal-Delta-Linf betraegt `0.008426626677711768`.

Das ist eine technische lokale Feldausbreitung. Sie ist keine Bedeutung,
Zuordnung oder innere Interpretation.

## Abnahme

Der erweiterte Feldverbund besteht mit `73 passed` und 4 Subtests. Geprueft
sind die vollstaendige Paarmatrix, Ereignisinventare, Hintergrundinvarianz,
die exakte Halbierung der Gain-Gegenbaseline, die feste Leaky-Gegenbaseline,
der Clipping-Gegenbefund, fehlende adaptive Rollen sowie die Regressionen
W1-R bis W1-T, neutrale Feldruntime, Substrat, gemeinsamer Feldverteiler und
aktuelle Architektur-API.

## Aussagegrenze

W1-U zeigt keinen Funktionsverlust durch hohe gleichmaessige
Hintergrundaktivierung im untersuchten neutralen Feld. Deshalb ist eine
adaptive Saettigungsregulation fuer diesen gebundenen Substratpfad weiterhin
nicht technisch begruendet.

W1-U belegt keine Ueberreizung, Selbstregulation, Wahrnehmung, Feldzeit,
Praegung, Memory, Organisation, Semantik oder KI. Ausserhalb der drei
Hintergrundstufen, der beiden lokalen Kontrastorte und der festen Zeitmatrix
wird keine Aussage getroffen.

## Bester naechster Schritt

W1-V trennt Feldamplitude von technischer Ressourcenlast. Mit unveraenderten
Kontaktwerten wird nur die Dichte abgeschlossener synthetischer
Rezeptorereignisse variiert. Gemessen werden Ereignisinventar, Laufzeit und
begrenzte Arbeitsmenge, ohne daraus eine Organismusfunktion oder Regulation
abzuleiten. Erst eine reproduzierbare Ressourcenverletzung koennte eine
technische Eingangsbegrenzung motivieren; sie waere noch keine
Selbstregulation.

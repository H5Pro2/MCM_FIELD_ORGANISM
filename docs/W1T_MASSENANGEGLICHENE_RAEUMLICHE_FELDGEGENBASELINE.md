# W1-T: Massenangeglichene raeumliche Feldgegenbaseline

Stand: 2026-08-09

Entscheidung: `W1T_EQUAL_CONTACT_MASS_GEOMETRY_DIFFERENCE_OBSERVED`

Forschungslauf: nein

Realer Browser gestartet: nein

Adaptive Regulation implementiert: nein

## Auftrag

W1-T trennt die in W1-S vermischten Rollen Kontaktanzahl und Feldgeometrie.
Jede 100-ms-Unterstuetzung traegt in allen Mustern exakt dieselbe gesamte
Kontaktmasse:

```text
sum(abs(contact)) = 1.0
```

Fuenf Muster werden ueber 0.1, 1.0 und 4.0 s Belastung sowie 0.0, 1.0 und
4.0 s Nullkontakt untersucht. Das ergibt 45 frische Felder.

## Massenangleichung

| Muster | aktive Kontakte | Wert je Kontakt | Gesamtmasse |
|---|---:|---:|---:|
| local_auditory_mass1 | 1 | 1.0 | 1.0 |
| auditory_distributed_mass1 | 8 | 0.125 | 1.0 |
| local_visual_mass1 | 1 | 1.0 | 1.0 |
| visual_distributed_mass1 | 18 | 0.05555555555555555 | 1.0 |
| av_distributed_mass1 | 26 | 0.038461538461538464 | 1.0 |

Nur die raeumliche Verteilung unterscheidet sich. Feldgeometrie,
Kontaktzeit, Antwortzeit und Erholungsfenster bleiben identisch.

## Vier-Sekunden-Befund

| Muster | Feld-L1 | Feld-Linf | Grenzabstand |
|---|---:|---:|---:|
| local_auditory_mass1 | 0.9816843611112666 | 0.35727128118469537 | 0.6427287188153046 |
| auditory_distributed_mass1 | 0.9816843611112658 | 0.07971531778678712 | 0.9202846822132129 |
| local_visual_mass1 | 0.9816843611112648 | 0.30478396088127424 | 0.6952160391187258 |
| visual_distributed_mass1 | 0.9816843611112663 | 0.05155885247570923 | 0.9484411475242908 |
| av_distributed_mass1 | 0.9816843611112639 | 0.037757090811971726 | 0.9622429091880282 |

Die L1-Werte unterscheiden sich um weniger als `3e-15`. Gleiche gesamte
Kontaktmasse erzeugt damit in dieser verlustfreien Feldstufe dieselbe gesamte
Aktivierungsmasse.

Die lokalen Maxima unterscheiden sich dagegen deutlich. Lokale Konzentration
erzeugt den hoechsten Linf-Wert; raeumliche Verteilung vergroessert den
Abstand zur normierten Grenze. Der Unterschied ist eine Geometriewirkung,
keine veraenderte Gesamtaufnahme.

## Korrektur des W1-S-Risikos

Der W1-S-Arm `distributed_av` mit 26 Kontakten zu je 1.0 erreichte Linf
`0.9816843611112727`. Nach Angleichung derselben Geometrie auf Gesamtmasse
1.0 erreicht `av_distributed_mass1` nur
`0.037757090811971726`.

Die starke Grenzannaeherung in W1-S wurde daher durch die 26-fache gesamte
Kontaktmasse getragen. Sie ist kein Beleg dafuer, dass verteilte oder
multimodale Geometrie allein das Feld ueberlastet.

## Erholung

Alle fuenf Muster erholen sich ueber laengere Nullkontaktfenster monoton.
Nach vier Sekunden Nullkontakt liegen die Linf-Werte der vier Sekunden langen
Belastungen zwischen `0.0006915452408012282` und
`0.000842695549381124`.

Dies ist weiterhin feste Feldkinetik, keine adaptive Regulation.

## Abnahme

Der betroffene Feldverbund besteht mit `54 passed` und 26 Subtests. Geprueft
sind exakte Massenangleichung, Kontaktinventare, praktisch gleiche L1-Masse,
geometrieabhaengige Linf-Spitzen, Grenzabstand, monotone Erholung, fehlende
Rueckschreibung sowie W1-R-/W1-S- und Feldruntime-Regressionen.

## Aussagegrenze

W1-T belegt eine technische Geometriewirkung bei erhaltener gesamter
Kontaktmasse. Es belegt keine Ueberreizung, Selbstregulation, Wahrnehmung,
Feldzeit, Praegung, Memory, Organisation, Semantik oder KI.

Eine hohe Aktivierung allein ist noch kein funktionales Problem. Fuer einen
Regulationskandidaten muesste zuerst gezeigt werden, dass Weltunterschiede
unter hoher Last schlechter im Feld erhalten bleiben oder Ressourcen real
verletzt werden.

## Bester naechster Schritt

W1-U prueft die Erhaltung eines festen kleinen lokalen Kontrasts auf
verschiedenen gleichmaessigen Hintergrundlasten. Der Feldunterschied zwischen
Hintergrund und Hintergrund plus Kontrast wird gegen Nullhintergrund,
statisches Clipping, festen Gain und festes Leaky-Feld verglichen. Bleibt der
Kontrast im unveraenderten Feld erhalten, ist eine Sattigungsregulation fuer
den aktuellen Substratpfad weiterhin nicht begruendet.

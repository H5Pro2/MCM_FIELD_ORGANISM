# Methodik 011: Sparsamer auditiver Schnellfeld-Kandidat

## 1. Zweck

Geprüft wird die einfachste derzeit begründbare Feldlesart:

```text
verteilte auditive Rezeptorlage
+ unabhängiger lokaler Nachhall
-> passiver auditiver Schnellfeld-Kandidat
```

Es wird keine Kopplung zwischen Frequenzträgern, keine Spikegrenze und keine
Beziehungsmechanik ergänzt.

## 2. Hypothese

Die verteilte lokale Lage kann die schnelle sensorspezifische Feldfunktion
tragen, solange keine konkrete Weltfunktion zusätzliche Wechselwirkung
erfordert.

Der Kandidat darf nur:

- aktuelle Rezeptorenergie trägergetreu erhalten,
- unmittelbare lokale Geschichte endlich nachhallen lassen,
- einen unveränderlichen `MCMFieldWindow`-Vertrag erfüllen,
- ohne Bedeutungen am neutralen Verteiler andocken.

## 3. Bestehende Rezeptorzeit

Die auditive Rezeptorlage stammt bereits aus einem gleitenden Fenster von
100 ms. Ein 10-ms-Fortschritt löscht daher die vorherige akustische Lage nicht
sofort.

Ein zusätzlicher Nachhall ist nur dann funktional sichtbar, wenn:

```text
Rezeptorfenster nach Weltkontakt exakt null
+ Feldnachhall weiterhin ungleich null
```

Dieser Unterschied belegt nur eine verlängerte schnelle Gegenwart. Er ist kein
Lernen und keine Beziehungsgeschichte.

## 4. B1-Identitätsbedingung

Für jeden Träger `i` gilt ausschließlich die bekannte Baseline:

```text
h_i(t+1) = r * h_i(t) + (1-r) * x_i(t)
```

Dabei ist `x_i` die aktuelle technische Rezeptorenergie und `r` der offen
angegebene Zerfallsfaktor einer Versuchskonfiguration.

Der Feldkandidat muss für jeden geprüften Schritt exakt dieselbe Ausgabe wie
die unabhängige B1-Baseline liefern. Eine Abweichung bedeutet:

- Implementierungsfehler,
- versteckten Zustand,
- oder unzulässig ergänzte Mechanik.

## 5. Keine feste Anatomie

Mehrere `dt`/`tau`-Kombinationen werden ausschließlich als Parameterfamilie
verglichen. Der Versuch wählt keine Nachhallzeit für eine spätere Runtime aus.

Ein positiver Lauf trägt deshalb keine Aussage, dass ein bestimmtes `tau`
biologisch, organisch oder MCM-spezifisch richtig ist.

## 6. Pflichtprüfungen

1. Exakte B1-Identität jedes Trägers und jedes Schritts.
2. Kontakt eines Trägers wirkt niemals auf einen anderen Träger.
3. Aktuelle verteilte Rezeptorlage bleibt unverändert erhalten.
4. Gleiche Folge erzeugt nach vollständigem Neustart denselben Digest.
5. Träger- oder Geometriewechsel innerhalb einer Folge wird abgelehnt.
6. Nicht fortlaufende Schnappschüsse werden abgelehnt.
7. Observer ist wirkungslos oder vollständig abwesend.
8. Ausgabe kann an genau einen auditiven MCM-Dock übergeben werden.
9. Ausgabe enthält keine Rohsamples, Labels, Beziehungen oder Ressourcenwerte.
10. Nach vollständiger Rezeptorrelaxation wird mögliche Restwirkung B1-exakt
    ausgewiesen.

## 7. Abgrenzungsbaselines

- **B0:** nur aktuelle Rezeptorlage ohne Nachhall.
- **B1:** unabhängiger lokaler Leaky-Nachhall; muss exakt identisch sein.
- **B2:** globale Summe; darf verteilte Lagen nicht ersetzen.
- **B3:** fester Verzögerungspuffer; bleibt einfachere Erklärung für exakt
  kurzzeitige Reihenfolgeinformation.

## 8. Entscheidungsregel

Ein erfolgreicher Lauf kann nur zeigen:

> Eine verteilte Gegenwart mit lokalem B1-Nachhall erfüllt technisch den
> kleinsten auditiven Feld- und Dockvertrag.

Er zeigt nicht:

- zusätzliche Feldwirkung,
- MCM-spezifische Dynamik,
- organische Entwicklung,
- selbst gebildete Topologie,
- Semantik oder Feldintelligenz.

## 9. Stoppkriterium

Keine Kopplung oder langsamere Zeitlage wird ergänzt, solange B1 den gesamten
Kandidaten exakt erklärt und kein davon unabhängiger Funktionsmangel vorliegt.

## 10. Evidenzziel

Maximal **E1** für Implementierung, Invarianten und Dockfähigkeit des passiven
Kandidaten. Die auditive Feldmechanik im stärkeren Sinn bleibt **E0**.

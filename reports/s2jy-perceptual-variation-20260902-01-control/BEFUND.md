# S2-JY Funktionsbefund

Lauf-ID: `s2jy-perceptual-variation-20260902-01`

Technischer Status: `RECORDING_COMPLETE`

Funktionaler Status: `S2JY_VARIATION_IDENTITY_CONFIRMED`

Der private S2-JY-Hauptlauf wurde genau einmal und ohne Retry ausgefuehrt.
Der vorhandene read-only Verifikator wurde danach genau einmal aufgerufen und
meldete bei `116` Operationen keine Abweichung. Das Hauptgate wurde im
Kontrollpfad wieder auf `False` gesetzt; die Laufautorisierung wurde entfernt.

## Gebundener Umfang

- fuenf getrennte frische Geschichten;
- `20` tatsaechliche Formationen;
- `9` read-only Proben;
- `116` Memoryoperationen;
- `29` direkte L1-/Prototypbaseline-Aufrufe;
- keine Parameter-, Schwellen- oder Fixtureaenderung;
- keine Rohpixel oder PCM-Samples im Ergebnis;
- keine Feldabfrage und keine Wiederholung.

Die atomare Ergebnisdatei umfasst `113694` Byte und besitzt SHA-256:

```text
7742dcbd683602ce565d4685c345f6ca996a9215e1f8fccc1ee965e27bd15477
```

## Materialisierte Abstaende

Die Abstaende wurden aus den tatsaechlich erzeugten `48 + 288`
Rezeptorwerten berechnet:

| Rolle | auditiver L1-Abstand | visueller L1-Abstand |
| --- | ---: | ---: |
| `R0` | `0` | `0` |
| `E0` | `0` | `0` |
| `V1` | `0` | `0.0078431372549019485` |
| `A1` | `0.00047956059581593546` | `0` |
| `C1` | `0.00047956059581593546` | `0.0078431372549019485` |
| `Z1` | `0.062109660250351952` | `0.54166666666666663` |

## Funktionsergebnis

In den Geschichten `g0` bis `g3` entstand jeweils genau ein stabiles
auditives und visuelles Slow-Paar mit Support `3`. R0 und die jeweilige
nicht bitidentische Variante wurden sowohl in Fast als auch in beiden
stabilisierten Slow-Banken abgerufen. Das gilt getrennt fuer:

- die exakte Kontrolle `E0`;
- die visuelle Variation `V1`;
- die auditive Variation `A1`;
- die kombinierte Variation `C1`.

In `g4` blieben R0 und der deutlich verschiedene Distraktor `Z1` in zwei
Fast-Slots getrennt. Die auditiven und visuellen Slow-Banken enthielten je
zwei instabile Spuren mit Support `1`; kein oeffentlich stabiler Slow-Treffer
wurde ausgegeben.

Alle neun Probezugriffe hatten identische Vor- und Nachzustandsdigests. Die
direkte L1-/Prototypbaseline stimmte bei jeder Probe mit dem Memorybefund
ueberein. Technische Fehler oder fachliche Abweichungen wurden nicht
beobachtet.

## Aussagegrenze

Der interne Statusname enthaelt historisch den Begriff `IDENTITY`. Der Lauf
belegt jedoch kein erlerntes Wahrnehmungsidentitaetskonzept. Die Varianten
wurden prospektiv innerhalb der bereits vorhandenen festen Schwellen
konstruiert. Bestaetigt sind daher ausschliesslich:

- Toleranz gegenueber begrenzten, nicht bitidentischen AV-Wahrnehmungen;
- gemeinsame wiederholungsabhaengige Verdichtung dieser Wahrnehmungen;
- Trennung eines deutlich ausserhalb der Matchbereiche liegenden
  Distraktors;
- read-only Abruf im vollstaendigen 336-Werte-Profil.

Die direkte L1-Baseline erklaert das Ergebnis vollstaendig. Ein Nachweis von
Lernen erfordert als naechsten fachlichen Schritt prospektiv zurueckgehaltene
Varianten, deren Behandlung sich durch vorherige Erfahrung verbessert.

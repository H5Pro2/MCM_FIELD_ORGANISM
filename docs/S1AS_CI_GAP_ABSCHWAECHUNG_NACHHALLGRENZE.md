# S1AS: C_i-Gap-Abschwaechung und Nachhallgrenze

## Status

Technischer Kontrolllauf zur Gap-Laenge in der synthetischen Audio-/Video-
Testwelt. Der Lauf ist kein Vergessens-, Memory- oder Organismusnachweis.

## Aufbau

Der Reiz-Gap-Reiz-Aufbau wurde mit `1, 2, 4` und `8` aufeinanderfolgenden
kontrollierten Gap-Phasen wiederholt. Kontakt, veraenderter Kontakt und
gemeinsamer Probe blieben unveraendert. Verglichen wurden P0, der
amplitudenkalibrierte leaky-Arm und C_i.

## Messwerte

```text
Gap-Phasen  C_i max am Gap-Ende  leaky max am Gap-Ende  C_i-Probe-P0  leaky-Probe-P0  C_i History  leaky History
1           0.013329670         0.001380609            0.002690631    0.002690176     0.018411942   0.018373766
2           0.015618947         0.001669323            0.002652914    0.002681854     0.018411993   0.018373766
4           0.019733089         0.002229529            0.002590411    0.002672619     0.018412088   0.018373766
8           0.026744466         0.003327671            0.002486684    0.002658362     0.018412252   0.018373766
```

## Befund

Die C_i-Auslenkung sinkt in diesem Aufbau nicht monoton mit laengerer Gap-
Phase. Sie steigt sogar. Der Grund ist methodisch: Eine Gap-Phase mit
stummem beziehungsweise dunklem Quellmaterial ist nicht gleichbedeutend mit
keiner Feldzufuhr. Das bestehende Feld und sein Nachhall liefern weiterhin
Aktivierungswerte an den C_i-Pfad.

Damit wurde keine feldinterne Abschwaechung isoliert. Die Werte duerfen nicht
als Vergessen, Persistenz oder Memory interpretiert werden. Der Test zeigt
stattdessen, dass die aktuelle Testwelt fuer eine saubere Gap-Abklingmessung
eine explizite Nullkontakt-Definition benoetigt.

## Konsequenz

Weitere Gap-Laengen waeren in der aktuellen Form nicht aussagekraeftig. Der
naechste zulaessige Schritt ist ein statischer Vertrag fuer einen passiven
Nullkontakt: keine neuen Audio-/Videorezeptorframes, klar definierte
Feldweiterfuehrung und getrennte Messung von Feldnachhall und C_i-Zustand.
Erst danach darf die Abklingform der drei Arme verglichen werden.

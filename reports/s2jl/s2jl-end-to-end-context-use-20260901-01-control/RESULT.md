# S2-JL End-to-End-Kontextlauf - Abschlussbefund

Lauf-ID: `s2jl-end-to-end-context-use-20260901-01`

Technischer Status: `NOT_EVALUABLE`

Der freigegebene Hauptlauf wurde genau einmal aufgerufen. Der unabhaengige
read-only Verifikator wurde danach genau einmal ausgefuehrt. Er weist 171
Operationen und 346 Ereignisse aus; die gebundene Vollstaendigkeit von
`223/446` wurde nicht erreicht.

Der Lauf stoppte bei `ie-op-171` (`CONTEXT_ADMISSION_INVOKE`) mit dem neutralen
Fehlercode `IG-E009`. Anschliessend wurde ausschliesslich der registrierte
Fehlerabschluss bis `NOT_EVALUABLE` erzeugt. Ein `COMPLETE`-Marker existiert
nicht. Das Gate ist wieder `False`, alle gebundenen Quellhashes sind vor und
nach dem Lauf identisch, und es gab keinen Retry.

Da `RECORDING_COMPLETE` nicht vorliegt, werden weder die teilweise vorhandenen
Memory- und Signalbelege noch die erwarteten Ergebnisse fuer `c01` bis `c08`
fachlich ausgewertet. Insbesondere existiert kein gueltiger Befund zur
End-to-End-Kontextverwendung oder zur Gleichheit mit der Direktbaseline.

Der Kontextzweig wird entsprechend der Freigabe unabhaengig vom Ergebnis mit
`CLOSED_WITHOUT_FUNCTIONAL_RESULT` geschlossen. Der Abbruch ist ein technischer
Laufbefund und kein negativer Memory-, Kontext- oder Feldbefund. Es erfolgt
keine Wiederholung und keine nachtraegliche Reparatur dieses Laufs.

Der naechste Hauptabschnitt ist die verbindliche quellenunabhaengige
Audio-/Video-Wahrnehmungsgrenze.

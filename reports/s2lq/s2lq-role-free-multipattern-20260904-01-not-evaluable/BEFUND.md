# S2-LQ Rollenfreier Mehrmusterlauf 20260904-01

Lauf-ID: `s2lq-role-free-multipattern-20260904-01`

Technischer Status: `NOT_EVALUABLE`

Funktionsstatus: keiner

Der genehmigte Hauptaufruf wurde genau einmal gestartet. Er brach im
quellen- und geometriegebundenen Preflight vor dem ersten Memoryaufruf und
vor der atomaren Ergebnisablage ab:

```text
AttributeError: 'MaskedAuditoryCue48V1' object has no attribute 'observed_values'
```

Die Ursache liegt im privaten S2-LQ-Runner: `_source_geometry_preflight`
liest bei einem auditiven Teilhinweis `operation.cue.observed_values`. Der
qualifizierte Typ `MaskedAuditoryCue48V1` stellt dieses Feld nicht bereit.

Das vorgesehene Laufverzeichnis wurde nicht erzeugt. Die danach genau einmal
ausgefuehrte unabhaengige read-only Verifikation lehnte den fehlenden
Ergebnisbeleg fail-closed ab. Es existieren weder atomarer Ergebnisdigest noch
fachliche Auswertung. Insbesondere wurden keine Aussagen zu A/B-Support, C,
D oder der geplanten auditiven D-nach-A-Interferenz gewonnen.

Es gab keinen Retry, keine Parameter-, Fixture- oder Quellcodeaenderung. Das
Hauptgate war vor dem Aufruf `False` und wurde im `finally`-Pfad wieder auf
`False` gesetzt. Alle gebundenen Quellhashes waren nach dem Abbruch
unveraendert. Die bekannte Bootstrap-Datei blieb ausgeschlossen.

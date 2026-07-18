# Technischer Rezeptorprozessvertrag 012

## Status

Architekturvertrag vor `GF_001`.

Der vollständige Vertrag steht unter
[Minimaler Rezeptorprozessvertrag](../architektur/029_MINIMALER_REZEPTORPROZESSVERTRAG.md).
Seine Runtimefreigabe bleibt `CONTRACT_ONLY`, seine Evidenzstufe für eine
zukünftige gemeinsame Prozessgrenze `E0`.

## Festgelegte Grenze

Der Vertrag vereinheitlicht nur:

- lokalen Zustandsbesitz,
- kausale Quellursache,
- endliche Lösung früherer Wirkung,
- unveränderliche Snapshot-Übergabe,
- native Quellherkunft,
- fehlende Feldrückwirkung.

Er vereinheitlicht ausdrücklich nicht:

- Zustandsform,
- Fensterbreite,
- Ausgaberate,
- Zerfall,
- Halten,
- Modalitätsgewichtung.

Damit dürfen Audio und Video unterschiedliche Rezeptorprozesse besitzen,
ohne an der gemeinsamen Dockgrenze unterschiedliche Bedeutungs- oder
Prioritätsrollen zu erhalten.

## Kontrollen

Sieben Vertragskontrollen zeigen:

1. Der Referenzvertrag ist unveränderlich und reproduzierbar.
2. Zustandslose und zustandstragende lokale Prozesse bleiben zulässig.
3. Kausaler Quellfortschritt und endlicher Geschichtsverlust sind bindend.
4. Erforderliche Grenzen können nicht entfernt werden.
5. Halten, gemeinsame Dynamik, Gewichtung und Feldfeedback können nicht als
   Ursache oder Beobachtung eingeschleust werden.
6. Der öffentliche Vertrag besitzt keine Übergangsparameter.
7. Evidenz, Runtimefreigabe und Writeback können nicht erhöht werden.

## Befund

Die Architektur besitzt jetzt eine gemeinsame Rezeptorprozessgrenze, ohne
eine gemeinsame Rezeptordynamik zu programmieren.

```text
gemeinsamer Vertrag
!= gemeinsame Mechanik
```

Der Vertrag löst die offene Feldzeitfrage nicht. Er verhindert aber, dass sie
durch verstecktes Videohalten oder Überschreiben der auditiven
Fenstergeschichte scheinbar gelöst wird.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Vor weiterer Feldmechanik muss nun geprüft werden, ob die vorhandenen
modalitätseigenen Snapshotfolgen an der gemeinsamen Dockgrenze eine rein
kausale **Änderungsinformation** tragen können, ohne letzten Wert zu halten
oder Ereignisanzahl als Wirkungsmenge zu verwenden.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.

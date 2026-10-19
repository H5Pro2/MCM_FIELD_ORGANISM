# S2-TX-Ergebnis 20260919-01

Technischer Laufstatus: `RECORDING_COMPLETE`, read-only Verifikation:
`VERIFIED`. Qualifikationsstatus: `NOT_QUALIFIED`.

Der reale Einmallauf wurde technisch vollständig mit `27` Ereignissen, `22`
Audio-/NJ-Endpunkten, `20` Formationen, zwei Hintframes, fünf
Segmentabschlüssen und zwei Owner-Abschlüssen gespeichert. Der unabhängige
Verifikator bestätigte die Quellenbindungen, Werte, Übergänge, Inventare und
Hintentscheidung.

Beobachtete Übergänge:

* P3 bestätigte Generation 1 in beiden Armen. Der unveränderte Arm hielt
  `1,2`; der Aktualitätsarm hielt `2,1`.
* P4 verdrängte im unveränderten Arm Generation 1 und im Aktualitätsarm
  Generation 2.
* H1 ergab im Aktualitätsarm einen Match zu Generation 1; der unveränderte
  Arm enthielt keine passende Spur.
* Die Wiederkehr P5 bestätigte im unveränderten Arm Generation 2. Im
  Aktualitätsarm war diese Spur zuvor verloren; P5 bildete Generation 4 und
  verdrängte Generation 1.

Damit zeigt der gespeicherte Record den vorgesehenen Aktualitätskonflikt.
Er wird aber nicht als qualifizierter Funktionsbefund bewertet: Der formale
Testaufruf erreichte nur die ursprünglichen S2-TX-Prüfmethoden. Die später
ergänzten neutralen Kontrollen für unvollständige Formation,
Mehrfachgleichheit und Hint-Unveränderlichkeit waren nicht Teil dieses
Aufrufs. Es gibt keinen Retry und keine Quellenänderung.

`record.json` misst `34494` Byte, `verification.json` `68` Byte und liegt
damit innerhalb der Zusatzgrenze von `262144` Byte. Feld, A/B-Memory und
Hypothesen waren ausgeschlossen.

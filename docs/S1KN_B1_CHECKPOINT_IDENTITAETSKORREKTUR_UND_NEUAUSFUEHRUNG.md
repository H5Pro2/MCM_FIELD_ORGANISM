# S1-KN: B1-Checkpoint-Identitaetskorrektur und Neuausfuehrung

## Ergebnis

S1-KN implementiert die in S1-KM gebundene Identitaetsregel. Der Runner
uebergibt jetzt bei jedem Checkpoint die tatsaechlich angeforderte Replik-ID.
Der vollstaendige Outputvalidator verwirft jeden Output, dessen Checkpoint-ID
nicht mit der Eltern-Replik-ID uebereinstimmt.

Nur B1/P_IE r4 und r8 wurden je einmal neu ausgefuehrt. Die Korrektur
umfasste genau acht Intervallaufrufe.

## Korrigierte Ausgaben

- r4: `deb5611740ed7bdeccd13cfd2cea77ed3f6c1b7147e8c58e6d812c955b1e8790`
- r8: `fdb9cb500337b7d9285d23c0b0d8f357db1c446cde5d5437a6fff11db7757a1f`

Beide Ausgaben tragen in allen vier Checkpoints ihre jeweilige Eltern-ID.
Die korrigierten Provenienz-Digests unterscheiden sich voneinander und von
beiden historischen S1-KH-Digests.

Der Refinement-Vergleichsdigest bleibt fuer beide Ausgaben bitidentisch:

`276f2891e11e2e5a0b22f8dbf65594dc26e217bec28a526a02632bc20334d589`

Damit bleiben alle im Vergleich gebundenen numerischen Checkpoints,
Komponenten und Adapterdiagnostikdaten erhalten. Alle acht signed
Komponenten sind weiterhin null.

## Historische Abgrenzung

Die historischen S1-KH-v2-Ausgaben und ihre Digests wurden nicht
ueberschrieben. Der S1-KH-Receipt bleibt als historischer Record erhalten,
ist aber keine korrigierte Provenienzgrundlage. B1/r2 und alle B2/P_IE-
Repliken wurden nicht erneut ausgefuehrt.

Entscheidung:

`B1_R4_R8_CHECKPOINT_IDENTITIES_CORRECTED_EIGHT_INTERVALS_COMPARISON_PRESERVED`

Receipt-Digest:

`d751b4d059cd17200d884e69ff2a4c7d261127c12962b03e33b960ae7d75c939`

## Grenzen

C01 und C05 wurden noch nicht neu beziehungsweise erstmals zusammengesetzt.
Die 24-Fall-Matrix, weitere Rollen, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KO darf ausschliesslich den korrigierten technischen C01-Fallrecord aus
dem unveraenderten B1/r2-Output und den korrigierten B1/r4/r8-Ausgaben
zusammensetzen. Keine neue Replik oder kein neues Intervall und noch keine
C05-Komposition.

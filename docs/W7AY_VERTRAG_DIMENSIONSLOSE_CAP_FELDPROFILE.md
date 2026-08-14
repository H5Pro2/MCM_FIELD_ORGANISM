# W7-AY: Vertrag fuer dimensionslose CAP-Feldprofile

## Entscheidung

`CAP_FIELD_LIFECYCLE_PROFILE_CONTRACT_BOUND`

W7-AY legt wertfrei fest, wie aus den vorhandenen W7-AG-Probetrajektorien
spaeter CAP-Lebenszyklusprofile gebildet werden duerfen. Es nimmt keine
Trajektorienwerte entgegen, startet keine Integration und trifft keine
Profil- oder Funktionsentscheidung.

## Quellenkorrektur

W7-AK enthaelt CAP-minus-P0-Abstaende innerhalb desselben Pfades. Diese Werte
sind keine AB-gegen-UB-, AG-gegen-UG- oder sonstigen Lebenszykluseffekte.
W7-AK wird deshalb nur als CAP/P0-Provenienz- und Ausrichtungskontrolle
gebunden. Die acht Pfadkontraste muessen direkt aus den W7-AG-S/H-Samples
gebildet werden.

## Effektmetrik

Fuer jedes Pfadpaar und jeden Checkpoint muessen Ticks sowie S/H-Geometrie
exakt uebereinstimmen. Der skalare Effekt ist:

```text
effect = max(sampleweises S-Linf, sampleweises H-Linf)
```

Dies entspricht der bereits verwendeten gemeinsamen Fast-State-Metrik des
K2-B-Vertrags. SH-L2 bleibt Diagnose und wird nicht zur Profilkoordinate.

## Profilbildung

AB verwendet alte A-Wirkung unter B, alte A-Wirkung nach Unterbrechung und
neue B-Wirkung nach A. BA wird spiegelbildlich gebildet. Die neutralen
Neu-Kontakte bleiben Auditkontrollen und sind keine vierte Profilkoordinate.

Der jeweilige Anfangseffekt muss strikt ueber dem real bestimmten
W7-AT-Effektboden `1.8915768951188738e-07` liegen. Andernfalls ist das Profil
`NOT_RESOLVED`; ein Epsilon darf den Nenner nicht retten. Jedes Profil wird
durch seinen eigenen aufgeloesten Anfangseffekt normalisiert.

## Aussagegrenze

W7-AY definiert nur eine Mess- und Profiloberflaeche. Es belegt keine
Profilerklaerung, Feldfunktion, Freisetzung, Wiederverwendung, Memory,
Feldzeit, Organisation, Semantik, Selbstregulation oder KI.

## Naechster Schritt

W7-AZ darf aus bereits vorhandenen W7-AG- und W7-AK-Objekten die acht rohen
CAP-Pfadkontrastkurven und zwei dimensionslosen CAP-Profile rein in Memory
bilden. Es darf keine neue Integration und keinen Observervergleich starten.

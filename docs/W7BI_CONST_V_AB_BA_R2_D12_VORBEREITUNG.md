# W7-BI: CONST-V-AB/BA-R2 und rohe D12-Vorbereitung

## Zweck

W7-BI setzt den W7-BH-Vertrag technisch um. Es werden AB/R2 und danach BA/R2
mit der bestehenden privaten CONST-V-Runtime ausgefuehrt. Anschliessend werden
pro Richtung nur die gebundenen R1-/R2-Rohrollen in einer D12-Struktur
zusammengefuehrt.

## Ablauf

1. `AB/R2` wird als fuenfteilige Hauptkette mit fuenf isolierten Checkpoint-
   Proben erzeugt.
2. Danach wird `BA/R2` mit derselben Struktur erzeugt.
3. Je Richtung werden R1-Rollenidentitaet und R2-Rollenidentitaet gebunden.
4. Die rohe D12-Struktur enthaelt keine Distanzzahl.

Je Probe werden weiterhin 91 rohe S/H/Skalar-Samples erwartet. Der technische
Skalar bleibt unveraendert durch die S/H-Ausrichtung der Checkpointkopie.

## Evidenzgrenze

W7-BI bereitet D12 nur vor. Es berechnet weder R1/R2-Abstaende noch Epsilon,
Effektboden oder Profile. Das Ergebnis `RAW_D12_PREPARED` ist kein
Konvergenz-, Feldfunktions- oder Memorybefund.

## Technischer Laufbefund

- AB-R2-Rohrollen-Digest: `666bfd0424cdd50aa3380e50ad1b29b223eee0554141863518ceca1c8bd8910a`
- BA-R2-Rohrollen-Digest: `2d0983995be11c5b36d07cb60a0b07e4c0e5a436ae65c89797b27108a6b1a03d`
- terminaler D12-Digest: `b4daf8e5621369d4daa8e504910a4f84bb4fcc59c0722f769dbb20924cfcbf77`
- 6 fokussierte Tests bestanden.

## Naechster Anschluss

W7-BJ registriert die R4-Wiederholung fuer AB und BA. Erst danach darf die
vorbereitete R1/R2/R4-Struktur auf die gebundene Konvergenzregel angewendet
werden. W7-BJ ist mit Digest `140370ef...3b74` statisch abgeschlossen.

# S1-EC94: Finales r4/r8-Ressourcen- und Objektidentitaetsgate

## Gate

EC94 bindet EC89, EC92 und EC93 an einen aktuellen Ressourcen-Snapshot und
die fuenf geschuetzten Artefakte. Geprueft werden zwei getrennte Handoffs,
16 getrennte Slots und Bindings, acht Formation-Slot-Referenzen sowie 16
frische Feldobjekte. Das gemeinsame neutrale Anfangsfeld und der gemeinsame
Anfangszustand bleiben absichtlich dieselbe Baseline-Identitaet.

Der technische Laufrahmen bleibt unveraendert:

- 9.648 Bildungsschritte;
- 9.600 Probeschritte;
- maximal 19.248 Feldschritte;
- mindestens 4 GiB freier Arbeitsspeicher;
- mindestens 1 GiB freier Datentraeger;
- keine Persistenz, kein Retry und keine Nachparametrierung;
- keine Teilrueckgabe, sondern atomare Skalarquittungen.

Ein bestandenes EC94-Gate setzt ausschliesslich
`TECHNISCH_BEREIT_NEUE_R4_R8_EINMALLAUFFREIGABE_FEHLT`. Es autorisiert weder
Koordinator noch Adapter und fuehrt keine Feldoperation aus. Es besteht kein
Memory-, Feldzeit-, Organisations-, Topologie-, Semantik-,
Selbstregulations- oder KI-Nachweis.

Am besten geht es danach mit S1-EC95 weiter: EC94 mit einem aktuellen realen
Ressourcen-Snapshot auswerten. Nur falls alle technischen Gates bestehen,
muss vor jeder Ausfuehrung eine neue ausdrueckliche Besitzerfreigabe fuer
genau einen nicht persistenten r4/r8-Lauf mit maximal 19.248 Feldschritten
eingeholt werden.

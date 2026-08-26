# S1-ZG: Statischer privater Anwendungspreflight-Bindungskorrekturvertrag

## Ergebnis

S1-ZG schliesst die fuenf in S1-ZF identifizierten Bindungsluecken statisch.
Gebunden sind nun das kuenftige private Modul, die vollstaendigen Signaturen,
alle Drive-, Receipt- und Ergebnisinvarianten, eine endliche Fehlerprioritaet
mit getrennten Zaehlerzustaendigkeiten sowie eine dockkonsistente
Acht-Arm-End-to-End-Fixture.

Die Korrektur fuegt keine Mechanik hinzu. Sie legt nur so genau fest, was ein
spaeterer privater Helper und Anwendungsadapter tun duerften, dass die
Implementierung keine fachlichen Entscheidungen mehr erfinden muss.

## Acht-Arm-Fixture

Alle Arme verwenden dieselbe Ein-Neuron-Layeranatomie, denselben Zielschritt,
dasselbe Rezeptorkontaktbudget und dieselbe Anzahl an Drive-, Proposal- und
Layeraufrufen. Candidate und Generic erhalten paarweise denselben numerischen
lokalen Wert. No-Context und Digest-Only erhalten keinen lokalen Wert. Die
erwarteten Folgelayerrelationen bleiben dadurch generisch erklaerbar.

## Grenze

S1-ZG autorisiert weder Modulcode noch Fixture- oder Layerausfuehrung. S1-ZH
muss den Vertrag statisch auf Widerspruchsfreiheit und eindeutige
Implementierbarkeit pruefen. Oeffentliche API, Snapshot, `SharedMCMField`,
Produktion und Feldpfad bleiben unveraendert.

LPRH-1F bleibt eine generisch reduzierbare Engineeringkopplung. Es entsteht
kein Feldwirkungs-, Memory- oder MCM-spezifischer Mechanismusbefund.

Maschinenlesbarer Vertrag:
[S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json](S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json).

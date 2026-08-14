# NASA-Weltwiederkehr: sechsarmige Replikationsausfuehrungsfunktion

## Entscheidung

Die konkrete sechsarmige Replikationsausfuehrungsfunktion ist implementiert. Sie ist an eine positive Replikationsvorabnahme, die Runnerverdrahtung und den Permutationsvertrag gebunden.

Es wurde kein Replikationslauf gestartet.

## Armbehandlungen

- `return.continued.full_state`: Stufe eins, kontaktfreie Aufloesungsphase, gleiche Stufe-zwei-Sequenz.
- `return.fresh_stage_two`: Stufe eins, frisches Feld vor Stufe zwei, gleiche Stufe-zwei-Sequenz.
- `control.activation_only_carry`: Stufe eins, kontaktfreie Aufloesungsphase, observerseitig `reset_afterimage_preserve_activation`, gleiche Stufe-zwei-Sequenz.
- `control.afterimage_only_carry`: Stufe eins, kontaktfreie Aufloesungsphase, observerseitig `reset_activation_preserve_afterimage`, gleiche Stufe-zwei-Sequenz.
- `control.stage_two_order_permuted`: Stufe eins, kontaktfreie Aufloesungsphase, deterministisch permutierte Stufe-zwei-Sequenz gemaess Permutationsvertrag.
- `control.stage_two_sequence_withheld`: Stufe eins, kontaktfreie Aufloesungsphase, kontaktfreie Feldfortschreibung ueber den Stufe-zwei-Horizont ohne Rezeptorereignisse.

## Ergebnisvertrag

Die Funktion gibt ausschliesslich technische Messrollen zurueck:

- Ereigniszaehlungen je Arm,
- Snapshot- und Layer-Digests,
- Aktivierungs- und Nachhallvektoren,
- paarweise L-inf-Differenzmatrizen,
- Layer- und Snapshot-Gleichheitsmatrizen,
- Interventionsaudit-Identitaeten fuer die beiden Komponentenarme.

Sie definiert keine Memory-, Bedeutungs- oder Organisationsschwelle.

## Gate-Grenze

Die Funktion prueft vor dem Lauf:

- positive und unverbrauchte Replikationsvorabnahme,
- identischen Medienpfad,
- Quellenidentitaet,
- Runner- und Vorregistrierungsidentitaet,
- vollstaendige sechsarmige Verdrahtung,
- Permutationsvertragsdigest.

Fuer die direkte Injektion in den One-Shot-Einstiegspunkt existiert ein gebundener Executor-Adapter.

## Verifikationsgrenze

Die Tests verwendeten ausschliesslich injizierte Stubs fuer Sequenzen, Feldschritte, Interventionsausgabe und Feldfortschreibung. Es wurde kein Medium decodiert, kein Rezeptor gespeist und kein Feldlauf ausgefuehrt.

Memory-, Bedeutungs-, Organisations- und KI-Claims bleiben gesperrt.

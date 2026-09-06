# S2-NF: Neutrale Quellenbindungsqualifikation

Status: `S2NF_SOURCE_BINDING_QUALIFIED`. Genau ein Testaufruf,
`10/10`, Exit-Code `0`, `OK`. Kein Retry. Ausgangscommit `bbeb856`.

Aufruf aus dem workspace-Root:

```text
C:\Python314\python.exe -m reports.s2nf.qualify_once
```

Dieser archivierte Aufrufer materialisierte vorab die zehn eindeutigen
Test-IDs und die Quellhashes in `preregistration.json` und startete genau:

```text
C:\Python314\python.exe -m unittest tests.test_s2nf_private_source_binding -v
```

`stdout.txt` und `stderr.txt` sind die unveraenderten Prozessausgaben.
`result.json` bindet Exit-Code, Testzahl, Loghashes und identische
Vor-/Nachhashes von 47 Dateien. Ergebnisdigest:
`b0ea1001bf0a051d088662406f2904ac86998006f54f4c8431bf9de90b21f953`.

## Begrenzung und Abdeckung

Die zehn Tests prueften Built-in-math mit beiden notwendigen Nachweisen,
dateibasierte Herkunft und Fremdpfad, Quellenidentitaet und unveraenderliche
SourceSpecs, feste Partialreihenfolge, getrennte Exaktkopien, Payloadhash-
und Groessenfehler, literale Ereigniszeiten/Profil, getrennte Planwurzeln,
manipulierte Metadaten trotz neu berechnetem Digest sowie reine AST-Auswahl.

Keine NF-PCM-Quelle wurde erzeugt. Der harmonische Generator war im Test
gesperrt; die ausgewaehlten Chirpfunktionen wurden nicht aufgerufen.
Test 10 bestaetigte, dass weder `mcm_field_organism` noch das historische
rezeptorimportierende S2-LB-Modul geladen waren. Die synthetische neue
Payloadbindung in Planpruefungen war ausschliesslich ein neutraler Hash,
kein vermeintlich materialisiertes NF-Ergebnis.

Statischer Codecheck vor dem Aufruf: zehn eindeutige Testmethoden;
keine Generator-, Analyze- oder Vorversiegelungsaufrufe im Test;
Standardbibliothek plus bestehende reine ND-Generatorfunktionen;
S2-LB ausschliesslich ueber unveraenderte AST-Funktionskoerper, ohne dessen
Import- oder Materialisierungseinstieg. Keine historischen Dateien editiert.

Die unabhaengige Planpruefung rekonstruiert keine Nutzdaten. Sie prueft
kanonische Formen, Rezept-/Zeit-/Quellenbindungen und die getrennte
Evaluationszuordnung. Das qualifiziert nur die kleine Bindung, keinen
Regelvergleich, keine Rezeptorgeometrie und keine Memoryfunktion.

Die anschliessend separat autorisierte Quellenvorversiegelung wird unter
eigener ID dokumentiert. Keine weiteren Tests wurden gestartet.

WEITER: Am besten geht es jetzt mit dem separaten Befund der einmaligen
rezeptorfreien Vorversiegelung weiter.

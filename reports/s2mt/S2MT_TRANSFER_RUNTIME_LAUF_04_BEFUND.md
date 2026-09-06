# S2-MT: Transferlauf 04

## Entscheidung

Der einmalige Lauf
`s2mt-presealed-transfer-runtime-20260906-04` ist methodisch
`NOT_EVALUABLE`.

Der Hauptlauf erzeugte einen vollstaendigen atomaren Record mit
`technical_status = RECORDING_COMPLETE`. Alle 28 Runtimeereignisse besitzen
einen erfolgreichen Feldzweig und keine Fehlercodes. Die anschliessende
einzige unabhaengige read-only Verifikation stoppte jedoch fail-closed bei
der ersten Teilhinweispruefung mit `hypothesis modality differs`.

Die im Record enthaltene fachliche Evaluation wird deshalb nicht
uebernommen oder interpretiert. Es gab keinen Retry und keinen
Parameterwechsel. Die frueheren S2-MT-Laeufe bleiben unveraendert
`NOT_EVALUABLE`.

## Vorbindung

Vor dem Hauptaufruf galten:

- Quellcommit `ba634abed929566b0d96740deeb7cdfb23797bdc`;
- Runner und Verifikator banden ausschliesslich die neue Lauf-ID;
- die Lauf-ID `...-03` kam nur noch in historischen Belegen vor;
- das neue Ergebnisverzeichnis war nicht vorhanden;
- Hauptgate im Quellstand `False`;
- S2-MT-Runner-SHA-256
  `29f3ef7fa28bfde45236b3cce39febe542f4ab6470a3c0f9b8de7aac7549dcfd`;
- S2-MT-Verifikator-SHA-256
  `afcdae7465573b0dc88965782e08e06de2464688252626f2ec1711de261c27b6`;
- skalierter Quellenplan-SHA-256
  `56ac39b47e9df7cab424943a66636de80200c925035d4328521c90500dd92674`;
- S2-MR-Runtime-SHA-256
  `da7699b6ef2a17c3b241f257a8aa9c954439e8a2b5cc37dab2a372a7691cf49f`.

Der skalierte Quellenplan, Faktor `0.989912331104279`, Schwellen,
Ereignisfolge und Auswertung blieben unveraendert.

## Einmaliger Hauptaufruf

`run_main_once` wurde genau einmal mit der autorisierten Lauf-ID aufgerufen.
Der Prozess endete mit Exit-Code `0` und meldete danach:

```text
GATE=False
USED=True
```

Der atomare Ergebnisbeleg bindet:

- Lauf-ID `s2mt-presealed-transfer-runtime-20260906-04`;
- Status `RECORDING_COMPLETE`;
- Record-Digest
  `ec935094031724d70ff0825d52a11373885be0da0e4b8d00c5bc89028a79b89e`;
- Datei-SHA-256
  `a5c16ef89e7059cd358f82fc25422607b5405572d21a86b18b4f80c90d3e11c5`;
- Dateigroesse `149416` Byte;
- exakt 28 Ereignisse, davon 20 Formationen und acht Teilhinweise;
- 28 Feldzweige mit `FIELD_CONTACT_RECORDED`;
- null Runtimeereignisse mit Fehlercodes;
- gebundene `8064` Feldkontakte.

Die explizite S2-MT-Felduhr beseitigte damit den Feldfehler aus Lauf 03.

## Einmalige read-only Verifikation

`verify_result_file` wurde danach genau einmal auf die unveraenderte
Ergebnisdatei angewendet. Der Aufruf endete mit Exit-Code `1`:

```text
S2MTVerificationError: hypothesis modality differs
```

Der Ergebnisdateidigest war vor und nach dem Verifikationsversuch identisch.
Es wurde kein zweiter Verifikationsaufruf ausgefuehrt.

## Statisch lokalisierte Verifikatorgrenze

Der Verifikator hatte kanonische Serialisierung, Quellenbindungen,
Runtimekette, alle Formationen, erfolgreiche Feldzweige und fehlerfreie
Runtimeereignisse bereits geprueft. Fuer die Teilhinweise setzt er jedoch
fest:

```python
expected_present = index < 24
```

Damit verlangt er fuer die ersten vier Hinweise zwingend eine Hypothese.
Der erste auditive Hinweis `e21` enthaelt stattdessen eine gueltig
aufgezeichnete Enthaltung und keine Hypothese. `_verify_hypothesis` meldet
fuer diesen `None`-Wert den allgemeinen Fehler `hypothesis modality differs`.

Der Verifikator kann somit in seiner aktuellen Form keinen vollstaendig
aufgezeichneten, fachlich abweichenden Transferbefund unabhaengig bestaetigen,
sondern behandelt die vorgebundene Erfolgserwartung als technische
Beleginvariante.

## Aussagegrenze

Lauf 04 bestaetigt technisch den geschlossenen Feldpfad mit allen 28
erfolgreichen Feldgeschwisterzweigen. Er ist dennoch kein auswertbarer
Transferbefund, weil die einzige unabhaengige Verifikation nicht abgeschlossen
wurde. A/B-Stabilisierung, C-Instabilitaet, A_RECENT-Verdraengung und die acht
Hypothesenausgaben werden aus diesem Lauf nicht fachlich bewertet.

Runner, Verifikator, Ergebnisbeleg und historische Laeufe bleiben nach der
Ausfuehrung unveraendert. Ein weiterer Transferlauf ist nicht freigegeben.

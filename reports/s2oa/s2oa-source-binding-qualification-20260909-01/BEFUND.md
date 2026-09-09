# S2-OA: neutrale Quellen-/Ereignisqualifikation

ID `s2oa-source-binding-qualification-20260909-01`.
Genau ein Aufruf `C:/Python314/python.exe -m reports.s2oa.qualify_once`
aus dem workspace-Root; genau ein unittest-Unterprozess, **18/18**, Exit 0,
terminales OK. Kein Retry. Status `S2OA_SOURCE_BINDING_QUALIFIED`.

Inventar, Kommando, Grenzen, Umgebung und Quellhashes wurden vor dem Test
in [preregistration.json](preregistration.json) gebunden. Alle Testkoerper
sind in [stderr.txt](stderr.txt) einzeln erreicht; [result.json](result.json)
bindet unveraenderte Hashes vor/nach dem Aufruf.

## Tatsaechliche Deckung

1. Historisches np-a02-Rezept und JX-Ordinalkatalog.
2. Vollstaendige Ereignisfolge; vertauschte Ereignisse abgewiesen.
3. 22 auditive/26 visuelle Vorkommen; fremde Modalitaet abgewiesen.
4. Native Indizes fuer Anfang, spaeteres und fernes Fenster.
5. Negative, nicht teilbare, nicht ganzzahlige und boolesche Indizes abgewiesen.
6. Manipulierter Audioindex typisiert abgewiesen.
7. Manipuliertes gemeinsames Videofenster abgewiesen.
8. Fremde Felduhr abgewiesen.
9. Lueckenlos fortgesetzte Feldfenster; Abschnittsreset abgewiesen.
10. Neutraler JX-Frame mit Ordinal1: alle 288 Kanalzellen auf korrekte
    in-place Okklusion geprueft, sichtbare 0..31 unveraendert, andere Null;
    falsche Maske abgewiesen. Ordinal1 gehoert nicht zu OA.
11. Ein neutrales 16-Sample-Nullamplitudenrezept, 64 PCM-Bytes; vorhandene
    Generatorrechenfolge unveraendert per Quell-/AST-Bindung uebernommen.
12. 22 getrennte Audioidentitaeten und Quelldigests bei gleichem Payloadhash.
13. Falscher historischer Payloadhash und manipulierte Quellenzeit abgewiesen.
14. Getrennte Ausfuehrungs-/Evaluationswurzel, acht Hinweise, keine Erfolgsgates.
15. Manipulierte Quellenmetadaten und fremde Wurzelbindung abgewiesen.
16. Vollstaendige Metadatenhulle innerhalb Grenze; fehlende Quelle abgewiesen.
17. Dokumentierte math-Herkunft, auf diesem Build eingebaut und in der
    Built-in-Modulliste; keine erfundene Moduldatei.
18. Unveraenderlichkeit, geschlossenes Gate und keine Systemimporte.

Neutrale Payloads: genau ein PCM-Fenster mit 16 Samples und ein RGB-Frame.
Keine OA-Payloads; Planmetadaten und historische Belege nur gelesen.
Keine Rezeptor-/NJ-, Distanz-, Memory-, Feld- oder Runtimeaufrufe.
Importblock fuer Systemkomponenten im Testprozess. Keine Eininstanz- oder
Generationsimplementierung und keine Aussage ueber funktionale Erreichbarkeit.

## Bindungen und Grenze

- Resultatdigest: `49fdf3031315c08680b958651ed2d3a7e65f90c7cc15f61c5492adf405bb89ae`.
- OA-Planfilehash: `bb87f2a89621d2df6ee248d8b917e59db3758ecdeede2a9ac154fdde93a6a69d`.
- Quellenanschluss: `3aaa6505c6b56bdd35a346014d463cc8ca87a6cf786f1a3412913e6a0d11a607`.
- Verifikator: `20f98871ded362ee7b19595a73385674a4f20e527a16f8a7c45c4901d367a02e`.
- Testdatei: `e2b72f63d35d9b19311045c089b7d057e0508af31cf3ed89c7b4bd691ee4e71a`.

CPython 3.14.4, NumPy 2.4.4; Interpreter-/Bibliotheksdateien und Generator-AST
vollstaendig im Vorbeleg. Resultat 4.355 Byte; Vorregistrierung 7.790 Byte.
Qualifiziert ist nur die neue Quellen-/Ereignisbindung. Hauptgates False;
ME/MI und Systemintegration gesperrt, Prognosezweig ruhend.

Nach diesem Bestehen wurde der bereits freigegebene einmalige rezeptorfreie
Vorversiegelungsschritt separat ausgefuehrt; siehe den
[Quellenbefund](../s2oa-source-preseal-20260909-01/BEFUND.md).

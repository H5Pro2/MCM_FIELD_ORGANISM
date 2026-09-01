# S2-IZ Vertragsbefund

S2-IZ bindet die Gleichheit visueller Rezeptorwerte ueber ihre prospektiv
gebildete ganzzahlige Blocksumme. Bei 1600 Bytes pro Block-/Kanalkomponente
liegt der vollstaendige Codebereich bei `0..408000` und der mathematische
Rezeptorwert bei `byte_sum/408000`.

Verschiedene Rohbloecke mit derselben Summe sind auf dieser Rezeptorschicht
gleich. Direkt benachbarte Summen bleiben ohne Toleranz verschieden.
PPB-Kandidaten benoetigen weiterhin eine homogene, lueckenlose
Aggregatcodelinie.

Die vollstaendige Domaene wird mathematisch gebunden. Eine spaetere
Qualifikation ist auf 50 neutrale Faelle und hoechstens 1192 logische
Arbeitspositionen begrenzt. Der 2812-Zellen-S2-IX-Pfad wird nicht
implementiert.

Status:

`STATIC_RECEPTOR_AGGREGATE_CODE_EQUIVALENCE_CONTRACT_BOUND`

# Fensterweiser Replayanschluss

QUALIFIED, 19 Prüfgruppen, genau ein Aufruf.

Ein Replayfenster je Anfrage, 30 Sekunden je Anfrage, zusätzlich 600 Sekunden für höchstens 20 Anfragen einschließlich Zielfenster. Quellenprüfung zählt mit; keine Fristverlängerung durch Phasenmeldungen. EOF und close behalten eigene Grenzen.

Quellen-/Zeit-/Sequenzbindungen, fehlende/verdoppelte/rückläufige Bestätigungen, kumulative Zähler, Grenzfälle und Abbruch innerhalb/zwischen Abschnitten neutral geprüft. Native Spätwiederaufnahme nutzt synthetische Codecframes und eine neue neutrale Datei, nicht das reale Video. Ihr tatsächlich erreichter Status und Replay-ohne-Memory-Kontrollen stehen in native/*-process.json und den vollständigen Logs. Keine historische Passzahl übernommen.

Vollständige Erfolgshülle konservativ vorgebunden, neue Bestätigungen und temporäre Publikationen mitgezählt. Fehler nach letzter Bestätigung lassen unbestätigten Verbrauch ausdrücklich unbekannt. 30/600 Sekunden sind Abbruchgrenzen, keine Garantie realer Laufzeit. Historische Befunde unverändert; kein realer Lauf. Gates False.

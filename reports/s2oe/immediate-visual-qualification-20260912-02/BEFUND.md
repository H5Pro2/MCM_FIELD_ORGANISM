# Vorabstopp: korrigierte Fixture, Qualifikation nicht gestartet

Die enge Testkorrektur ist vorbereitet. Produktmodule, Validatoren und Regeln
blieben unverändert. Kein Testaufruf, kein Retry, keine neue Qualifikation.
Die Ablage `immediate-visual-qualification-20260912-02` enthält nur die
Vorbereitung; es existiert keine `qualification.claim` und kein Testergebnis.

## Korrektur

Die native Fixture verwendet beim NN-Aufruf nun `common_time=vt` mit
[466666666,500000000). Damit sind gemeinsame und visuelle Zeit gleich und
erfüllen statisch die zuvor verletzte Bedingung. Die native Audiozeit
[19200,24000) und visuelle Zeit [14,15) bleiben erhalten. Die neue
Kontroll-Sitzungszeit wird weiterhin erst im Kontrollanschluss separat
gebunden; historische Daten werden nicht verändert.

Administrative Herkunfts-, Digest- und Budgettests erzeugen ausschließlich
einen eigenen strukturellen Elternbeleg, ohne native Formationsfixture.
Nur Prüfgruppe 14 baut die native Fixture. Native Importe erfolgen dort
beziehungsweise in der separaten Gatesperrenprüfung, nicht im gemeinsamen
Setup. Die 18 Prüfgruppen bleiben vollständig erhalten. Ein eigener Zähler
soll tatsächlich erreichte Testkörper berichten. Diese Änderungen wurden
noch nicht durch Tests bestätigt.

## Vollständige Vorbilanz

| Klasse | Gebundene Byte | Grenze |
| --- | ---: | ---: |
| Historischer Eingangsrecord | 1.359.778 | 2.097.152 |
| Quelleninventar | 10.026 | 174.080 |
| Metadaten einschließlich Reserven | **98.304** | **65.536** |
| Verifikation | 262.144 | 262.144 |
| Zusatzbelege | 4.096 | innerhalb gemeinsamer Hülle |
| Datenhülle | 393.216 | bestehende Einzelgrenzen zusätzlich |
| Gemeinsame Zusatzhülle: Quellen + Zusatzbelege | 14.122 | 262.144 |
| Gesamt, ohne doppelte Addition der gemeinsamen Hülle | 2.127.564 | 4.194.304 |

Metadaten: Präregistrierung 8.192 + vollständiges Log 65.536 + Ergebnis
8.192 + Bilanz 4.096 + Laufbindung 8.192 + Bericht 4.096 = 98.304 Byte.
Die Logreserve wurde ausdrücklich prospektiv erhöht. Alle übrigen Reserven
und übergeordneten Grenzen wurden unverändert übernommen. Überschreitung:
**32.768 Byte in der Metadatenklasse**, keine Gesamtüberschreitung.

Selbst eine Kürzung sämtlicher übriger Reserven auf ihre tatsächlichen
positiven Mindestgrößen würde den grundsätzlichen Konflikt nicht beseitigen:
Das Log allein beansprucht bereits die gesamte Metadatengrenze. Es wurde
keine Verpackung, Umklassifizierung, Kürzung oder Grenzänderung eingeführt.

Aktuelle Produkt-/Test-/Aufrufhashes und transitive Abhängigkeiten stehen in
`inventory.json`; vollständige Reservebindung in `preregistration.json`.
Die vorbereitende administrative Hashbindung las den Elternrecord einmal
(1.359.778 Byte); keine Rezeptorwerte wurden an Memory oder Scans übergeben.

Tatsächlich erreichte Testkörper: **0, weil kein Test gestartet wurde**.
Dies ist nicht mit den 18 Setupfehlern des unverändert erhaltenen alten
NOT_QUALIFIED-Laufs gleichzusetzen. Gates False, reale Kontrolle gesperrt.

RÜCKMELDUNG ERFORDERLICH: Die neue Logreserve und die unveränderte gemeinsame
Metadatengrenze sind ohne zusätzliche Entscheidung nicht gleichzeitig
erfüllbar. Keine eigenständige Erweiterung oder Umklassifizierung.

# Fehlerglättung gegen letztes Fehlerpaar bei gleichem Budget

Aktualisierung nach analytischer Vorprüfung: **STOPP für den großen U/L-Vergleich
auf der festgelegten LZ1-Quellenstruktur.** Reguläre Vorhersagen sind äquivalent;
Abweichungen entstehen nur durch numerische Gleichstände. Die untenstehende
Stabilitäts-/Wechselerwartung ist historischer Vorschlag, keine bestätigte
Gegenprognose. [Herleitung und neutrale Prüfungen](../reports/s2uc/ul-analytic-precheck-20261004-01/REPORT.md).
Keine Umsetzung dieses Vergleichs empfohlen. LZ1-Abnahme unverändert.


2026-10-04 — ausschließlich KONZEPT; keine Implementierung, Qualifikation,
Quellenerzeugung oder Forschungsausführung. Genau ein Vergleich U/L.
Grundlage: fachliche LZ1-Abnahme und anschließender Konzeptauftrag des Projektleiters.

## Frage und genau eine Änderung

Welchen Beitrag leistet die zeitliche Glättung der Fehlerbewertung, wenn
Originalspuren, Abruf und Speicheraufbau gleich sind?

U bleibt multi_error_exact_v1: erste gültige Bewertung speichert (ec, ep),
danach EC = 0,5·EC + 0,5·ec und EP = 0,5·EP + 0,5·ep, in der bestehenden
binary64-Operationsfolge. L speichert bei jedem gültigen Feedback ausschließlich
EC = ec und EP = ep. L ist damit die einfache Bewertung durch die letzte
Beobachtung; kein zusätzlicher Parameter, Zähler, Ring oder Verlaufsspeicher.
Die Wahl dieser Regel folgt ihrer minimalen zeitlichen Erinnerung, nicht einer
Anpassung an LZ1-Zahlen. U behält sein bereits zuvor festgelegtes alpha=1/2.

Beide wählen aus warmen berechtigten Hypothesen das eindeutige Minimum
d = EC−EP, ausschließlich wenn d < 0; andernfalls Persistenz. Kalte Zellen,
Gleichstände, Enthaltung und Identitätsprüfung bleiben exakt gleich.
Auch nicht gewählte Hypothesen erhalten dieselben gültigen Rückmeldungen.
Nur die Bildung der beiden gespeicherten Bewertungswerte unterscheidet sich.
Dies untersucht den Glättungsbeitrag, nicht den gesamten MCM-Mechanismus.

## Gleicher Informationszugang und Lebenszyklus

Zwei isolierte Instanzen erhalten frameweise dieselbe Quelle in derselben
Reihenfolge und dieselben regulären Aufnahme-, Abruf- und Feedbackgelegenheiten.
Unveränderte Aufnahme, Bestätigung, Verdrängung und direkte Promotionsmitnahme;
kein Rückgriff auf Ausgaben zur Aufnahme. Gleiche Originalidentitäten und
Lebensdauern, maximal drei Vierframespuren, maximal sechs berechtigte Hypothesen.
Jede Entscheidung wird vor dem Ziel eingefroren. Feedback nur für eingefrorene,
noch lebende Schlüssel; verlorene Generationen werden gleich behandelt.
Kein Reset beim Wechsel, keine Phaseninformation, Labels oder Quellenparameter
im Arm. A1/K1 aus. Beobachterdaten sind keinem Arm zugänglich.

Ein späterer Vergleich muss je Ereignis identische Bestände, Hypothesenschlüssel,
Warm/Kalt-Belegung und Feedbackzulässigkeit nachweisen. Eine Abweichung macht
die Zuschreibung an die Bewertungsstrategie nicht auswertbar.

## Explizite Ressourcenbilanz je Arm

Die folgenden Größen sind Vertragsbudget und statische Struktur, keine neue
Messung. Dieselbe Zählweise gilt für beide Arme und sämtliche Lebensphasen.

| Bereich | U und L, jeweils |
| --- | --- |
| Originalframes | gleiche tatsächliche Union aller gehaltenen Frameidentitäten; harte Grenze 18, keine zusätzlichen Vektorkopien |
| Originalnutzdaten | 48 Float64 je Frame = 384 Byte, höchstens 6.912 Byte; Python-Objekte und Metadaten zusätzlich ausweisen |
| Bewertungsbank | genau eine allokierte 416-Byte-Bank, keine zweite Bank |
| Lebende Zellen | sechs Slots zu 32 Byte = 192 Byte; davon pro gültiger Zelle 16 Byte EC/EP; gleiche Anzahl gültiger Zellen je Ereignis |
| Zielheader | 16 Byte |
| Eingefrorene Hypothesenschlüssel | sechs Slots zu 16 Byte = 96 Byte |
| Temporäres Update-Staging | sechs Fehlerpaare zu 16 Byte = 96 Byte, bereits in der Bank enthalten |
| Steuerung | 16 Byte; einschließlich reservierter Bytes |
| Zusätzlicher Python-Heap | höchstens 16.384 Byte einschließlich Bankobjekt, Halter, Scope, Skalare, Iteratoren, Tupel, Promotion und Bereinigung; keine kostenlosen Systemhalter im Beobachter |
| Ausgaben | höchstens zwei 48er Vektorslots, 768 Byte logisches Nutzdatenäquivalent; Originalaliase werden physisch nicht doppelt gezählt; Originale und Ausgaben zusammen höchstens 20 |
| Eingangsframe | Quellsample samt 48er Payload separat und für beide identisch ausweisen; nicht durch Umbenennung aus der Bilanz entfernen |
| Receipt/Serialisierung | gleicher Feldumfang; Receipt höchstens 16.384 Byte, transientes UTF-8 höchstens 32.768 Byte; tatsächliche Längen und Heapüberlappungen separat ausweisen |

416 = 192 + 16 + 96 + 96 + 16. Persistente Bewertungspayload je lebender
Hypothese ist in beiden Armen tatsächlich 16 Byte, nicht nur gleich begrenzt.
Beide Werte werden gebraucht: Kontextfehler und zugehöriger Persistenzfehler.
Keine bedeutungslose Padding-Historie zum Vortäuschen gleicher Nutzung.
Die beiden Fehlerwerte verdichten unterschiedliche Zeitinformation; genau
diese unterschiedliche Nutzung derselben Kapazität ist der Untersuchungsgegenstand.

Gleiche Höchstgrenzen beweisen keine gleiche tatsächliche Nutzung. Bei einer
späteren technischen Qualifikation sind deshalb pro Phase und Ereignis
Originalunion, gültige Zellen, Stagingbelegung, Ausgangsaliase, dauerhaft
erreichbare Python-Objekte, temporärer Peak und Receiptlängen getrennt zu
erfassen. Den gemeinsamen Basisspeicher einschließlich Frameobjekten und
Metadaten in beiden Armen vollständig zählen; der Zusatzheap allein ist
keine Gesamtbilanz. Physisch geteilte Objekte einmal pro isoliertem Arm zählen;
Ausgabealiase zusätzlich logisch kennzeichnen. Peaks überlappender Bereiche
nicht als unabhängige Messwerte addieren. Messinstrumentierung und externe
Referenzen separat ausweisen, niemals als kostenloser Armspeicher verwenden.

Die tatsächliche Python-Gesamtgröße und die temporären Peaks von L sind heute
unbekannt. L spart voraussichtlich Rechenoperationen; identische Byte-Peaks
werden nicht behauptet und nicht durch künstliche Allokationen erzwungen.
Abnahme verlangt gleiche Original-/Zellbelegung und gleiche feste Bank sowie
offengelegte tatsächliche Unterschiede innerhalb derselben Budgets. Ein Befund
darf nur als Vergleich bei gleichem Budget und gleicher persistenter
Informationskapazität bezeichnet werden, nicht ohne Messbeleg als identischer
Gesamtspeicherverbrauch. Budgetverletzung sperrt den Vergleich; keine Erhöhung.

LZ1 ist nur historische Ressourcenreferenz: U-Zusatzheap 5.495 Byte, Bank
416 Byte; konservativ zwölf Originalframes, kein gemessener Frame-Trace.
H64 mit 73.728 Byte Ring ist ausdrücklich kein Arm dieses Vergleichs.

## Erwartung und vorab bestimmter Gegenbefund

Mechanistische Hypothese: U glättet einzelne zufällige Abweichungen und ist
deshalb in stabilen Abschnitten genauer als L. L vergisst den bisherigen
Bewertungswert nach einem gültigen Feedback vollständig; es kann nach einem
Wechsel schneller reagieren, reagiert aber auch auf einzelne Zufallsereignisse.
Das ist eine offene Erwartung, kein aus LZ1 abgeleiteter Messbefund.

Für eine spätere, gesondert vorab gebundene Untersuchung: gleiche strukturelle
S/W/N-Aufgabe und unveränderte Y-Masken, neue vorab versiegelte Folgen statt
Wiederabspielen der verbrauchten LZ1-Freigabe. Keine Auswahl unter Seeds oder
Anpassung an den alten Lauf. Genau zwei Arme, keine Variantenfamilie.
Stabile Genauigkeit: S, Y 33–128. Frühe Wechselreaktion: W, Y 129–160.
Diese Fenster sind aus dem vorhandenen Vertrag übernommen, nicht nachträglich
optimiert. Frühe Fenster-MAE ist keine individuelle Anpassungslatenz.

Definiere D = MAE(U)−MAE(L), je Wiederholung gepaart. Erwartet werden D < 0
im stabilen Fenster und D > 0 im frühen Wechselfenster. Beide gerichteten
Aussagen werden getrennt mit vorab festgelegten 97,5%-Intervallen berichtet
(Bonferroni für zwei Kontraste); Wiederholungscluster statt Einzelziele.
Der spätere Prüfvertrag muss Quellbindung und Unsicherheitsverfahren vor
Materialisierung schließen; dieser Konzeptauftrag erzeugt sie nicht.

Konkrete Widerlegung der erwarteten Abwägung: U ist in beiden Fenstern
nachweislich besser (beide Intervalle vollständig unter null); dann fehlt
der vorausgesagte Reaktionsvorteil von L. Ebenso widerlegt ein stabiler
nachgewiesener Vorteil von L die Stabilitätserwartung. Null einschließende
Intervalle bedeuten Nichtnachweis, keine Bestätigung oder Gleichwertigkeit.
Gesamtes G_Y, spätes Wechselfenster, N, Gerüst, Schäden, Enthaltungen und
Ressourcen bleiben vollständig sekundär sichtbar, ohne die beiden Kriterien
nach dem Ergebnis auszutauschen. Keine Parameteroptimierung nach Befund.

## Abschluss und nächster Schritt

Der Projektstand ist synchronisiert; LZ1-Einmalfreigabe verbraucht.
Dieser Vorschlag ist konzeptionell abgeschlossen. Nächster sinnvoller Schritt:
Projektleiter bewertet U/L als isolierten Glättungsvergleich und entscheidet
über einen begrenzten Implementierungs-/Qualifikationsauftrag. Eine spätere
Forschungsausführung braucht weiterhin ihre eigene Freigabe. Keine heutige
Codeänderung, kein Testlauf, keine neue Laufnummer.

Quellen: [LZ1-Bericht](../reports/s2uc/lz1-assessment-20261004-01/REPORT.md),
[bestehender Bewertungsvertrag](S2UC_MEHRHYPOTHESEN_FEHLERBEWERTUNG_VERTRAG_20261003.txt),
[U-Implementierung](../tools/_s2uc_multi_error.py).

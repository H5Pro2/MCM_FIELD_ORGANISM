# S2-FD: Statischer Vertrag der Startinfrastruktur

## Status und Grenze

**STATIC_PREPARATION_CONTRACT_BOUND_EXECUTION_BLOCKED**

Dieser Vertrag bereitet ausschliesslich die private Startinfrastruktur vor.
S2-FC bleibt blockiert. Es wurden keine Implementierungsdateien angelegt,
keine Metadaten erneut erhoben und keine Projektfunktionen, Tests, Flushes,
Recorder oder Matrixzellen ausgefuehrt. Das Ledger wurde nicht erzeugt.

Die vollstaendige maschinenlesbare Bindung steht in
[S2FD_STATISCHER_STARTINFRASTRUKTUR_VERTRAG_V1.json](S2FD_STATISCHER_STARTINFRASTRUKTUR_VERTRAG_V1.json).
Sie pinnt den bestehenden Quellstand, die archivierten Originalbelege,
geschlossene Datenformen, Rollen, Budgetableitung und Abbruchreihenfolge.

## Vollstaendiges Startpaket

Das spaetere Paket muss die acht unveraenderten Bestandsmodule, die neuen
privaten Startquellen, alle Bootstrap-Abhaengigkeiten, die vorgesehene Runtime,
alle vier nativen Elternidentitaeten und deren Abnahme enthalten. Hinzu kommen
F, SourceManifest, RunBinding, die unveraenderten 133 Recorderpfadrollen,
24 Fixture-Payloads, elf Fehlervorgaben und die drei inneren Actorrollen.

Runtime-Dateien ausserhalb des Repositorys werden vom Starter separat
geprueft. Sie duerfen nicht in WindowsFiles.read_source gelangen: Dieser
Bestandspfad erlaubt ausschliesslich Quellen unter repository/git_common.
Ein lokales Manifest bindet die externe Runtime, ersetzt aber nicht deren
tatsaechliche Quellenpruefung.

Die Digestreihenfolge ist verbindlich:

1. Quellen, Runtime, Elternbelege und alle spaeteren Quellpfadnamen binden.
2. SourceManifest und F erzeugen.
3. RunBinding mit Pfadnamen, Payloads und Fehlervorgaben binden.
4. Innere Freigabe und Vorregistrierungsabnahme nur an F/RunBinding/SourceManifest binden.
5. Deren Originalbytes in die vollstaendige lokale Leseliste aufnehmen.
6. Budgetbeleg ableiten und damit die komplette RecorderBinding binden.
7. Aeusseres StartPackage und unabhaengige StartAdmission binden.

Die aeussere Abnahme und der Budgetbeleg bleiben ausserhalb der Recorder-
Leseliste. Die innere Freigabe darf keine spaeteren Binding-/Paketdigests
enthalten. So entsteht kein Selbsthash oder Kreis zwischen Freigabe,
Quellliste, Budget und Startpaket. Die spaetere Ausfuehrungsfreigabe ist
separat; dieser Vertrag ist keine solche Freigabe.

## Ledger und Pfadrollen

Vorgesehen bleibt ausschliesslich:

`C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\.git\mcm-execution-ledger`

Es ist parent.ledger der bestehenden Vier-Eltern-Bindung. Der archivierte
Metadatenbeleg dokumentiert sein Fehlen. Die anderen drei Eltern ersetzen
dieses Verzeichnis weder logisch noch hinsichtlich nativer Identitaet.

Fuer den externen Startbesitzer werden nur zwei kuenftige Namen gebunden:

- `s2fd.s2em.002.dispatch.json`
- `s2fd.s2em.002.dispatch.seal.json`

Beide liegen im vorgesehenen Ledger, bleiben von den 133 Recorderpfadrollen
getrennt und duerfen nur vom externen Beobachter/Startbesitzer verwendet
werden. Keine neue Schreibrolle fuer Worker, Helper oder Supervisor.
Die Namen haengen nicht vom Plandigest ab; ein geaenderter Plan darf keinen
neuen Versuch unter anderem Namen ermoeglichen.

Die spaetere Einrichtung und Abnahme des Verzeichnisses benoetigt eine eigene
Freigabe. Der Starter darf fehlende Verzeichnisse niemals automatisch anlegen.

## Abgeleitete Budgetbelege

Gebunden sind 13 Faelle, 24 Payloads mit zusammen 528 Bytes, 133 innere
Pfadrollen, 28 Renamekanten und zwei getrennte externe Ownerdateien. Je
Starter, Supervisor und Worker ist hoechstens ein Prozess zulaessig; der
bestehende Helper bleibt ein begrenzter Thread. Keine Wiederholung.

Die Budgettabelle ist aus den gelesenen Bestandsfunktionen abgeleitet.
D bezeichnet die vollstaendige Zahl gepinnter Verzeichnisse, A die bei einem
Quellzugriff erstmals hinzugekommenen Verzeichnisse, n die gebundene
Byteanzahl und q(n) = ceil(n / 1048576).

| Bestandsoperation | Obere native Aufrufzahl |
| --- | --- |
| Dateimetadaten pruefen | 4 |
| Verzeichnismetadaten pruefen | 5 |
| Datei / Verzeichnis oeffnen | 5 / 6 |
| Alle gepinnten Verzeichnisse pruefen | 5D |
| Vier Eltern initial pinnen | 4 + 11D |
| Abwesenheit pruefen | 5D + 1 |
| Datei lesen | 7 + q(n) |
| Quelldatei lesen | 6A + 5D + 12 + q(n) |
| Neue Datei erzeugen | 5D + 5 |
| Datei schreiben / flushen | q(n) / 1 |
| Datei verifizieren | 5D + 7 + q(n) |
| Rename / finalen Namen pruefen | 5D + 5 / 5 |
| Fixture-Record schreiben und abnehmen | 10D + 13 + 2q(n) |

Dies sind statische Kosten, keine ausgefuehrten Operationen. Die vollstaendige
spaetere Ableitung muss alle Schleifen, Fehlerzweige, moegliche zweite
Postcondition-Pruefungen, erhaltenen Handles und Cleanup-Aufrufe mitzaehlen.
Physische native Aufrufe und logische Recorder-Aufrufpaare bleiben getrennt;
eingespeiste Proxys duerfen nicht unter den Tisch fallen.

Der Bytebeleg hat eine gerichtete Abhaengigkeitsfolge: Quellen und
Fixture-Records, danach Falltraces, rohe Worker-Ausgabe, gerahmtes Transkript,
Supervisor-Kontrolltrace und zuletzt dessen nichtrekursive eigene Datei-I/O.
Ein Transkript darf nicht mit seiner eigenen Obergrenze begruendet werden.

Pipe-Lesungen koennen kuerzer als 65.536 Bytes ausfallen. Der Vertrag rechnet
daher auch mit Ein-Byte-Fragmenten und deren zusaetzlicher JSON-/Base64-Huelle.
Die rohe Ausgabe und das gerahmte Transkript benoetigen getrennte Obergrenzen.
Validierungsarbeit, gehaltene Bytekopien, Kontroll-Spool-I/O, Prozesswartezeiten
und Abbruchschritte werden ebenfalls gebunden, nicht als kostenlos behandelt.

**Noch kein numerisch vollstaendiger Ausfuehrungsbeleg:** Die neuen Quellen,
die finale Leseliste und ihre Prozess-/IPC-Aufrufstellen existieren noch
nicht. Daraus werden nach der Implementierung die konkreten positiven
Grenzwerte und ein passender Ressourcenrahmen statisch abgeleitet. Unbekannte
Werte oder bloss willkuerlich grosse Zahlen lassen S2-FC nicht bestehen.

## Unabhaengiger Start und Abschluss

Der externe Abschlussbeobachter besitzt die Einmalfreigabe. Vor dem ersten
Starterprozess muss er die getrennte Dispatch-Reservierung und deren
gebundenen Abschluss nach dem spaeter abgenommenen Persistenzvertrag sichern.
Danach startet er genau einen Starter; dieser genau einen Supervisor.

Erst nach dessen bestehender RESERVED-Abnahme darf der einmalige Worker
record_worker betreten. Der Supervisor besitzt das echte Popen-Objekt fuer
capture; der Beobachter benoetigt zusaetzlich einen unabhaengig gebundenen
nativen Prozesshandle. PID oder vom Kind gemeldeter Exit-Code allein reichen
nicht. Die Einzelheiten des Handle-/Pipe-Uebergangs gehoeren zum separat
abzunehmenden Implementierungsumfang, nicht zu einer heutigen Ausfuehrung.

Der Beobachter darf Erfolg erst nach unveraendertem LiveRecordingCompletion,
vollstaendigen Originalbelegen, tatsaechlichen Prozessenden und bestaetigter
Kontroll-Spool-Schliessung zurueckgeben. Sein eigener Aufrufer muss wiederum
seinen tatsaechlichen terminalen Abschluss sehen. Es wird keine rekursive
Kette von sich selbst bestaetigenden JSON-Markern eingefuehrt.

## Einmaligkeit und Fail-Closed

Vorhandene, leere, beschaedigte oder fremd gebundene Dispatchdateien bedeuten
immer verbraucht. Teilfehler, Timeout, falsche Herkunft, fehlende Daten,
Budgetueberschreitung und Close-/Flush-Fehler sperren einen Abschluss.
Kein Retry, keine Loeschung, kein Rollback und kein Wiederanlauf.

Ein Fehler vor der ersten erfolgreichen dauerhaften Reservierung erzeugt
keinen nachtraeglichen Plattenbeweis. Hier bleibt die unabhaengig vergebene
Einmalfreigabe des Aufrufers die ausdrueckliche Vertrauensgrenze. Unklarheit
bedeutet UNKNOWN und keine erneute Verwendung, auch bei leerem Verzeichnis.
Es wird nicht behauptet, lokale Dateien koennten Ereignisse vor ihrer eigenen
Erzeugung beweisen. Vor bestaetigter Dispatchbindung startet kein Kindprozess.

## Herkunft der nativen Metadaten

Der archivierte Originalbeleg mit Record-Digest
`b13e2a3a851f47ae0a2c65e1e03cb8aaccfac8e236ed242cef108b2c50d1af03`
bleibt unveraendert. Originaldatei und Record-Digest werden getrennt gebunden.
Die damalige Observer-Runtime wird nicht in die kuenftige Recorder-Runtime
umbenannt. Der vierte Elternbeleg, Einrichtung, Haltbarkeitsgrundlage sowie
noch nicht enthaltene native Eigenschaften duerfen nicht erfunden werden.

Erst nach unabhaengiger Herkunftsabnahme darf eine abgeleitete NativeOrigin
nach der unveraenderten S2-FB-Form entstehen. Der Originalbeleg bleibt daneben
erhalten. Eine erneute Metadatenerhebung ist heute nicht freigegeben.

## Naechste Freigabe

Als naechstes kann ausschliesslich die private Implementierung der vier im
JSON genannten Start-/Beobachtungsdateien beantragt werden. Bestandsmodule
bleiben unveraendert. Keine Ledger-Provisionierung und kein Ausfuehrungsstart.

Nach der Implementierung sind Quellkette, genaue Prozessschnittstellen und
numerische Budgets statisch abzunehmen. Tests, fehlende Elternbelege und
Plattformausfuehrung benoetigen jeweils ihre eigene ausdrueckliche Freigabe.
Bis zur vollstaendigen Startbindung bleibt S2-FC blockiert.

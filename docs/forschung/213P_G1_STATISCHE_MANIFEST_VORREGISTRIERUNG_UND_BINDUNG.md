# 213P - G1 statische Manifest-Vorregistrierung und Bindung

## Einordnung

213P ist ein statisches Vorregistrierungs- und Bindungspaket, kein
Forschungslauf, kein Manifest und kein Resolverlauf. Es legt die Anforderungen
an die noch fehlenden Builtin-/Frozen- und Native-Manifeste fest und bindet nur
vorhandene Installationsdateien read-only. Es wurden keine Module importiert,
keine Tests ausgefuehrt und keine Prozesse gestartet.

## Forschungsfrage und Auftrag

Welche Quellen, Formate, Pflichtfelder, Bytebindungen und Stopplinien muessen
vorliegen, damit die in 213O freigegebene statische Resolverimplementierung in
einem spaeter separat freizugebenden G1-Lauf Builtin-/Frozen- und native Module
ohne Laufzeitabfrage aufloesen darf?

## Tatsaechlich verwendete Quellen

- aktueller freigegebener Uebergabe-Eingang;
- `docs/forschung/213N_G1_STATISCHE_RESOLVER_VORREGISTRIERUNG.md`;
- `docs/forschung/213O_G1_STATISCHE_RESOLVERIMPLEMENTIERUNG.md`;
- `tools/static_g1_resolver.py`;
- installierte CPython-3.14.4-Dateien unter `C:/Python314`;
- installierte NumPy-Erweiterungen unter
  `.venv/Lib/site-packages/numpy`.

Keine Webquelle und keine externe MCM-Quelle wurde verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden ausschließlich PowerShell-Dateiauflistung, Dateigroesse,
SHA-256 und Textsuche. Python, NumPy, der Resolver und Projektmodule wurden
nicht importiert oder gestartet. Ausser diesem Dokument wurde keine Datei
veraendert.

## Gebundene CPython-Quellen

| Rolle | Pfad | Bytes | SHA-256 |
|---|---|---:|---|
| CPython-Implementierungsbibliothek | `C:/Python314/python314.dll` | 6.767.440 | `A07F7D09C3121492BB066535C6D0811DF5FBC2090CBCA7031A97BB47CE1480C9` |
| stabile ABI-Bibliothek | `C:/Python314/python3.dll` | 74.072 | `1DD696F02326E32E67B52C25B249B3ACCE3238176212D16E8FB1A050A1455AE9` |
| Import-API-Deklaration | `C:/Python314/include/cpython/import.h` | 929 | `65FC03C4074B2834A0FAA06A4347CCA1BB8B320D2DE48EEB75DE951575CD7782` |
| interne Import-Deklaration | `C:/Python314/include/internal/pycore_import.h` | 4.789 | `A90DBB06D12E732F2A6138E4521E6B88A8BD6ABF9AD35EFBE1BA7EBD85BB0800` |
| Importbibliothek | `C:/Python314/libs/python314.lib` | 404.054 | `D3E1766F345719F4FC11E3D49F87D42F767E4D7C00928370B6D300FE75BCB0D4` |

Die Header belegen die Existenz der Frozen-Tabellenstrukturen und ihrer
Schnittstellen, aber nicht deren konkrete Eintraege in diesem Binary. Weder die
Header noch die Importbibliothek sind eine autoritative Builtin-/Frozen-
Namensliste. `python314.dll` bindet die konkrete Implementierung bytegenau,
liefert ohne separat geprueften statischen Tabellenleser aber ebenfalls noch
keine belastbare Modulliste.

## Gebundener Native-Kandidatenraum

Unter `C:/Python314/DLLs` wurden 34 `.pyd`-Dateien mit zusammen 4.344.208
Bytes gefunden. Unter `.venv/Lib/site-packages/numpy` wurden 19 `.pyd`-Dateien
mit zusammen 7.294.976 Bytes gefunden. Der gebundene Kandidatenraum umfasst
damit 53 Dateien und 11.639.184 Bytes.

### CPython-DLLs

| Datei | Bytes | SHA-256 |
|---|---:|---|
| `_asyncio.pyd` | 78.160 | `13B374175108C266F4A5BDF907F990D0CCD5B486D0313856E08A60BA9BF856CF` |
| `_bz2.pyd` | 87.896 | `33641A8AD0403473D678C7435197D49550FC5185BA7979FB16AB80256B1F9072` |
| `_ctypes.pyd` | 142.680 | `79967D8614F735CC62B81649641FD8D0414CA66D3D6656FA7788334BBDBBD35B` |
| `_ctypes_test.pyd` | 133.464 | `600DAC573E67373037AB9438F49A0E12B2C2495FF5E9A0B17393A8B6E377D94D` |
| `_decimal.pyd` | 291.160 | `1F4A8CA9814508D3597992173FDF4DB312F3B970F6BAEB053B9D8C3087F907E7` |
| `_elementtree.pyd` | 138.584 | `557DA5278599B51F1C0A53B2FFC617A05A21BE23A2A6B862A5B5CE04667C5F70` |
| `_hashlib.pyd` | 69.464 | `58C5C9FF93F989E2A233B8C5E06420EA73DD6C013E1F08D996FB0F2828EBA0AA` |
| `_lzma.pyd` | 161.112 | `A01F1927ADAA60ADCFBE3B0314205A528CB9DD5A93B7E61CB284EDDEE9B0B347` |
| `_multiprocessing.pyd` | 38.744 | `A88475C4CBA47977EEF5756C217C79441C53CF57D0B05441DE87744313E2898B` |
| `_overlapped.pyd` | 58.200 | `43B9E0BDC41646FC363F144BF050600DAB647CE9E7C251A2B6D0E75358CB10CF` |
| `_queue.pyd` | 36.696 | `2A7BB0A53E86AE4982A6F64E2570137829A0BE66537BB1C166913AF273EDBF0C` |
| `_remote_debugging.pyd` | 76.632 | `2C21987B99CA5F0946B0585AB7A534967C7B4D7C5DB0102FC625DBFA05A0D4E0` |
| `_socket.pyd` | 87.888 | `435A86973131C5D5DC90F828E72D7BB0607578A48AB5BC5377F4A280A6BEB8F7` |
| `_sqlite3.pyd` | 132.432 | `9A31C522E38CDEA19386AE912F44FB75BB7F155D14D486D6BCF4DE7E16883949` |
| `_ssl.pyd` | 184.664 | `06F51FBE150C831AF619890EEA2D9FCA9CE8B49758BFE3F382883551C592E6B3` |
| `_testbuffer.pyd` | 58.712 | `B0DD3C65B036B8199FBF6C723777D5355E7B54DBD4F1CDBB77BDB7528A3EB77C` |
| `_testcapi.pyd` | 302.936 | `C8155B69A4C6FC3A5833B114BCD65A5D45590D6B11DAE2049EAA8F683AFF956E` |
| `_testclinic.pyd` | 110.936 | `26372F98C4826444AAC4DBE3AD108B62163C91229CD340B7A5C20B0C8289EF63` |
| `_testclinic_limited.pyd` | 30.040 | `5CB257CC63324BF07B8639E9787E2C9D1CFC0DAA131CFBA98C5A90281C4915C9` |
| `_testconsole.pyd` | 29.528 | `AEB8F9C8A8C568EFBFF2BB779C3BF37923ECDBCE7CEC53185A7A7C349FCCCBE0` |
| `_testimportmultiple.pyd` | 27.992 | `9F2DFDC3349E118BC7E76A5255733ACD9DD6CDFB1F8B44FA998D291013F7382C` |
| `_testinternalcapi.pyd` | 96.600 | `F126CAB08563E197C92CA0ACA35240AE0E7D2F61E8E68841848B74D22476363C` |
| `_testlimitedcapi.pyd` | 153.944 | `5112A8BA2036254E55FA8CDFDE30B6D0B17474371930855F454D93CF46BEFD1E` |
| `_testmultiphase.pyd` | 42.840 | `B4AAE4F23F125FFD460F421E3FEA4A6835D43CCC2CE6D3D649EAF8FF573C22FB` |
| `_testsinglephase.pyd` | 35.160 | `5C5CBB2087EBDB6D1C005EB07928BFEEB9E73F5B068D33F0C8DCAD49726C0B38` |
| `_tkinter.pyd` | 69.464 | `B7BC5C036699510968FF5040A392DE8FE612FA66DAD01FBB5D66DF56DB554A8F` |
| `_uuid.pyd` | 28.504 | `35F26F7F55DED30DA92ED30258FB9624A7398BA3EADEE134813133C560FCBBAE` |
| `_wmi.pyd` | 40.280 | `ECCB72A070D63F0DDDE054C7A15D375B11B1DFC3362452C55CCABB487DEE87FC` |
| `_zoneinfo.pyd` | 52.048 | `65FAD0EFC2524E411C65919288835BB8781926BF9E7A5F92912B6FFA393A226B` |
| `_zstd.pyd` | 503.128 | `E5924E2985186797668DD3B2E1EFEB9313459258A4564DBF5499935C7EBD44E7` |
| `pyexpat.pyd` | 218.968 | `05530AFC9CBFE68C28C052EEC159B852E731316007E1F52E0A31412E4EDA07F9` |
| `select.pyd` | 33.624 | `56441C3148743A0890986CCDF93FEA8174155B0EE84DB2493151F075D8E7C51A` |
| `unicodedata.pyd` | 758.616 | `58013696B4F08717AEE2885AEFA24031F4B18B3E62FAA8125248CC3E0A86AF2A` |
| `winsound.pyd` | 33.112 | `959771D50F61FA373B05A076AF29696209C12457EA9D6A78C5AFC5AA8638190A` |

### NumPy-Erweiterungen

| Relativer Pfad unter `.venv/Lib/site-packages` | Bytes | SHA-256 |
|---|---:|---|
| `numpy/_core/_multiarray_tests.cp314-win_amd64.pyd` | 66.048 | `7C6F3E0793C6EDE96204639B5798693786EFE9D35A5FAB7A86D4A5F9D559E229` |
| `numpy/_core/_multiarray_umath.cp314-win_amd64.pyd` | 3.904.512 | `AB5CEA76A0FAD4FD1BC58667AEFBA1382A7CE8C147B51CF3BFF53EEC4EFB4AB2` |
| `numpy/_core/_operand_flag_tests.cp314-win_amd64.pyd` | 12.288 | `322D6717B0A56E29D303F993BDAA853BFA44F9BB189EE6709B8B3C208CC04EFE` |
| `numpy/_core/_rational_tests.cp314-win_amd64.pyd` | 43.520 | `EA67AC1B1CF3D6444E1F038A0B56BFE6A5770478956E2D55AE393549892EDEA78` |
| `numpy/_core/_simd.cp314-win_amd64.pyd` | 831.488 | `27B44FA3BE39216E416C529FAD5F2AF9196A02D1CA51D6D08ABEC41BF9FBDD09` |
| `numpy/_core/_struct_ufunc_tests.cp314-win_amd64.pyd` | 14.336 | `380216DA0E2D51DCCE8A973FDDA3291BEB7DEE743E43802E0CC8710492C08CC4` |
| `numpy/_core/_umath_tests.cp314-win_amd64.pyd` | 34.304 | `7B042F544CFE99E846FD188D0B0065AE6455A4C1C104578E69CB535727956214` |
| `numpy/fft/_pocketfft_umath.cp314-win_amd64.pyd` | 276.480 | `0FB0D660B2B608A270828D34FB79D4E14B2C33E1BA799AAC7232B714E36A4742` |
| `numpy/linalg/_umath_linalg.cp314-win_amd64.pyd` | 112.128 | `8264D9D70A1A1D72793805A989FC5EBAB8D55970E44A829E1262FD58335FF8D5` |
| `numpy/linalg/lapack_lite.cp314-win_amd64.pyd` | 18.944 | `4CEF8F26BE5895A6973B3C969D024CAB1C3C777DF675059CA20A69D22FDC7B49` |
| `numpy/random/_bounded_integers.cp314-win_amd64.pyd` | 215.040 | `52E8867A30524DB560F6FFE9B3EDB63BEAA8160DD349FFA9CB8EAEEFF786C486` |
| `numpy/random/_common.cp314-win_amd64.pyd` | 173.056 | `54809657FB43A25138617F9706EF781D9E9502B66A9A5366EA7BD76EED918F61` |
| `numpy/random/_generator.cp314-win_amd64.pyd` | 599.040 | `15215EE2AE4C1EC0960C29D433871A8E6BA4C392B8DEE367541FB736F9C6D4C6` |
| `numpy/random/_mt19937.cp314-win_amd64.pyd` | 86.528 | `434AB2857D104FF19C3B5008916197787FCC253339EABC66A16E4BDECFC1C74C` |
| `numpy/random/_pcg64.cp314-win_amd64.pyd` | 96.256 | `B469CBC850EE42A8CA5B5A9B58811D529FC0C7B65DBC7EB4B9D24B924B4B8D07` |
| `numpy/random/_philox.cp314-win_amd64.pyd` | 81.408 | `5B7FFD698D931ACADE2970FD318FA077E14F634ED08D32678A44C2997CEBC600` |
| `numpy/random/_sfc64.cp314-win_amd64.pyd` | 60.416 | `1E4D72BCCC8045C798D13529439D907CE1F1F2D40E6A635F7D4DE93D1F4CA9E6` |
| `numpy/random/bit_generator.cp314-win_amd64.pyd` | 168.448 | `D481331ECA4F875EB6E53A69D722C6BF03A915B6E2033F91DAF2BAD2EFCB7133` |
| `numpy/random/mtrand.cp314-win_amd64.pyd` | 500.736 | `CD83271CC04FB0219FB5D5CB06C5117F60291866A88E332B7C8E8276375D1344` |

Diese 53 Dateien sind eine breite, bytegebundene Kandidatenbaseline. Sie sind
nicht automatisch G1-relevant. Insbesondere Testmodule duerfen nicht allein
aufgrund ihres Vorhandenseins aufgenommen werden. Ein Dateiname oder ABI-Suffix
beweist noch nicht den importierbaren vollqualifizierten Modulnamen.

## Vorregistriertes Builtin-/Frozen-Manifest

Das spaetere JSON-Dokument muss ein Objekt mit mindestens diesen Feldern sein:

```json
{
  "schema": "mcm-g1-builtin-frozen-manifest-v1",
  "platform": {
    "implementation": "CPython",
    "version": "3.14.4",
    "os": "Windows",
    "architecture": "AMD64"
  },
  "source_bindings": [],
  "modules": {
    "example": {
      "kind": "builtin",
      "evidence_source": "C:/absolute/source",
      "evidence_locator": "static-table-entry"
    }
  }
}
```

Pflichtregeln:

1. `schema` und alle vier Plattformwerte muessen exakt passen.
2. Jede inhaltlich verwendete Quelle benoetigt absoluten Pfad, Rolle, Bytes und
   SHA-256 in `source_bindings`.
3. Jeder Schluessel in `modules` ist der exakte importierbare Modulname.
4. `kind` ist ausschließlich `builtin` oder `frozen`.
5. `evidence_source` verweist auf eine gebundene Quelle;
   `evidence_locator` bezeichnet den reproduzierbaren statischen Fundort.
6. Frozen-Aliase und Paketkennzeichen muessen explizit dokumentiert werden;
   sie duerfen nicht aus Namenskonventionen geraten werden.
7. Eine Laufzeitliste wie `sys.builtin_module_names` oder eine `_imp`-Abfrage
   ist keine zulaessige Quelle dieses statischen Pakets.

## Vorregistriertes Native-Manifest

Das spaetere JSON-Dokument muss mindestens dieses Format haben:

```json
{
  "schema": "mcm-g1-native-manifest-v1",
  "platform": {
    "implementation": "CPython",
    "version": "3.14.4",
    "os": "Windows",
    "architecture": "AMD64"
  },
  "source_bindings": [],
  "modules": {
    "package.example": {
      "path": "C:/absolute/module.pyd",
      "size": 123,
      "sha256": "64 uppercase hex characters",
      "init_symbol": "PyInit_example",
      "evidence_locator": "PE export table"
    }
  }
}
```

Pflichtregeln:

1. Plattform- und Quellenbindung entsprechen dem Builtin-/Frozen-Vertrag.
2. `path` ist kanonisch, absolut und liegt unter einer in 213N zugelassenen
   Wurzel; Symlink- oder Junction-Aufloesung darf diese Wurzel nicht verlassen.
3. `size` ist die exakte Bytezahl und `sha256` der Hash derselben Rohbytes.
4. Der Modulschluessel muss durch den statisch gelesenen PE-Export
   `PyInit_<leafname>` und den statisch aufgeloesten Paketpfad belegt sein.
5. Mehrphasige oder mehrere Init-Exporte werden offen dokumentiert; bei nicht
   eindeutiger Zuordnung entsteht kein Manifesteintrag.
6. Nur durch den statischen Importgraph erreichte Module werden aus dem
   Kandidatenraum in das Abschlussmanifest uebernommen.
7. DLL-Abhaengigkeiten einer `.pyd` sind G2-Kanten. Sie werden nicht als
   Native-Module in G1 umklassifiziert.

## Hash-, Groessen- und Dateiregeln

- SHA-256 wird ueber die unveraenderten Rohbytes berechnet und als 64-stellige
  Grossschreibung dokumentiert.
- Groessen sind dezimale Bytezahlen; Locale-Trennzeichen gehoeren nicht in JSON.
- Jeder Manifestpfad muss zum Erhebungszeitpunkt existieren, regulaere Datei
  sein und genau einmal vorkommen.
- Vor einem Resolverlauf werden Manifestdatei und jede referenzierte Quelle
  erneut gegen Groesse und SHA-256 geprueft.
- Abweichung, Fehlen, Doppelbelegung, Fallkollisionsname oder Wurzelflucht ist
  ein harter Stopp, kein alternativer Suchpfad.
- Das Manifest selbst erhaelt nach Erstellung eine separate Bytebindung. Diese
  Bindung ist nicht selbstreferenziell Bestandteil derselben Manifestdatei.

## Messergebnisse und Gegenbaselines

Beobachtet:

- 5 zentrale CPython-Quellen wurden mit Pfad, Groesse und SHA-256 gebunden;
- 53 native Kandidatendateien wurden gefunden und bytegenau gebunden;
- die Native-Kandidaten umfassen 11.639.184 Bytes;
- die installierten Header deklarieren Frozen-Strukturen, enthalten aber keine
  konkrete installierte Namensliste;
- es wurde kein vorhandenes autoritatives Builtin-/Frozen-Manifest gefunden.

Gegenbaseline:

- Eine Aufnahme aller 53 `.pyd`-Dateien nach Dateiname wird verworfen, weil sie
  Testmodule und moeglicherweise nicht erreichte Module einschliesst und den
  vollqualifizierten Namen nicht beweist.
- Eine Ableitung der Builtin-/Frozen-Liste aus Headerdeklarationen wird
  verworfen, weil Deklarationen keine konkreten Tabelleneintraege belegen.
- Eine Interpreterabfrage wird wegen des statischen Auftrags nicht verwendet.

## Stopplinien

Die Manifest-Erstellung oder der spaetere Resolverlauf stoppt, wenn mindestens
eine dieser Bedingungen eintritt:

1. Builtin-/Frozen-Name oder Art ist nicht durch eine gebundene statische
   Tabellenquelle eindeutig belegt.
2. Ein Native-Modul hat keinen eindeutigen passenden `PyInit_`-Export.
3. Dateiname, Export, Paketpfad oder Importname widersprechen sich.
4. Eine Quelle, ein Manifest oder ein Eintrag weicht in Pfad, Groesse oder
   SHA-256 ab.
5. Ein erforderlicher Native-Pfad liegt ausserhalb der zugelassenen Wurzeln.
6. Ein PE-Parser, Tabellenleser oder eine andere neue Implementierung waere
   erforderlich, ist aber noch nicht separat statisch freigegeben.
7. Eine DLL-Abhaengigkeit muesste fuer G1 als Modul behandelt oder G2 vorgezogen
   werden.
8. Der Resolver meldet spaeter `alternative`, `unresolved`, fehlende
   Elternpfade, Manifestfehler oder sonstige Stopps.

## Grenzen und nicht gepruefte Annahmen

- Die konkreten Builtin-/Frozen-Eintraege von `python314.dll` wurden nicht
  extrahiert oder verifiziert.
- PE-Exporttabellen der 53 `.pyd`-Dateien wurden nicht gelesen.
- Die Kandidatenliste ist kein Nachweis, dass eine Datei vom Projektgraphen
  erreicht wird.
- DLL-Abhaengigkeiten, `numpy.libs`, G2 und Windows-Sicherheitszustaende wurden
  nicht bearbeitet.
- Die in 213O implementierte Manifestvalidierung prueft nur den fuer die
  Aufloesung benoetigten Kern. Die zusaetzlichen Pflichtfelder dieses Vertrags
  muessen vor einem Lauf entweder durch eine separat freigegebene statische
  Validierung oder durch eine vorab dokumentierte externe Bytepruefung
  durchgesetzt werden.

## Konkrete Schlussfolgerung

Die Quellenbasis und die Manifestvertraege sind statisch vorregistriert. Ein
Native-Kandidatenraum ist bytegenau vorhanden, aber noch nicht durch Exporte und
Importgraph auf akzeptierte Module reduziert. Fuer Builtin/Frozen fehlt eine
autorisierte statische Extraktion der konkreten Binary-Tabellen. Deshalb wurden
keine Manifestdateien erzeugt, G1 ist nicht bestanden, G0 bleibt davon abhaengig
und Huerde G bleibt gesperrt. Es gibt keine erkennbare Zielabweichung.

## Vorschlag fuer den naechsten begrenzten Forschungs- und Entwicklungsschritt

Als naechstes sollte genau ein statisches Werkzeug-Vorregistrierungspaket fuer
die fehlenden Nachweise erstellt werden: read-only PE-Exportauswertung der
gebundenen `.pyd`-Dateien sowie read-only Extraktion oder anderweitig
autoritative statische Bindung der Builtin-/Frozen-Tabelleneintraege aus der
gebundenen CPython-3.14.4-Installation. Das Paket soll Eingaben, Ausgabeformat,
Parsergrenzen, Fehlermodi und Stopplinien festlegen. Noch keine Implementierung,
kein Werkzeuglauf, kein Resolverlauf und keine G2-Bearbeitung.

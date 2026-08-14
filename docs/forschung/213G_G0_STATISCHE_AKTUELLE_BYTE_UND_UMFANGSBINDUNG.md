# Teilpaket 213G: G0 - Statische aktuelle Byte- und Umfangsbindung

## Einordnung, Forschungsfrage und Auftrag

Dies ist ein rein statisches G0-Paket und kein Forschungslauf. Deshalb wird keine
Laufnummer vergeben. Der Auftrag lautet, vorhandene relevante Dateien und Dokumente
zu enumerieren sowie Existenz, Pfad, Groesse, SHA-256, Geltungsumfang und offene
Byte-/Umfangsabweichungen zu dokumentieren.

Dieses Paket aendert keine Datei des gebundenen Korpus und erteilt keine Huerde-G-,
Implementierungs-, Import-, Test-, Prozess-, SID-, Profil-, ACL-, SACL- oder
AppContainer-Freigabe.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang mit der G0-Freigabe;
- `docs/forschung/192_...`, `202_...` bis `208_...`, `212_...` und `213A_...` bis
  `213F_...` gemaess der unten vollstaendig ausgeschriebenen Dokumenttabelle;
- die 22 unten gebundenen lokalen Projektquellen;
- `.venv/pyvenv.cfg`;
- die 25 in 213E definierten nativen Seeds.

Keine Web- oder externen MCM-Quellen wurden verwendet.

## Verwendete Dateien und Schnittstellen

Verwendet wurden ausschliesslich read-only `Test-Path`, `Get-Item` und
`Get-FileHash -Algorithm SHA256`. Es wurden keine Projektmodule importiert, keine
Tests oder Zielprozesse gestartet und keine Sicherheits- oder Systemabfragen
ausgefuehrt.

## Geltungsumfang

Der **aktuell bekannte G0-Korpus** umfasst:

| Klasse | Dateien | fehlend | Bytes |
| --- | ---: | ---: | ---: |
| private Projektquellen und Importbaseline | 22 | 0 | 272.960 |
| venv-Konfiguration | 1 | 0 | 215 |
| Entscheidungsdokumente | 15 | 0 | 144.346 |
| native Seeds aus 213E | 25 | 0 | 35.478.952 |
| **Summe** | **63** | **0** | **35.896.473** |

Die Summe ist eine Bestandsbindung, kein Laufzeitabbild. Nicht enthalten sind die
erst in G1 zu bestimmenden konkreten Standardbibliotheks-/NumPy-Python-/Datendateien
und die erst in G2 zu bindenden Loader-Sonderpfade und deren Dateien. Daher ist dies
noch nicht der endgueltige Huerde-G-Byteumfang.

## Projektquellen

Alle Pfade liegen unter `mcm_field_organism/`.

| Datei | Bytes | SHA-256 |
| --- | ---: | --- |
| `_previous_state_minimal_runner.py` | 8.655 | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `_runtime_fixation_adapters.py` | 11.458 | `422f511c54da7cecce541313ab23bcb37d5d8edab6a97a5cfe04768f111048fc` |
| `_runtime_fixation_binding.py` | 2.226 | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `_runtime_fixation_handoff.py` | 1.086 | `73e3fd5559dbc9eced92e2b7e31adea247c9fe8be73f79b59fc359ca2bbab068` |
| `_runtime_fixation_single_use_path.py` | 482 | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |
| `_runtime_fixation_structure.py` | 15.549 | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `auditory_baselines.py` | 8.538 | `1bd6a5f22181ef0af345509cfbf25195dd97c66e4137f11fefc7f629a9c35731` |
| `broadband_hearing_path.py` | 7.754 | `4dea43d16110444dc2408137361740c5b4a0cca24ac627b715f409ceff0c6535` |
| `carrier_baselines.py` | 3.572 | `dc891f4f263b17acf7b7b50c7c135d9a3d028cb1b9bdb72c342d72d24f1337ab` |
| `field_step_time.py` | 1.790 | `2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd` |
| `finite_video_path.py` | 10.943 | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| `live_audio_adapter.py` | 13.852 | `c37ab44ded2678a3d0a664044390bdced5de7a4c10174935e1b0025bb286a676` |
| `log_spectral_receptor.py` | 7.024 | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| `mcm_neuron.py` | 7.702 | `79cf8f8aa79d8c336c5d3fd57303a9f618e2840217c7786688112d0b7c66783a` |
| `mcm_neuron_layer.py` | 18.322 | `ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277` |
| `neutral_local_field_substrate.py` | 28.183 | `df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13` |
| `receptor_contract.py` | 7.853 | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| `receptor_distributor.py` | 7.563 | `649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad` |
| `shared_mcm_field.py` | 31.578 | `2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec` |
| `transient_neuron_input.py` | 9.799 | `1ee10351fbe97811211aa08099cd967072b9ad1bbe24e151faefd2e64cfc7546` |
| `previous_state_contribution_hook.py` | 4.568 | `42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648` |
| `__init__.py` | 64.463 | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

## Konfiguration

| Pfad | Bytes | SHA-256 |
| --- | ---: | --- |
| `.venv/pyvenv.cfg` | 215 | `db1630fa5d429e8fb601db5afbc5ad6f32b31bb45ce5d16b204e30ea4cb1b9b8` |

Die Datei bindet die bestehende venv an `C:\Python314` und Python `3.14.4`. Dies ist
eine Bytebeobachtung, kein Nachweis der Laufzeitumgebung.

## Entscheidungsdokumente

Alle Pfade liegen unter `docs/forschung/`.

| Dokument | Bytes | SHA-256 |
| --- | ---: | --- |
| `192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | 9.019 | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `202_ERNEUTE_HUERDE_A_UMFANGSBINDUNG_PRIVATE_EINMALVERKETTUNG_RUNTIME_FIXIERUNG.md` | 8.820 | `8365dbf825962d10acd11a9422b507e412bda19f71a0613ad1d7bf7e84674bfd` |
| `203_ERNEUTE_HUERDE_B_EINMALLAUFVERTRAG_PRIVATE_VERKETTUNG_RUNTIME_FIXIERUNG.md` | 4.776 | `53456fb230bc3a4eb7d45a9464abaefc8c7eec7d20fcfbec030a88930ecd4a52` |
| `204_ERNEUTE_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | 4.228 | `ec0cead77a18d2b3ca0ba1caca43c0baf96d5af269ea8512fe72ff4823018671` |
| `205_ERNEUTE_HUERDE_D_EINGANGS_UND_QUELLENBINDUNG_PRIVATE_EINMALVERKETTUNG.md` | 5.017 | `8cf2f6671e911884e253fc66938f522b1a0722499c9333cfa57994206fc0e04e` |
| `206_ERNEUTE_HUERDE_E_AUSGABE_UND_SEITENEFFEKTGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | 5.289 | `ccca9c42afb11a03f4aa3460b275b1a8426e8a4b035a92ed146c404fbe2aced4` |
| `207_LAUF_ERNEUTE_HUERDE_F_GESCHLOSSENE_PRIVATE_EINMALVERKETTUNG.md` | 8.474 | `da5abac6b88da15887dfef568afce44432c59101986e5de98461d8e5fe55d01c` |
| `208_LAUF_HUERDE_G_DOKUMENTARISCHE_ENTSCHEIDUNG_EINMALLAUF_GESPERRT.md` | 7.812 | `13176a3c7a5725b14b8733c35cd5433b03948c2b1923c512737546ec5bc51c38` |
| `212_LAUF_STATISCHE_APPCONTAINER_KOMPATIBILITAETSANALYSE_PYTHON_KORRIDOR.md` | 11.798 | `038bee5072278a2f8f3a3921d6e8d9c848d7a5a2c1b4df6bdc4304f42992a5a7` |
| `213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md` | 12.300 | `5fdc9731ae6951378dbdfd8131063a7d0e59440e062b7dda8c408d6af6622170` |
| `213B_STATISCHE_APPCONTAINER_ACL_PROFIL_TEMP_CACHE_DIAGNOSEKARTE.md` | 14.612 | `4f9417b5c9a4048aa90e47e8cb697bd7e7948380875de53e26cc20eba7b34223` |
| `213C_STATISCHE_PACKAGE_CAPABILITY_SID_ACE_SOLLMATRIX.md` | 17.024 | `26618ee68d929530fa9422f240ed4d47a1dfbb7ea1c116ac820e7596024526da` |
| `213D_READ_ONLY_ACL_MANDATORY_LABEL_ISTAUFNAHME.md` | 13.024 | `fd5ea77b5babf82c6d034122cae18203217e3fea2259f49c4e1b86e2c0a97e86` |
| `213E_STATISCHE_LOADER_STDLIB_NUMPY_SYSTEM_DLL_PFADBAUM_ISTAUFNAHME.md` | 10.346 | `bf9ef11e646dadadc9f37e8b0280758bc8ca9900139f7ca6414eb87587b2ac03` |
| `213F_STATISCHER_NACHWEISKATALOG_VOR_HUERDE_G_ENTSCHEIDUNG.md` | 11.807 | `76793ffedd860058751540e7e7eea074d2fe6222de4468c9700255ebaefc44f2` |

## Native Seeds

Die vier Loader-/Python-Dateien:

| Pfad | Bytes | SHA-256 |
| --- | ---: | --- |
| `C:/Python314/python.exe` | 106.328 | `7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a` |
| `C:/Python314/python3.dll` | 74.072 | `1dd696f02326e32e67b52c25b249b3acce3238176212d16e8fb1a050a1455ae9` |
| `C:/Python314/python314.dll` | 6.767.440 | `a07f7d09c3121492bb066535c6d0811df5fbc2090cbca7031a97bb47ce1480c9` |
| `.venv/Scripts/python.exe` | 255.320 | `4b8c3912806b3c1591ba3cb403bff77ad309c3fe5756f87c20b7a6f8f0174262` |

Die 19 Pfade liegen unter `.venv/Lib/site-packages/numpy/`:

| Datei | Bytes | SHA-256 |
| --- | ---: | --- |
| `fft/_pocketfft_umath.cp314-win_amd64.pyd` | 276.480 | `0fb0d660b2b608a270828d34fb79d4e14b2c33e1ba799aac7232b714e36a4742` |
| `linalg/lapack_lite.cp314-win_amd64.pyd` | 18.944 | `4cef8f26be5895a6973b3c969d024cab1c3c777df675059ca20a69d22fdc7b49` |
| `linalg/_umath_linalg.cp314-win_amd64.pyd` | 112.128 | `8264d9d70a1a1d72793805a989fc5ebab8d55970e44a829e1262fd58335ff8d5` |
| `random/bit_generator.cp314-win_amd64.pyd` | 168.448 | `d481331eca4f875eb6e53a69d722c6bf03a915b6e2033f91daf2bad2efcb7133` |
| `random/mtrand.cp314-win_amd64.pyd` | 500.736 | `cd83271cc04fb0219fb5d5cb06c5117f60291866a88e332b7c8e8276375d1344` |
| `random/_bounded_integers.cp314-win_amd64.pyd` | 215.040 | `52e8867a30524db560f6ffe9b3edb63beaa8160dd349ffa9cb8eaeeff786c486` |
| `random/_common.cp314-win_amd64.pyd` | 173.056 | `54809657fb43a25138617f9706ef781d9e9502b66a9a5366ea7bd76eed918f61` |
| `random/_generator.cp314-win_amd64.pyd` | 599.040 | `15215ee2ae4c1ec0960c29d433871a8e6ba4c392b8dee367541fb736f9c6d4c6` |
| `random/_mt19937.cp314-win_amd64.pyd` | 86.528 | `434ab2857d104ff19c3b5008916197787fcc253339eabc66a16e4bdecfc1c74c` |
| `random/_pcg64.cp314-win_amd64.pyd` | 96.256 | `b469cbc850ee42a8ca5b5a9b58811d529fc0c7b65dbc7eb4b9d24b924b4b8d07` |
| `random/_philox.cp314-win_amd64.pyd` | 81.408 | `5b7ffd698d931acade2970fd318fa077e14f634ed08d32678a44c2997cebc600` |
| `random/_sfc64.cp314-win_amd64.pyd` | 60.416 | `1e4d72bccc8045c798d13529439d907ce1f1f2d40e6a635f7d4de93d1f4ca9e6` |
| `_core/_multiarray_tests.cp314-win_amd64.pyd` | 66.048 | `7c6f3e0793c6ede96204639b5798693786efe9d35a5fab7a86d4a5f9d559e229` |
| `_core/_multiarray_umath.cp314-win_amd64.pyd` | 3.904.512 | `ab5cea76a0fad4fd1bc58667aefba1382a7ce8c147b51cf3bff53eec4efb4ab2` |
| `_core/_operand_flag_tests.cp314-win_amd64.pyd` | 12.288 | `322d6717b0a56e29d303f993bdaa853bfa44f9bb189ee6709b8b3c208cc04efe` |
| `_core/_rational_tests.cp314-win_amd64.pyd` | 43.520 | `ea67ac1b1cf3d644e1f038a0b56bfe6a5770478956e2d55ae393549892edea78` |
| `_core/_simd.cp314-win_amd64.pyd` | 831.488 | `27b44fa3be39216e416c529fad5f2af9196a02d1ca51d6d08abec41bf9fbdd09` |
| `_core/_struct_ufunc_tests.cp314-win_amd64.pyd` | 14.336 | `380216da0e2d51dcce8a973fdda3291beb7dee743e43802e0cc8710492c08cc4` |
| `_core/_umath_tests.cp314-win_amd64.pyd` | 34.304 | `7b042f544cfe99e846fd188d0b0065ae6455a4c1c104578e69cb535727956214` |

Die zwei Pfade liegen unter `.venv/Lib/site-packages/numpy.libs/`:

| Datei | Bytes | SHA-256 |
| --- | ---: | --- |
| `libscipy_openblas64_-b788215d9d47792bcba3a2e2a7114320.dll` | 20.405.760 | `b788215d9d47792bcba3a2e2a71143205a57282828a483f1fb071ca2c159f616` |
| `msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` | 575.056 | `a4c2229bdc2a2a630acdc095b4d86008e5c3e3bc7773174354f3da4f5beb9cde` |

## Offene Byte- und Umfangsabweichungen

### A1 - Hook-Digestabweichung

`_runtime_fixation_structure.py::_SOURCE_DIGESTS` erwartet fuer
`previous_state_contribution_hook.py` weiterhin
`2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e`.
Beobachtet ist
`42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648`.
Damit passen weiterhin nur `7/8` eingebettete Quelldigests. Die Abweichung wurde
weder inhaltlich bewertet noch korrigiert.

### A2 - Umfangsabhaengigkeit von G1 und G2

Der aktuelle Korpus bindet die 25 breiten nativen Seeds, aber noch nicht die konkrete
Python-/NumPy-Dateiauswahl eines vorgesehenen Starts und nicht die Dateien aus
Loader-Sonderpfaden. Diese Mengen werden erst durch G1 und G2 bestimmbar. G0 kann
deshalb vor deren Abschluss nur als aktuelle Teilbindung, nicht als endgueltiger
Huerde-G-Byteabschluss gelten.

### A3 - Dokumentfortschreibung

Dieses neu erzeugte Dokument ist selbst noch nicht in seiner eigenen Eingangsliste
enthalten und muss nach unabhaengiger Pruefung mit seinem finalen SHA-256 in eine
spaetere kumulative G0-Bindung aufgenommen werden. Selbstreferenz wird nicht durch
einen behaupteten stabilen Eigenhash vorgetaeuscht.

## Durchgefuehrte Schritte

1. Den bekannten Korpus aus 213A, 213E und 213F festgelegt.
2. Alle 63 Pfade read-only auf Existenz geprueft.
3. Bytegroessen und SHA-256 fuer jede Datei erhoben.
4. Klassenzaehler und Bytesummen gebildet.
5. Die eingebettete Hook-Digestabweichung und die von G1/G2 abhaengige
   Umfangsluecke getrennt ausgewiesen.

## Messergebnisse und Gegenbaselines

- bekannte relevante Dateien: `63`;
- vorhandene Dateien: `63/63`;
- fehlende Dateien: `0/63`;
- gebundene Bytes: `35.896.473`;
- Projektquellen: `22`;
- Konfigurationen: `1`;
- Entscheidungsdokumente: `15`;
- native Seeds: `25`;
- passende eingebettete Quelldigests: `7/8`;
- offene Byteabweichungen: `1`;
- offene Umfangsabweichungen: `2` (G1/G2-Erweiterung und spaetere Eigenaufnahme);
- Imports, Tests, Prozesse und Sicherheitsaktionen: jeweils `0`.

Gegenbaselines:

| Gegenbaseline | Befund |
| --- | --- |
| nur 20 private relative Importmodule | uebersieht Hook-Dateiverweis und `__init__.py` |
| nur acht `_SOURCE_DIGESTS`-Dateien | bindet weder gesamten Projektgraphen noch Dokumente oder native Seeds |
| nur 25 native Seeds | bindet nicht alle 37 PE-Knoten und keine Python-/Datendateien |
| 4.831 installierte Bibliotheksdateien pauschal binden | waere breit, aber noch kein konkreter Laufzeitumfang |
| aktueller 63-Dateien-Korpus als vollstaendiges G0 ausgeben | methodisch falsch, solange G1/G2 offen sind |

## Grenzen und nicht gepruefte Annahmen

- **Beobachtet:** Alle 63 aktuell ausgewaehlten Dateien existieren und sind
  hashbar; ein eingebetteter Quelldigest weicht ab.
- **Technische Interpretation:** Der bekannte Korpus ist reproduzierbar gebunden,
  aber wegen A1 bis A3 nicht freigabefaehig.
- **Hypothese:** Nach Klaerung der Hook-Abweichung und Abschluss von G1/G2 kann eine
  kumulative G0-Neubindung einen geschlossenen Byteumfang ergeben.
- **Offene Frage:** Welche zusaetzlichen Dateien G1/G2 exakt ergeben, ist hier nicht
  untersucht.
- **Nicht gepruefte Annahme:** Die 22 Projektquellen umfassen jede durch einen
  spaeteren Start gelesene Projektdatei; dynamische Laufzeitbeobachtung war gesperrt.
- Installierte Dateibaeume wurden nicht erneut vollstaendig gehasht.
- Keine Aussage betrifft Lauffaehigkeit, Feldwirkung, Memory, Organisation,
  Topologie, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Der bekannte G0-Korpus ist mit 63 vorhandenen Dateien und 35.896.473 Bytes statisch
gebunden. G0 ist dennoch **nicht bestanden**. Die Hook-Bytebindung ist inkonsistent,
der endgueltige Umfang haengt von G1/G2 ab, und 213G muss nach seiner unabhaengigen
Pruefung erst in eine spaetere kumulative Bindung aufgenommen werden.

Huerde G, Implementierung, Projektimporte, Tests, Prozessstarts, SID-Ableitung,
Profilanlage, ACL-/Systemaenderungen und SACL-Abfragen bleiben gesperrt.

## Naechster begrenzter Schritt

Als naechster Schritt ist ausschliesslich die unabhaengige statische Pruefung von
213G zulaessig. Zu reproduzieren sind Auswahlregeln, 63/63 Existenzbefunde,
Klassenzaehler, Bytesummen, Einzelhashes und die drei offenen Abweichungsklassen.

Eine Korrektur der Hook-Bytebindung oder die Bearbeitung von G1/G2 bedarf eines neuen,
jeweils eng begrenzten Auftrags. Aus 213G folgt keine automatische Anschlussfreigabe.

## Zielabweichung

Keine erkennbare Zielabweichung. Das Paket bindet nur den aktuellen technischen
Korpus und behauptet keine MCM-, Memory-, Organismus- oder KI-Funktion.

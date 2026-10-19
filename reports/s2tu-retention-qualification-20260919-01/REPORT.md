# S2-TU-Neutralqualifikation 20260919-01

Status: `QUALIFIED`.

Der einmalige, ausschließlich neutrale Aufruf lief mit `7/7` bestandenen
Prüfungen. Er materialisierte keine S2-TU-Quelle.

Geprüft wurden: vollständige 23-Ereignis-Kette, 20 Endpunktbindungen,
12 Formationen, acht Hintframes, drei Segmentabschlüsse, FIFO-Ersetzung,
vier Entscheidungen, finaler Owner-Abschluss sowie eine unabhängige
read-only Verifikation. Manipulierte Quellen-, Werte-, Übergangs-,
Entscheidungs- und Owner-Belege wurden typisiert abgewiesen.

Die Vollhülle bleibt unter `262144` Byte; der reale Einzelbeleg wird vor
Veröffentlichung erneut gegen diese Grenze geprüft. `5376` Byte sind nur
die gebundene Vektor-Spitze: zwei gehaltene Vierertraces, aktive Formation
und Hintpuffer. Sie sind keine vollständige Zustands- oder Beleggrenze.

Gebundene Dateien, SHA-256:

* `_s2tu_retained_trace.py`: `bf530380f93c8a1bf0eeae5a4169e81bc99aee10050872e3e5ddc7bfdb88f3f6`
* `_s2tu_source_schedule.py`: `1242ef19973864fac449b1955da039d896fd962fadfe57f1ac4328cc1ecabf33`
* `_s2tu_run.py`: `f1d53c97332634f3fcdb8af8010aff30571ebe6d208bf24652f2ffaf5c0a8ae8`
* `_s2tu_verification.py`: `257e627b932f4896c5b7fe9a3f66accce009c79c7f7448669b75613b0b00cd9b`
* `test_s2tu_retained_trace.py`: `7c70150cb901a446c67647a3ffe01522307bd72ca3dcfa27e3018beca9ebf554`
* `test_s2tu_source_schedule.py`: `12523dfdca641b56f5a92f193558714995a827a01f6450bd2357266d754d8b21`
* `test_s2tu_verification.py`: `7d487f2234569ef75e7e84e6c410184f6a80566fd6abb14735ad6e0088ef2804`

Die Quellenwurzel ist unverändert an
`6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10`
gebunden. Feld, A/B-Auflösung und Hypothesenanwendung bleiben außerhalb
von S2-TU.

## Begründung

Der wohl grösse Einflussfaktor auf die schlussendliche Imagegrösse hat das benutzte Python Image. Wobei die Naive Version das Image `python:3.12` benutzt, dass bereits eine Speichergrösse von 1.62 GB hat, benutzt das optimierte Image die schlanke Version von Python 3.12 mit dem Image `python:3.12-slim`. Dieses Image benötigt gerade einmal 179MB an Speicherplatz. Dies entspricht ungefähr 11 Prozent des Naiven Images.

**Auflistung Image Size**

| Image Type | Size    | Python Image     | Python Size |
| ---------- | ------- | ---------------- | ----------- |
| Naiv       | 1.67 GB | python:3.12      | 1.62GB      |
| Optimiert  | 217 MB  | python:3.12-slim | 179MB       |

Des weiteren hilft `.dockerignore` das Image klein zu halten, in dem es alle Files und Folders, welche nicht ins Image gehören auch nicht mit baut. Dadurch wird das Image kleiner.

Die mehreren Stages tragen auch dazu bei, dass das Image klein bleibt in dem die Build-Artefakte und Caches nicht in der Runtime drin sind.

Um das Image sicher zu machen wird ein Applikationspezifischer Benutzer verwendet anstelle des root Benutzers. Dies hat den Nutzen, dass falls jemand aus dem Docker ausbrechen könnte dort keine Root Berechtigungen hat sondern nur diejenige des App-Users.
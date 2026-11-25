**English** · [Türkçe](README.tr.md)

<div align="center">

# Yardım Masası

**A PyPI version lookup, a support ticket summary, and a FastAPI application that stores tickets in PostgreSQL. In a single Python package.**

![Python](https://img.shields.io/badge/Python-3.15-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-2ea44f)

[Highlights](#highlights) · [Setup and running](#setup-and-running) · [Commands](#commands) · [API summary](#api-summary) · [Tests](#tests)

</div>

Yardım Masası (Help Desk) has three parts. The `yardim-masasi` command shows the latest version on PyPI of the given Python packages and the Python version range each one supports. The `talep-ozeti` (ticket summary) command summarizes the support tickets in a JSON or JSON Lines file. The FastAPI application stores the tickets in PostgreSQL and serves them over HTTP.

The project is also a worked example on the Python interpreter, virtual environments, `uv`, dependency management and environment variables. It is written with Python 3.15, FastAPI, psycopg, Alembic, httpx and uv.

> Command output, API field names and error messages are in Turkish. The detailed documents under `docs/` and the notes under `notes/` are in Turkish.

## Highlights

- **PyPI lookup:** queries packages without installing them; requests run concurrently (default limit 4), and the output is written in the order the packages were given on the command line.
- **Retries:** connection and timeout errors are retried two more times, half a second apart; HTTP status errors are not retried.
- **Ticket summary:** counts tickets by status and lists the ones that are not closed in priority order; the status, priority, tag and last N days filters are applied together.
- **Validation and exit codes:** every ticket is validated as it is read; the commands return `0` on success, `1` on a data or network error, and `2` on a usage error.
- **HTTP API:** eight endpoints; listing, reading, creating and updating tickets, a status summary, comments and a health check.
- **Pagination:** the cursor is not a page number but the `(acildi, id)` pair of the last ticket (`acildi` is the time the ticket was opened); pages do not shift even if a new ticket is opened between two pages.
- **Search:** in ticket titles, with PostgreSQL's Turkish full-text search; the `or`, `-word` and quoted phrase syntaxes work.
- **Conditional requests:** `ETag`, `If-Match` and `If-None-Match`; a `PATCH` that arrives with an old version gets `412` and nothing is written.
- **Migrations:** the schema is built by five Alembic revisions; the tests check that each revision can be rolled back and applied again.
- **Containers:** `docker compose up` starts the database, the migrations and the API in order; the image is two-stage and runs as a non-root user.
- **Tests and type checking:** pytest and pyright; the store tests run the same contract both in memory and on PostgreSQL.

## Requirements

- [uv](https://docs.astral.sh/uv/): manages Python and the project dependencies.
- Python 3.15: selected in the `.python-version` file. If no suitable interpreter is present, uv can install it when automatic downloads are enabled.
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose: the PostgreSQL database and, optionally, the API run in containers.
- An internet connection, to download packages on first setup and for PyPI queries.

## Setup and running

```bash
git clone https://github.com/ismailarat56/yardim-masasi.git
cd yardim-masasi
uv sync --locked
```

The command-line tools do not need a database:

```bash
uv run yardim-masasi httpx fastapi
uv run talep-ozeti
uv run talep-ozeti --oncelik yuksek --etiket hesap
uv run talep-ozeti ornek/talepler-zamanli.jsonl --son-gun 10
```

To start the API in containers, together with the database and the migrations:

```bash
cp .env.example .env
cp .env.db.example .env.db
docker compose up -d --build --wait
docker compose exec api talep-yukle
```

The server starts at `http://127.0.0.1:8000`; `http://127.0.0.1:8000/docs` shows the automatic documentation, where the endpoints can be tried from the browser. `talep-yukle` (load tickets) loads the sample tickets.

To run the API on the machine itself, so that it restarts when the code changes, only the database is started in a container, with the same `.env` and `.env.db` files. If the API container is running, stop it first with `docker compose stop api`.

```bash
docker compose up -d db
uv run --env-file .env alembic upgrade head
uv run --env-file .env fastapi dev src/yardim_masasi/api.py
```

Details: [docs/KURULUM.md](docs/KURULUM.md) (setup and environment variables), [docs/VERITABANI.md](docs/VERITABANI.md) (database and migrations), [docs/DOCKER.md](docs/DOCKER.md) (services and image).

## Commands

| Command | Function |
|---|---|
| `yardim-masasi [-e N] PAKET [PAKET ...]` | Shows the latest version on PyPI and the Python version range of the packages (`PAKET` is a package name). `-e` is the concurrent query limit. |
| `talep-ozeti [dosya]` | Summarizes the tickets in a `.json` or `.jsonl` file (`dosya`). If no file is given, `ornek/talepler.json` is read. |
| `talep-yukle [dosya]` | Loads the sample tickets into the database. If no file is given, `ornek/talepler-zamanli.jsonl` is read. |

`talep-ozeti` flags: `--durum` (status), `--oncelik` (priority), `--etiket` (tag), `--son-gun N` (last N days), `-v` / `--ayrintili` (verbose), `--version`. The summary goes to stdout; logs and error messages go to stderr.

All flags, exit codes, log records and the format of the ticket file: [docs/KOMUT_SATIRI.md](docs/KOMUT_SATIRI.md)

## API summary

| Endpoint | Function |
|---|---|
| `GET /saglik` | Sends `SELECT 1` to the database; returns `503` if it cannot be reached (`saglik` means health). |
| `GET /talepler` | Lists the tickets (`talepler`) from newest to oldest, page by page; takes the `durum`, `oncelik`, `etiket`, `ara` (search), `limit` and `ayrac` (cursor) parameters. |
| `GET /talepler/ozet` | Returns the number of tickets in each status. |
| `GET /talepler/{talep_id}` | Returns a single ticket; the `ETag` header holds the version of the ticket. |
| `POST /talepler` | Creates a new ticket. |
| `PATCH /talepler/{talep_id}` | Changes the status, the priority or both, if the version in `If-Match` is current. |
| `GET /talepler/{talep_id}/yorumlar` | Lists the comments (`yorumlar`) of the ticket in the order they were added. |
| `POST /talepler/{talep_id}/yorumlar` | Adds a comment to the ticket. |

The read endpoints are open. The `POST` and `PATCH` endpoints require the server's `API_ANAHTARI` (API key) value in the `X-API-Anahtari` header; on a server where the key is not set, writing is disabled entirely.

Error codes, pagination, search syntax, conditional requests and sample requests: [docs/API.md](docs/API.md)

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `PYPI_ZAMAN_ASIMI` | `10` | Timeout of the PyPI request, in seconds. |
| `DATABASE_URL` | none | The database that the API, `talep-yukle` and the `alembic` commands connect to. |
| `TEST_DATABASE_URL` | none | The database for the PostgreSQL tests. It must not point to the main database; its schema is dropped and rebuilt in every test session. |
| `API_ANAHTARI` | none | The `X-API-Anahtari` value expected for `POST` and `PATCH`. |

uv does not read the `.env` file on its own; it is passed with `--env-file .env`. `.env` and `.env.db` are not included in Git. Details: [docs/KURULUM.md](docs/KURULUM.md#ortam-değişkenleri)

## Folder structure

```
src/yardim_masasi/
  __init__.py     yardim-masasi command: arguments, concurrent queries, exit codes
  pypi.py         PyPI queries and summary format
  eszamanli.py    bounded concurrent gathering and async retry
  araclar.py      synchronous retry decorator
  model.py        ticket model, validation and file reading
  akis.py         line-by-line reading and JSON Lines generators
  filtre.py       status, priority, tag and opening time filters
  talepler.py     counting, sorting, search and the talep-ozeti command
  depo.py         in-memory ticket store
  metin.py        Turkish text helpers
  veritabani.py   DATABASE_URL reading and the talep-yukle command
  pg_depo.py      PostgreSQL ticket store
  sayfa.py        pagination cursor
  sema.py         Pydantic schemas for API bodies and responses
  api.py          FastAPI application
migrations/       Alembic environment and revisions (versions/)
tests/            pytest tests and tip_araclar.py, which is checked with pyright
ornek/            sample ticket files (.json, .jsonl)
docs/             detailed documents
notes/            daily work notes
compose.yaml      db, migrate and api services
Dockerfile        two-stage image
pyproject.toml    project definition, dependencies and command entry points
uv.lock           locked dependency versions
```

Detailed description of the modules: [docs/MIMARI.md](docs/MIMARI.md)

## Tests

```bash
uv run --locked --env-file .env pytest -q
uv run pyright
```

The PostgreSQL tests need the database container to be running and the test database to be created once:

```bash
docker compose exec db createdb -U yardim yardim_masasi_test
```

Without `--env-file .env`, `TEST_DATABASE_URL` is not defined and the PostgreSQL tests are skipped; the in-memory copies of the same store tests and the API tests also run when Docker is stopped.

What the tests check, type checking and dependency management: [docs/GELISTIRME.md](docs/GELISTIRME.md)

## Known limitations

- The API key is a single value shared by everyone. There is no separation between users; who created or changed a ticket is not recorded.
- Pages only go forward. The response has no total ticket count or page count.
- Search covers only the title. The Turkish stemmer cannot match some suffixed words with their base forms.
- A single uvicorn process runs in the container. Base images are selected by tag, not pinned by digest.
- There is no cache for PyPI queries.

Full list: [docs/BILINEN_SINIRLAMALAR.md](docs/BILINEN_SINIRLAMALAR.md)

## License

The code is released under the [MIT license](LICENSE).

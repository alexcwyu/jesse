# jesse maintenance validation

Recorded 2026-10-12T01:32:45.614228+08:00. Branch `feature/ayu_develop`; upstream default `upstream/master` is merged: **true**. Branch/tag synchronization records are retained in the workspace maintenance evidence. Feature branch publication is coordinated separately.

Runtime: **CPython 3.14.8**, uv **0.13.0**, build backend `hatchling.build`. Python 3.15 was attempted: Numba/Tulipy dependency support prevented the full environment. Python 3.14.8 is selected. The local jesse-rust native source separately builds on Python 3.15.

Existing suite: **================= 1970 passed, 18 skipped in 275.31s (0:04:35) =================** (exit `0`). Full existing tests pass with local ../jesse-rust. Rust coordinator coverage is included when cargo is on PATH; the separate existing coordinator suite also passes. MCP remains on the newest compatible 1.x API because 2.x changed existing HTTP/MCP behavior.

No test cases were added. Existing assertions and strict warning behavior remain active; repaired fixtures own their loops, sessions, files and configuration paths. Existing upstream platform skips and configured deselections are reported exactly.

## Final build commands

| Check | Exact command | Exit | Seconds |
| --- | --- | ---: | ---: |
| lock | `uv lock --upgrade` | 0 | 0.44 |
| sync | `uv sync --all-extras --frozen --python 3.14.8` | 0 | 49.24 |
| build | `uv build --python 3.14.8` | 0 | 21.71 |
| compile | `.venv/bin/python -m compileall -q src` | 0 | 0.24 |

## Existing test and compatibility evidence

| Check | Exact command | Exit | Result |
| --- | --- | ---: | --- |
| lock-3.15 | `uv lock --upgrade --python 3.15` | 0 | Check completed; see exact exit code. |
| sync-3.15 | `uv sync --all-extras --python 3.15` | 2 | Check completed; see exact exit code. |
| tests | `/Users/alex/workspaces/trading/jesse/.venv/bin/python -m pytest tests` | 2 | ============================== 17 errors in 5.34s ============================== |
| backtest-diagnostic | `.venv/bin/python -m pytest tests/test_backtest.py -x` | 1 | ============================== 1 failed in 0.50s =============================== |
| tests-2 | `.venv/bin/python -m pytest tests` | 1 | ============ 1 failed, 1916 passed, 71 skipped in 271.23s (0:04:31) ============ |
| tests-3 | `.venv/bin/python -m pytest tests` | 0 | ================= 1917 passed, 71 skipped in 293.61s (0:04:53) ================= |
| tests-4 | `.venv/bin/python -m pytest tests` | 0 | ================= 1970 passed, 18 skipped in 275.31s (0:04:35) ================= |

Raw logs remain in the workspace maintenance evidence directory. The [portable verification record](maintenance/verification.json) retains exact command arrays, exits, timing, runtime inventory and log filenames. Earlier failed attempts remain recorded and are not treated as successful final validation.

## Installed dependency versions

This is the selected environment after locked synchronization; isolated wheel build dependencies are resolved by the build backend and recorded in build output.

| Distribution | Version |
| --- | --- |
| aiofiles | 25.1.0 |
| alembic | 1.20.0 |
| annotated-doc | 0.0.5 |
| annotated-types | 0.8.0 |
| anyio | 4.15.1 |
| arrow | 1.4.0 |
| attrs | 26.1.0 |
| bitarray | 3.12.0 |
| blinker | 1.9.0 |
| certifi | 2026.7.22 |
| cffi | 2.1.1 |
| charset-normalizer | 3.5.2 |
| ckzg | 2.1.8 |
| click | 8.5.0 |
| cloudpickle | 3.1.2 |
| colorlog | 6.12.0 |
| contourpy | 1.4.0 |
| cryptography | 50.0.2 |
| cycler | 0.12.1 |
| cytoolz | 1.2.0 |
| ecdsa | 0.19.2 |
| eth-account | 0.14.0 |
| eth-hash | 0.8.0 |
| eth-keyfile | 0.10.0 |
| eth-keys | 0.8.0 |
| eth-rlp | 3.0.0 |
| eth-typing | 6.0.0 |
| eth-utils | 6.0.0 |
| eth_abi | 6.0.0 |
| fastapi | 0.143.0 |
| filelock | 4.1.1 |
| fnc | 0.5.3 |
| fonttools | 4.66.1 |
| formulaic | 1.2.2 |
| h11 | 0.16.0 |
| hexbytes | 2.0.0 |
| httpcore | 1.0.9 |
| httpx | 0.28.1 |
| httpx-sse | 0.4.3 |
| idna | 3.20 |
| iniconfig | 2.3.1 |
| interface_meta | 2.0.1 |
| jesse | 3.3.1 |
| jesse-rust | 1.3.1 |
| joblib | 1.6.0 |
| jsonschema | 4.26.0 |
| jsonschema-specifications | 2025.9.1 |
| kiwisolver | 1.5.1 |
| Mako | 1.4.3 |
| MarkupSafe | 3.0.4 |
| matplotlib | 3.11.2 |
| mcp | 1.30.0 |
| msgpack | 1.2.3 |
| narwhals | 2.27.1 |
| numpy | 2.5.4 |
| opentelemetry-api | 1.45.1 |
| optuna | 5.0.0 |
| packaging | 26.3 |
| pandas | 3.0.6 |
| parsimonious | 0.10.0 |
| patsy | 1.0.3 |
| peewee | 4.5.3 |
| pillow | 12.3.0 |
| pluggy | 1.6.0 |
| protobuf | 7.36.2 |
| psycopg2-binary | 2.9.13 |
| py-ecc | 8.0.0 |
| pycparser | 3.11 |
| pycryptodome | 3.24.0 |
| pydantic | 2.14.0 |
| pydantic-settings | 2.15.0 |
| pydantic_core | 2.50.0 |
| pydash | 8.1.0 |
| Pygments | 2.21.0 |
| PyJWT | 2.15.1 |
| pyparsing | 3.3.3 |
| pytest | 9.1.1 |
| python-dateutil | 2.9.0.post0 |
| python-dotenv | 1.2.4 |
| python-multipart | 0.0.32 |
| PyYAML | 6.0.3 |
| ray | 2.59.0 |
| referencing | 0.37.0 |
| regex | 2026.9.29 |
| requests | 2.34.2 |
| rlp | 5.0.0 |
| rpds-py | 2026.9.1 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| simplejson | 4.2.0 |
| six | 1.17.0 |
| SQLAlchemy | 2.1.4 |
| sse-starlette | 3.5.0 |
| starkbank-ecdsa | 2.3.1 |
| starlette | 1.7.0 |
| statsmodels | 0.15.0 |
| tabulate | 0.10.0 |
| threadpoolctl | 3.7.0 |
| timeloop | 1.0.2 |
| toolz | 1.2.0 |
| tqdm | 4.70.1 |
| typing-inspection | 0.4.4 |
| typing_extensions | 4.16.0 |
| tzdata | 2026.5 |
| urllib3 | 2.8.0 |
| uvicorn | 0.54.0 |
| websocket-client | 1.9.2 |
| websockets | 17.2 |
| wrapt | 2.5.0 |
| wsaccel | 0.6.7 |

See [architecture](ayu-develop.md) for source-linked component/sequence/workflow diagrams and [development](development.md) for reproducible uv commands.

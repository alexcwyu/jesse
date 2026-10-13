# jesse: portable verification records

<!-- current-documentation-provenance -->
Documentation reviewed: 2026-10-13 / Git source base: `37c568de9cf316a9f6cca0e471335c419237f8f0` / [Current architecture and feature guide](../ayu-develop.md).
Historical execution commands/results below retain their original dates and scope; this metadata update is not a new application test run.
<!-- /current-documentation-provenance -->


Full raw logs are retained in the workspace maintenance evidence, not distributed here. Hashes identify those original logs. A successful build or selected test subset does not imply a full test-suite pass. Commands containing <workspace> describe the original execution environment.

[Machine-readable records](verification.json) · [Repository validation summary](../validation.md)

## Executed commands

| Check | Exit | Duration | Command | Outcomes |
| --- | ---: | ---: | --- | --- |
| backtest-diagnostic | 1 | 26.27s | `.venv/bin/python -m pytest tests/test_backtest.py -x` | See exit status; no test-count assertion. |
| build | 0 | 21.84s | `uv build --python 3.13` | Successfully built dist/jesse-2.3.4.tar.gz<br>Successfully built dist/jesse-2.3.4-py3-none-any.whl |
| compatible-sync | 0 | 1.26s | `uv sync --all-extras --python 3.13` | See exit status; no test-count assertion. |
| compile | 0 | 0.82s | `<workspace>/jesse/.venv/bin/python -m compileall -q src` | See exit status; no test-count assertion. |
| coordination-required | 0 | 11.55s | `.venv/bin/python -m pytest tests/test_coordination.py -rs` | ======================== 7 passed, 53 skipped in 0.24s ========================= |
| coordination-required-2 | 0 | 26.43s | `env PATH=/opt/homebrew/opt/rustup/bin:/opt/homebrew/bin:/usr/bin:/bin JESSE_COORDINATION_REQUIRE_TESTS=1 .venv/bin/python -m pytest tests/test_coordination.py -rs` | ============================= 60 passed in 13.76s ============================== |
| final-build | 0 | 47.09s | `uv build --python 3.14.8` | Successfully built dist/jesse-3.3.1.tar.gz<br>Successfully built dist/jesse-3.3.1-py3-none-any.whl |
| final-build-2 | 0 | 21.71s | `uv build --python 3.14.8` | Successfully built dist/jesse-3.3.1.tar.gz<br>Successfully built dist/jesse-3.3.1-py3-none-any.whl |
| final-compile | 0 | 0.9s | `.venv/bin/python -m compileall -q src` | See exit status; no test-count assertion. |
| final-compile-2 | 0 | 0.24s | `.venv/bin/python -m compileall -q src` | See exit status; no test-count assertion. |
| final-lock | 0 | 0.52s | `uv lock --upgrade` | See exit status; no test-count assertion. |
| final-lock-2 | 0 | 0.44s | `uv lock --upgrade` | See exit status; no test-count assertion. |
| final-sync | 0 | 0.05s | `uv sync --all-extras --frozen --python 3.14.8` | See exit status; no test-count assertion. |
| final-sync-2 | 0 | 49.24s | `uv sync --all-extras --frozen --python 3.14.8` | See exit status; no test-count assertion. |
| history-diagnostic | 0 | 18.53s | `.venv/bin/python -m pytest tests/test_mcp_live_history.py::test_shared_queries_and_hydration_leave_caller_transaction_intact` | ============================== 1 passed in 1.52s =============================== |
| local-native-sync | 0 | 78.86s | `uv sync --all-extras --python 3.14` | See exit status; no test-count assertion. |
| lock-3.13 | 0 | 0.74s | `uv lock --upgrade --python 3.13` | See exit status; no test-count assertion. |
| lock-3.14 | 0 | 0.34s | `uv lock --upgrade --python 3.14` | See exit status; no test-count assertion. |
| lock-3.15 | 0 | 0.78s | `uv lock --upgrade --python 3.15` | See exit status; no test-count assertion. |
| rust-build | 0 | unrecordeds | `uv build` | Successfully built dist/jesse_rust-1.3.1.tar.gz<br>Successfully built dist/jesse_rust-1.3.1-cp315-cp315-macosx_11_0_arm64.whl |
| rust-build-current-metadata | 0 | unrecordeds | `uv build` | Successfully built dist/jesse_rust-1.3.1.tar.gz<br>Successfully built dist/jesse_rust-1.3.1-cp315-cp315-macosx_11_0_arm64.whl |
| rust-cargo-coordinator-tests | 0 | unrecordeds | `cargo test --manifest-path coordination/Cargo.toml` | test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.20s<br>test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s<br>test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s |
| rust-cargo-tests | 0 | unrecordeds | `cargo test` | test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s |
| rust-cargo-update | 0 | unrecordeds | `cargo update` | See exit status; no test-count assertion. |
| rust-native-import | 0 | unrecordeds | `uv run --no-sync python -c import jesse_rust; import numpy as np; print(jesse_rust.ema(np.array([1., 2., 3., 4.]), 2)); print(callable(jesse_rust.run_coordinator))` | See exit status; no test-count assertion. |
| rust-python-sync | 1 | unrecordeds | `uv sync --all-groups --all-extras --python 3.15` | See exit status; no test-count assertion. |
| rust-python315-fixed-sync | 0 | unrecordeds | `uv sync --all-groups --all-extras --python 3.15` | See exit status; no test-count assertion. |
| rust-python315-modern-sync | 1 | unrecordeds | `uv sync --all-groups --all-extras --python 3.15` | See exit status; no test-count assertion. |
| sync-3.13 | 0 | 4.89s | `uv sync --all-extras --python 3.13` | See exit status; no test-count assertion. |
| sync-3.14 | 1 | 34.34s | `uv sync --all-extras --python 3.14` | See exit status; no test-count assertion. |
| sync-3.15 | 2 | 0.04s | `uv sync --all-extras --python 3.15` | See exit status; no test-count assertion. |
| tests | 2 | 21.28s | `<workspace>/jesse/.venv/bin/python -m pytest tests` | See exit status; no test-count assertion. |
| tests-2 | 1 | 277.76s | `.venv/bin/python -m pytest tests` | ============ 1 failed, 1916 passed, 71 skipped in 271.23s (0:04:31) ============ |
| tests-3 | 0 | 313.8s | `.venv/bin/python -m pytest tests` | ================= 1917 passed, 71 skipped in 293.61s (0:04:53) ================= |
| tests-4 | 0 | 287.59s | `.venv/bin/python -m pytest tests` | ================= 1970 passed, 18 skipped in 275.31s (0:04:35) ================= |

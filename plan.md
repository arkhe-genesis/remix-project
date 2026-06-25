1. **Create formal specifications and workflows**:
   - Write file `specs/squidbleed_detection.tla` containing the TLA+ specification for squidbleed detection.
   - Write file `.github/workflows/tla-check.yml` with the apalache github action check.
   - Write file `.github/workflows/kani-proofs.yml` with the kani proof action check.
   - Run `ls -la specs/` and `ls -la .github/workflows/` to verify file creations.
2. **Create documentation**:
   - Write file `CONSTITUTION.md` with the constitution content.
   - Write file `ORCHIDEAS.md` with the orchideas content.
   - Verify by running `ls -la` in root.
3. **Setup auxiliary crates**:
   - Create `Cargo.toml` and `src/lib.rs` for `crates/arkhe-core`, `crates/arkhe-agents`, `crates/arkhe-llm`, `crates/arkhe-metacognition`, `crates/arkhe-bridge` using `write_file`.
   - Add `crates/arkhe-core/src/string_safe.rs` with safe string and kani proofs.
   - Verify creation by `ls -la` and tree commands in those folders.
4. **Implement `arkhe-security-audit` crate**:
   - Write `crates/arkhe-security-audit/Cargo.toml`.
   - Write `crates/arkhe-security-audit/src/lib.rs`.
   - Write `crates/arkhe-security-audit/src/types.rs`.
   - Write `crates/arkhe-security-audit/src/hunt/mod.rs` and other phases stub files.
   - Verify by `ls -R crates/arkhe-security-audit` and running `cargo check -p arkhe-security-audit`.
5. **Update root `Cargo.toml`**:
   - Add new crates to workspace members in `Cargo.toml` using `replace_with_git_merge_diff`.
   - Run `cargo metadata --format-version 1 | grep arkhe-security-audit` and `cargo check` to verify workspace resolution.
6. **Pre-commit and verification**:
   - Run `cargo test` across the workspace to ensure tests pass.
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
7. **Submit changes**.

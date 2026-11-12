# Contributing

Use English for repository documentation, technical names, code comments, and ADRs. Keep each change focused and record the checks that support it.

1. Branch from `main` for a change with a reviewable outcome.
2. Update the decision log when proposing a design change. Record the evidence and owner approval when accepting an ADR.
3. For documentation changes, check relative links and run `git diff --check` before staging and `git diff --cached --check` after staging.
4. For source reuse, record the original repository, commit, and path, and include the relevant source tests.
5. For database work, follow the [migration plan](docs/MIGRATION_PLAN.md) and report the results from the isolated test environment.

Use a local environment file for credentials. Keep database backups, personal records, and raw archives outside Git. Once application tooling lands, the relevant setup and verification commands will be documented alongside it.

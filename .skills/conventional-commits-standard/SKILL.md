---
name: conventional-commits-standard
description: > 
  Git commit message patterns adhering strictly to Conventional Commits v1.0.0. Trigger: When writing commit messages (ONLY when user explicitly requests a commit), squashing commits, or reviewing PR titles.
license: Apache-2.0
metadata:
  author: cleteci
  version: "1.0"
  scope: [root, frontend, backend]
  auto_invoke:
    - "Committing code changes"
    - "Writing a git commit message"
    - "Formatting a Pull Request title"
allowed-tools: Bash, Git
---

## ⚠️ IMPORTANT: User Control Policy
**NEVER execute `git commit` unless the user explicitly requests it.** This skill is for formatting commit messages ONLY when the user has already instructed you to create a commit.

### When to Use This Skill
- User says: "haz commit", "dale commit", "commitea eso", "create a commit"
- User explicitly requests a git commit operation

### When NOT to Use This Skill
- After completing a task automatically
- When you think changes should be committed
- Without explicit user instruction

This skill covers commit message structure and semantics based on conventionalcommits.org.

### Commit Structure (REQUIRED)
Every commit message MUST adhere to this structure:

```plaintext
<type>[optional scope]: <description>

[required body]

[optional footer(s)]
```

### Commit Types (REQUIRED)
Must be lowercase. Use the following hierarchy to determine the type:

Type | Use Case | Triggers Release?
feat | A new feature for the user or API. | Yes (Minor/Patch)
fix | A bug fix for the user or API. | Yes (Patch)
refactor | Code change that neither fixes a bug nor adds a feature. | No
perf | Code change that improves performance. | No
test | Adding missing tests or correcting existing tests. | No
docs | Documentation only changes (README, Swagger). | No
build | Changes that affect the build system or dependencies (npm, maven). | No
ci | Changes to CI configuration files and scripts (GitHub Actions, Docker). | No
chore | Other changes that don't modify src or test files. | No
style | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons). | No

### Scopes (Optional but Recommended)
Scopes provide context about what section of the codebase was modified. Enclose them in parentheses. In this monorepo, scopes should generally reflect the architecture:

```plaintext
# ✅ GOOD: Clear boundary context
- Fixes xxxx
- Improvements on xxxx
- Add unit tests for xxxx

feat(ui): add user profile component
- Fixes xxxx
- Improvements on xxxx
- Add unit tests for xxxx

fix(api): resolve null pointer exception in auth service
- Fixes xxxx
- Improvements on xxxx
- Add unit tests for xxxx

build(deps): update spring boot to 3.2.0

```

### Subject Line: Imperative Mood (REQUIRED)
The description (subject) MUST use the imperative, present tense: "change" not "changed" nor "changes". It must not end with a period.

```plaintext
# ✅ GOOD: Imperative mood, lowercase, no period
feat(auth): add JWT validation filter
fix(ui): correct button alignment on mobile

# ❌ BAD: Past tense, capitalized, trailing period
Feat(auth): Added JWT validation filter.
Fix(ui): Corrects button alignment.
```

### Breaking Changes (REQUIRED)
If a commit introduces a breaking change (e.g., changing an existing API contract, removing a feature), it MUST be indicated by:

1. An exclamation mark ! after the type/scope.
2. A BREAKING CHANGE: footer.

```plaintext
# ✅ GOOD: Exclamation mark syntax
feat(api)!: remove deprecated v1 user endpoint

# ✅ GOOD: Footer syntax
refactor(auth): migrate from basic auth to OAuth2

BREAKING CHANGE: the `Authorization` header now strictly requires a Bearer token.
```

### Body (REQUIRED) and Footers (Optional)
Use the body to explain what and why (not how) enumaring the changes purposes. Use footers to reference issue trackers.

```plaintext
fix(db): optimize user query execution

The previous query was doing a full table scan which caused timeouts 
on tables with > 1M records. Added an index and refactored the JPA query.

Resolves: #123
See also: #456
```

### What NOT to Write

```plaintext
# ❌ Meaningless messages
update files
wip
fix bug
test

# ❌ Mixing multiple types in one commit
feat and fix: add login and fix layout
# (Squash these into separate commits or pick the most dominant type)
```

### Git Author (REQUIRED — always verify before committing)

**All commits in ALL repositories MUST use:**
- `user.email = carloscapella01@gmail.com`
- `user.name = Carlos Capella`

Before every commit, verify:
```bash
git config user.email   # must be carloscapella01@gmail.com
git config user.name    # must be Carlos Capella
```

If wrong, fix it first:
```bash
git config user.email "carloscapella01@gmail.com"
git config user.name "Carlos Capella"
```

### Commands

```bash
# Standard commit
git commit -m "feat(ui): implement generic table component"

# Commit with body (using HEREDOC — preferred to avoid quoting issues)
git commit -m "$(cat <<'EOF'
fix(api): handle missing pagination params

Defaulting to page 0 and size 20 to prevent query failures.
EOF
)"

# Amending the last commit message (if it violates conventional commits)
git commit --amend -m "chore(deps): bump angular to v21"
```

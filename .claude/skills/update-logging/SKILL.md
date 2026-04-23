---
name: update-logging
description: Apply OCS-CI logging guidelines to a Python test file or module
authoritative_source: docs/logging_guide.md
last_synced: 2026-04-23
args:
  file_path:
    description: Path to the Python file to update
    required: true
---

# Update Logging

This skill applies the OCS-CI logging guidelines from `docs/logging_guide.md` to a Python test file or module.

**Authoritative Source**: `docs/logging_guide.md` is the single source of truth for all logging guidelines.
This SKILL.md provides a quick reference checklist and common patterns derived from that guide.

## What This Skill Does

1. Ensures proper logger setup (`logger = logging.getLogger(__name__)`)
2. Adds strategic logging at key points in the code
3. Fixes common logging anti-patterns
4. Ensures appropriate log levels are used
5. Adds context to log messages

## Scan for Issues

Use this to identify logging issues in the file. For detailed patterns and examples, see `docs/logging_guide.md`.

### Logger Setup Issues (Fix First)
- Variable named `log` instead of `logger`
- Logger created inside functions (creates new logger on every call)
- Missing `import logging`
- Missing `logger = logging.getLogger(__name__)`
- Logger not placed immediately after imports
- Custom logger name instead of `__name__`
- Getting root logger with `logging.getLogger()` (no argument)

### Anti-Patterns to Fix
- `logger.error()` in except blocks → use `logger.exception()`
- Assertion logs AFTER assert statements → move BEFORE
- INFO level inside loops → change to DEBUG
- Generic messages without context ("Processing", "Failed", "Done")
- Decorative framing (lines of `===`, `---`, `###`)
- Leading newlines in messages (`\n` at start)
- Excessive TEST_STEP usage (every line vs major phases)
- Redundant messages (no info beyond function name)
- Missing context (resource names, counts, states, values)
- String formatting waste (expensive operations in DEBUG without `isEnabledFor` check)

### Strategic Logging to Add

Identify where logging is needed based on file type:

- **Test Files (`tests/`):** TEST_STEP, ASSERTION, INFO, DEBUG, WARNING, EXCEPTION
- **Deployment Code (`ocs_ci/deployment/`):** TEST_STEP, INFO, DEBUG, WARNING, EXCEPTION
- **Helper/Utility Files (`ocs_ci/helpers/`, `ocs_ci/utility/`):** INFO, DEBUG, WARNING, EXCEPTION
- **Resource Classes (`ocs_ci/ocs/resources/`):** INFO, DEBUG, WARNING, EXCEPTION
- **Framework Modules (`ocs_ci/framework/`):** CRITICAL, ERROR, WARNING, INFO, DEBUG (no TEST_STEP/ASSERTION - framework should be less chatty)

See `docs/logging_guide.md` "Usage by Code Type" section for detailed guidance on each file type.

### Common Patterns to Apply

- **Exception handling**: Always use `logger.exception()` in except blocks (includes traceback)
- **Loop/iteration logging**: INFO for start/completion, DEBUG for per-iteration details
- **TimeoutSampler**: Only log state changes (track last state, compare before logging)
- **Assertion placement**: Log BEFORE assert (won't execute if assert fails)
- **Structured logging**: Use `key=value` format for searchability
- **Performance-sensitive**: Wrap expensive DEBUG operations with `if logger.isEnabledFor(logging.DEBUG)`
- **Multi-line messages**: Use `\n` within message or multiple logger calls with consistent prefixes
- **Step numbering**: Reset with `reset_step_counts(__name__)` for independent iterations

See `docs/logging_guide.md` "Common Patterns" and "Special Topics" sections for detailed examples.

### Log Message Quality
- Use `key=value` format for structured logging
- Include context: operation, resource, values
- Never log: passwords, tokens, API keys, secrets
- For loops: INFO at start/end, DEBUG per-iteration
- For TimeoutSampler: only log state changes
- Be specific: what operation, which resource, relevant values
- Avoid generic: "Processing", "Failed", "Done", "Error"

### Available Log Levels

From highest to lowest severity (see guide for detailed usage):

- **CRITICAL** (50): System failures, framework crashes, unrecoverable cluster states
- **ERROR** (40): Test failures, exceptions, operation failures
- **WARNING** (30): Deprecations, retries, non-critical issues
- **TEST_STEP** (25): Major test workflow phases (tests/deployment only)
- **INFO** (20): General progress, operations, successful completions
- **ASSERTION** (15): Test validations and assertions (tests only)
- **DEBUG** (10): Detailed diagnostics, iteration details, internal flow
- **AI_DATA** (5): ML predictions, metrics (requires explicit enabling, rarely used)

## Usage

```bash
/update-logging tests/functional/test_example.py
```

or

```bash
/update-logging ocs_ci/helpers/helpers.py
```

## Maintenance

When logging guidelines evolve:

1. **Update `docs/logging_guide.md`** (authoritative source)
2. **Review this SKILL.md** - update if workflow/checklist changes
3. **Update `last_synced` date** in frontmatter above
4. **Test the skill** against the updated guidelines with sample files

**Sync Check**: If `docs/logging_guide.md` has commits after the `last_synced` date above, this skill may need review.

## Implementation

**CRITICAL**: Before making any changes, ALWAYS:
1. Read `docs/logging_guide.md` in full for the complete, authoritative guidelines
2. Apply all patterns, anti-patterns, and examples documented there
3. Use the guide as the definitive reference - the checklist above is a quick summary only

Now analyzing and updating the file: {{ file_path }}

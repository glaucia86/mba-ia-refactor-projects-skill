# Audit Report Template

Use these formats exactly enough to keep reports comparable. Write in the user's language when obvious from the request.

## Phase 1 Summary

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Project:       <name>
Language:      <language/version if known>
Framework:     <framework/version if known>
Dependencies:  <key dependencies>
Domain:        <short domain description>
Architecture:  <current architecture assessment>
Source files:  <N files analyzed | approx LOC>
Database:      <engine and tables/models>
Entry point:   <file and boot command>
Endpoints:     <count and key paths>
Validation:    <available commands/checks>
================================
```

## Phase 2 Audit Report

```markdown
# Architecture Audit Report - <project>

## Summary

- Stack: <language + framework>
- Files analyzed: <N>
- Approx LOC: <N>
- CRITICAL: <N>
- HIGH: <N>
- MEDIUM: <N>
- LOW: <N>
- Total findings: <N>

## Findings

### [CRITICAL] <finding title>

- File: `<path>:<start>-<end>`
- Description: <what is wrong>
- Evidence: <specific code signal>
- Impact: <why this matters>
- Recommendation: <target fix>

### [HIGH] ...
```

End Phase 2 with:

```text
Phase 2 complete. Proceed with MVC refactoring (Phase 3)? Reply with explicit confirmation before I modify files.
```

## Phase 3 Completion Report

```markdown
# Phase 3 Refactoring Complete - <project>

## New Project Structure

```text
<tree>
```

## Changes Applied

- <change>

## Validation

- [x] Application boots without errors: `<command>`
- [x] Endpoint checks passed: `<commands or examples>`
- [x] Anti-patterns addressed: <summary>

## Residual Risks

- <risk or "None known">
```

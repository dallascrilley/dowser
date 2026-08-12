# Security Policy

## Supported versions

Security fixes land on the default branch (`main`). There is no long-term support train for older tags yet.

## Reporting a vulnerability

Email **dallas@dallascrilley.com** with:

- A short description of the issue
- Steps to reproduce or a proof of concept
- Impact assessment if you have one
- Whether you plan a public write-up and on what timeline

Please do not open a public GitHub issue for unfixed security bugs.

I will acknowledge receipt when I can and work toward a fix or a clear decision. There is no formal bug bounty.

## Scope

In scope:

- The Dowser plugin hooks and skill search code in this repository
- Scripts that run with user privileges as part of install or garden checks
- Accidental exposure of secrets in tracked files

Out of scope:

- Skills that only document how to call third-party APIs (those systems have their own security process)
- Issues that require a compromised Claude Code host or malicious local config
- Dependency vulnerabilities with no realistic path through this plugin (still welcome as notes; prefer upstream reports)

## Secrets in skills

Example skills may show environment variable names (`OPENAI_API_KEY`, and similar). Never commit real credentials. Use placeholders only.

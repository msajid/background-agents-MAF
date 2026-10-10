---
title: Security Policy
description: Supported versions and private vulnerability reporting guidance
ms.date: 2026-10-10
ms.topic: security
---

## Supported versions

This demonstration currently supports the latest revision on the default branch. Older
commits and forks may not receive security updates.

## Report a vulnerability

Do not disclose suspected vulnerabilities in a public issue, discussion, or pull request.

Use GitHub private vulnerability reporting from the repository's **Security** tab. Include:

* A clear description of the issue and its impact
* Reproduction steps or a minimal proof of concept
* Affected files and dependency versions
* Suggested mitigations, if known

If private vulnerability reporting is unavailable, contact a repository maintainer
privately through the contact options on their GitHub profile.

Never include active API keys, access tokens, personal data, or unrelated third-party
information in a report. Maintainers will acknowledge valid reports and coordinate a fix
before public disclosure.

## Demonstration security notes

* Use Azure CLI or another supported token credential instead of storing an API key.
* Keep Foundry endpoints and model settings in the ignored `.env` file.
* Register only trusted child agents because delegated prompts and returned text cross
  agent boundaries.
* Treat child-agent output as untrusted when adapting this example to tools or private
  data.
* Review model usage and cost controls before running repeated demonstrations.

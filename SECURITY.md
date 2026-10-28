# Security Policy — RedLocalBlock 🛡️

## Supported Versions

Only the latest release versions receive active security updates, vulnerability patches, and dependency audits.

| Version | Supported          |
| :------ | :----------------- |
| >= 1.0  | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🔒 Responsible Vulnerability Disclosure

Security and user privacy are foundational pillars of **RedLocalBlock**. If you discover a security vulnerability or weakness within this codebase, we appreciate your help in disclosing it responsibly.

### How to Report a Vulnerability
- **Do NOT open public GitHub Issues or discussions** for potential security vulnerabilities.
- Please report vulnerabilities directly through the **[GitHub Private Vulnerability Reporting](https://github.com/dwn10/RedLocalBlock/security/advisories/new)** feature in the **Security** tab of this repository.
- Alternatively, you may contact the maintainer directly via GitHub profile: [@dwn10](https://github.com/dwn10).

### What to Include in Your Report
Please provide sufficient details to allow us to reproduce and investigate the issue quickly:
1. **Description:** A clear explanation of the potential vulnerability (e.g., unintended packet crafting, privilege escalation, unhandled exception resulting in network partition).
2. **Steps to Reproduce:** Exact reproduction steps, environment details (OS, Python version, Npcap version), and proof-of-concept (PoC) code if applicable.
3. **Impact:** Your assessment of the severity and affected components.

---

## ⏱️ Response Timelines & SLA
- **Initial Acknowledgment:** Within **48 hours** of receiving the report.
- **Triage & Status Update:** Within **5 business days** confirming the validity of the report.
- **Remediation & Patch:** A patch or mitigation will be prioritized based on severity (CVSS score) before any public advisory is published.

---

## ⚖️ Scope & Ethical Testing Guidelines
- This application operates under a **Strictly Defensiva & Local-First** policy.
- Automated testing should only be conducted on private, isolated networks owned or authorized by the tester.
- Testing that disrupts public infrastructure or third-party networks is strictly prohibited.

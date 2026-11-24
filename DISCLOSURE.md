# Coordinated disclosure

We audit third-party RL environments. Default: **coordinated, not surprise-public.**

1. **Notify the builder first.** Report the defect with evidence, not as a sales pitch.
2. **Give a fix window.** Default 90 days from first notification, or a shorter/longer window agreed in writing.
3. **Minimize public detail.** Public case studies describe method, impact, and numbers. They omit step-by-step exploit payloads for unpatched live environments until the window closes.
4. **Anonymize until permission.** A commercial builder's environment is named publicly only with written permission. Otherwise describe it generically.
5. **No client secrets.** Never publish client confidential data, customer names, or environment-specific thresholds.
6. **Open environments.** Still notify the maintainer and offer the patch; publish after the window or with consent.

If a defect is actively exploited in a live training run or poses a safety risk, we shorten the window and notify the affected lab in addition to the builder.

"""Synthetic credential shapes -- every value below is a dummy placeholder.

No real credential exists here: the GitHub token bodies are repeated filler and
the AWS key is the vendor's published documentation example. The gate must
redact them: output carries only a 4-char prefix plus file:line.
"""

GITHUB_PAT = "github_pat_11AAADUMMYDUMMYDUMMY_0000000000000000000000000000000000000000000"
GITHUB_TOKEN = "ghp_000000000000000000000000000000000000"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"

PRIVATE_KEY_PLACEHOLDER = """-----BEGIN RSA PRIVATE KEY-----
MIIBOgIBAAJBAKfakefakefakefakefakefakefakefakefakefakefakefakefake
-----END RSA PRIVATE KEY-----
"""

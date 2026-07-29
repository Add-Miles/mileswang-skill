from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/check_privacy_contract.py"
SPEC = importlib.util.spec_from_file_location("privacy_contract", MODULE_PATH)
assert SPEC and SPEC.loader
PRIVACY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PRIVACY
SPEC.loader.exec_module(PRIVACY)


class PrivacyIdentityTests(unittest.TestCase):
    def test_accepts_github_noreply_identity(self) -> None:
        address = "123+Public-Brand" + "@" + "users.noreply.github.com"
        PRIVACY.validate_identity_lines(["a" * 40 + "\x00" + address + "\x00" + address])

    def test_rejects_private_author_or_committer_identity(self) -> None:
        private = "private-contact" + "@" + "example.com"
        noreply = "123+Public-Brand" + "@" + "users.noreply.github.com"
        with self.assertRaises(PRIVACY.PrivacyContractError):
            PRIVACY.validate_identity_lines(
                ["b" * 40 + "\x00" + private + "\x00" + noreply]
            )
        with self.assertRaises(PRIVACY.PrivacyContractError):
            PRIVACY.validate_identity_lines(
                ["c" * 40 + "\x00" + noreply + "\x00" + private]
            )

    def test_rejects_private_annotated_tag_identity(self) -> None:
        private = "private-tagger" + "@" + "example.com"
        noreply = "123+Public-Brand" + "@" + "users.noreply.github.com"
        PRIVACY.validate_tagger_lines(
            ["tag\x00refs/tags/v1.0.0\x00<" + noreply + ">"]
        )
        with self.assertRaises(PRIVACY.PrivacyContractError):
            PRIVACY.validate_tagger_lines(
                ["tag\x00refs/tags/v1.0.0\x00<" + private + ">"]
            )
        PRIVACY.validate_tagger_lines(
            ["commit\x00refs/tags/lightweight\x00"]
        )

    def test_current_skill_contract_passes_without_history(self) -> None:
        checks = PRIVACY.validate_privacy_contract(check_history=False)
        self.assertTrue(any("privacy gate" in check for check in checks))


if __name__ == "__main__":
    unittest.main()

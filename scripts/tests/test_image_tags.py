import os
from pathlib import Path
import subprocess
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "image-tags.sh"
IMAGE = "ghcr.io/projetssd/ssdv2-webui"


class ImageTagsTest(unittest.TestCase):
    def test_ref_event_policy(self):
        cases = [
            ("push", "refs/heads/dev", "dev"),
            ("workflow_dispatch", "refs/heads/dev", "dev"),
            ("push", "refs/heads/main", "latest"),
            ("workflow_dispatch", "refs/heads/main", "latest"),
            ("push", "refs/tags/v1.2.3", "v1.2.3"),
            ("workflow_dispatch", "refs/heads/feature", None),
            ("push", "refs/heads/feature", None),
            ("pull_request", "refs/heads/dev", None),
            ("pull_request", "refs/heads/main", None),
            ("pull_request", "refs/pull/1/merge", None),
            ("push", "refs/tags/v1/bad", None),
        ]
        for event, ref, tag in cases:
            with self.subTest(event=event, ref=ref):
                result = subprocess.run(
                    ["bash", str(SCRIPT)], capture_output=True, text=True, check=True,
                    env={**os.environ, "IMAGE": IMAGE, "GITHUB_EVENT_NAME": event,
                         "GITHUB_REF": ref, "INPUT_TAG": "latest"},
                )
                self.assertEqual(result.stdout.strip(), f"{IMAGE}:{tag}" if tag else "")


if __name__ == "__main__":
    unittest.main()

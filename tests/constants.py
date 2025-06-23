"""Constants used in the tests."""

import os

CI_PROJECT_URL = os.environ["CI_PROJECT_URL"]
CI_COMMIT_REF_NAME = os.environ["CI_COMMIT_REF_NAME"]

print(
    f"CI_PROJECT_URL is {CI_PROJECT_URL}\nCI_COMMIT_REF_NAME is {CI_COMMIT_REF_NAME}\n"
)

#!/usr/bin/env python3
import glob
import re
import sys
from typing import IO, Mapping

import yaml

ALLOWED_ORGANIZATIONS = ["actions", "lumapps"]
SHORT_SHA1_PATTERN = re.compile(
    r"^(?P<actions_name>[A-Za-z0-9_.-]*\/[A-Za-z0-9_.-]*)@(?P<actions_version>[a-f0-9]{7})$"
)


# pylint: disable=too-many-nested-blocks,too-many-branches
def is_github_workflow_valid(file: IO, allowed_actions: Mapping[str, str]) -> bool:
    is_valid = True
    for environment in yaml.safe_load(file)["jobs"].values():
        for step in environment["steps"]:
            actions = step.get("uses", "")
            organization = actions.split("/")[0] if actions else None
            if organization and organization not in ALLOWED_ORGANIZATIONS:
                if not re.match(SHORT_SHA1_PATTERN, actions):
                    print(
                        f"ERROR {file.name}: Actions {actions} must follow "
                        f"'actions_name@short_sha1_tag  # github_tag' format."
                    )
                    is_valid = False
                else:
                    match = re.match(SHORT_SHA1_PATTERN, actions).groupdict()  # type: ignore
                    actions_name, actions_version = (
                        match["actions_name"],
                        match["actions_version"],
                    )
                    if actions_name not in allowed_actions.keys():
                        print(f"ERROR {file.name}: Actions {actions_name} forbidden")
                        is_valid = False
                    elif actions_version != allowed_actions[actions_name]:
                        print(
                            f"ERROR {file.name}: Version {actions_version} forbidden, "
                            f"instead you must use {allowed_actions[actions_name]}."
                        )
                        is_valid = False
                    else:
                        pass
    return is_valid


def load_allowed_actions() -> Mapping[str, str]:
    with open("./ALLOWED_ACTIONS.yaml", mode="r") as file:
        return yaml.safe_load(file)


def main() -> None:
    executions = []
    allowed_actions = load_allowed_actions()
    for extension in ("yaml", "yml"):
        for entry in glob.glob(f".github/workflows/**/*.{extension}", recursive=True):
            with open(entry, mode="r") as file:
                executions.append(is_github_workflow_valid(file, allowed_actions))

    sys.exit(not all(executions))


if __name__ == "__main__":
    main()

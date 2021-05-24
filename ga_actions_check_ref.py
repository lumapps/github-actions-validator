#!/usr/bin/env python3
import glob
import re
import sys
import yaml
from typing import IO, Mapping

SHORT_SHA1_PATTERN = re.compile(
    r"^(?P<actions_name>[A-Za-z0-9_.-]*\/[A-Za-z0-9_.-]*)@(?P<actions_version>[a-f0-9]{7})$"
)


def is_github_workflow_valid(file: IO, allowed_actions: Mapping[str, str]) -> bool:
    is_valid = True
    document = yaml.safe_load(file)
    for environment in document["jobs"].values():
        for step in environment["steps"]:
            actions = step.get("uses", "")
            if actions and not actions.startswith("actions/"):
                if not re.match(SHORT_SHA1_PATTERN, actions):
                    print(
                        f"ERROR: Actions {actions} must follow "
                        f"'actions_name@sohrt_sha1_tag  # github_tag' format."
                    )
                    is_valid = False
                else:
                    match = re.match(SHORT_SHA1_PATTERN, actions).groupdict()
                    actions_name = match["actions_name"]
                    actions_version = match["actions_version"]
                    if actions_name not in allowed_actions.keys():
                        print(f"ERROR: Actions {actions_name} forbidden")
                        is_valid = False
                    elif actions_version != allowed_actions[actions_name]:
                        print(
                            f"ERROR: Version {actions_version} forbidden, "
                            f"instead you must use {allowed_actions[actions_name]}."
                        )
                        is_valid = False
                    else:
                        pass
    return is_valid


def load_allowed_actions() -> Mapping[str, str]:
    with open("ALLOWED_ACTIONS.yaml", mode="r") as file:
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

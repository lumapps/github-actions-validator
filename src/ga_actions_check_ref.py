#!/usr/bin/env python3
import glob
import re
import sys
from dataclasses import dataclass, field
from typing import IO, List, Mapping

import yaml
from jsonpath_ng import parse

ALLOWED_ORGANIZATIONS = ["actions", "lumapps"]
GITHUB_ACTIONS_PATTERN = re.compile(
    r"^(?P<owner>[A-Za-z0-9_.-]+)\/(?P<repository>[A-Za-z0-9_.-]+)@(?P<reference>.*)$"
)

SHA1_PATTERN = re.compile(r"^[a-f0-9]{40}$")


@dataclass
class GithubActions:
    name: str = field(init=False)
    owner: str
    reference: str
    repository: str

    def __post_init__(self) -> None:
        self.name = f"{self.owner}/{self.repository}"


def find_gitub_actions_in_workflow(file: IO) -> List[GithubActions]:
    github_actions = []
    jsonpath_expr = parse("jobs.*.steps[*].uses")
    for actions in [match.value for match in jsonpath_expr.find(yaml.safe_load(file))]:
        match = re.match(GITHUB_ACTIONS_PATTERN, actions).groupdict()  # type: ignore
        github_actions.append(
            GithubActions(
                owner=match["owner"],
                repository=match["repository"],
                reference=match["reference"],
            )
        )

    return github_actions


def is_github_workflow_valid(file: IO, allowed_actions: Mapping[str, str]) -> bool:
    is_valid = True
    for github_actions in find_gitub_actions_in_workflow(file):
        if github_actions.owner in ALLOWED_ORGANIZATIONS:
            continue

        if f"{github_actions.name}" not in allowed_actions.keys():
            print(f"ERROR {file.name}: Actions {github_actions.name} forbidden")
            is_valid = False
        elif not re.match(SHA1_PATTERN, github_actions.reference):
            print(
                f"ERROR {file.name}: Actions {github_actions.name} must follow "
                f"'actions_name@sha1  # github_tag' format."
            )
            is_valid = False
        elif github_actions.reference != allowed_actions[github_actions.name]:
            print(
                f"ERROR {file.name}: Version {github_actions.reference} forbidden, "
                f"instead you must use {allowed_actions[github_actions.name]}."
            )
            is_valid = False

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

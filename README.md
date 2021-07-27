# GitHub actions checker

## About The Project
A Github Action to ensure all your organization's repositories are using approved Actions and their reference to keep your codebase safe.

### Github actions format
Each usage of github actions consists of an owner, a repository and a reference.
#### Bad practice
```yaml
- uses: cirrus-actions/rebase@1.5
```
#### Good practice
```yaml
- uses: cirrus-actions/rebase@c473b716e3fcde0c6bf67416e2c2882830ad40f6  # 1.5
```

#### Why
Git tags can be updated to point at a different SHA1 (and becoming malicious which can imply leaks/steals), whereas SHA1 is immutable.

### Safe github actions
Github actions (and their references) must be one of:
- `ALLOWED_ACTIONS.yaml` file
- starts with following patterns `(actions|lumapps)/.*` (no need to use SHA1 in this case)

### Installation

To configure the action simply add the following lines to your `.github/workflows/github-actions-validator.yml` workflow file:
```yaml
name: "CI: github-actions-validator"

on:
  pull_request:


jobs:
  github-actions-validator:
    name: Github-actions-validator
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: lumapps/github-actions-validator@v1
```

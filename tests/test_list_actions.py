from src.ga_actions_check_ref import find_gitub_actions_in_workflow


def test_list_valid_github_actions() -> None:
    with open("tests/sample_workflow.yaml", mode="r") as file:
        assert [
            github_actions.name
            for github_actions in find_gitub_actions_in_workflow(file)
        ] == [
            "actions/checkout",
            "lumapps/commit-message-validator",
            "cirrus-actions/rebase",
        ]

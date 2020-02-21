import json
import os.path
from unittest import mock

import pytest

import next_build


__here__ = os.path.dirname(__file__)

test_data = [
    {
        "package": "gimp",
        "expected_results": [
            # 5 existing builds -> 6
            {"dist": "fc32", "last": "gimp-2.10.14-4.fc32.1", "next": "gimp-2.10.14-6.fc32",},
            {"dist": "fc31", "last": "gimp-2.10.14-3.fc31", "next": "gimp-2.10.14-4.fc31",},
        ],
    },
]


def data_as_test_parameters(test_data):
    parameters = []

    for datum in test_data:
        blueprint = datum.copy()
        expected_results = blueprint.pop("expected_results")
        for expected in expected_results:
            parameters.append({**blueprint, **expected})

    return parameters


class TestNextBuild:
    @pytest.mark.parametrize("test_data", data_as_test_parameters(test_data))
    def test_main(self, test_data, capsys):
        with open(
            os.path.join(__here__, "koji-output", "list-builds", test_data["package"] + ".json"),
            "rb",
        ) as f:
            koji_list_builds_output = json.load(f)

        with mock.patch("next_build.koji") as mock_koji:
            mock_client = mock.MagicMock()
            mock_koji.ClientSession.return_value = mock_client
            mock_client.getPackageID.return_value = 1234
            mock_client.listBuilds.return_value = koji_list_builds_output

            next_build.main((test_data["package"], test_data["dist"]))

        mock_client.getPackageID.assert_called_once()
        mock_client.listBuilds.assert_called_once()

        expected_output = f"Last build: {test_data['last']}\n" f"Next build: {test_data['next']}\n"
        captured_output = capsys.readouterr()

        assert captured_output.out == expected_output

import os
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class TestSersolAPI(TestCase):
    """Tests for the Serials Solutions XML API proxy."""

    def test_missing_issn(self):
        """Test that calling the endpoint without an ISSN returns an error."""
        response = self.client.get(reverse("sersol_api"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {"error": "No ISSN parameter provided"})

    @patch("sersol_api.views.requests.get")
    def test_valid_issn_xml_processing(self, mock_get):
        """Test successful proxy fetching and XML-to-JSON namespace-stripped conversion."""
        # Read the real-world XML response from example.xml
        xml_path = os.path.join(os.path.dirname(__file__), "example.xml")
        with open(xml_path, "r", encoding="utf-8") as f:
            xml_response = f.read()

        mock_get.return_value.text = xml_response
        mock_get.return_value.status_code = 200

        issn = "2162-2574"
        response = self.client.get(reverse("sersol_api"), {"issn": issn})
        self.assertEqual(response.status_code, 200)

        # Verify requests.get was called with the correct url/parameters
        expected_url = (
            "http://ey7mr5fu9x.openurl.xml.serialssolutions.com/openurlxml?version=1.0&url_ver=Z39.88-2004&issn=%s"
            % issn
        )
        mock_get.assert_called_once_with(expected_url)

        # Verify JSON conversion and namespace prefix stripping
        data = response.json()
        self.assertEqual(data["version"], "1.0")
        self.assertIn("results", data)
        self.assertIn("result", data["results"])

        # Verify the citation source uses the full namespace URL (since it's not stripped)
        citation = data["results"]["result"]["citation"]
        self.assertEqual(
            citation["http://purl.org/dc/elements/1.1/:source"],
            "ARTMargins (Cambridge, Mass.)",
        )

        # Verify the ISSN list/dict mapping
        issns = citation["issn"]
        self.assertIsInstance(issns, list)
        self.assertEqual(len(issns), 2)
        self.assertEqual(issns[0]["@type"], "print")
        self.assertEqual(issns[0]["#text"], "2162-2574")
        self.assertEqual(issns[1]["@type"], "electronic")
        self.assertEqual(issns[1]["#text"], "2162-2582")

        # Verify holding data exists and uses stripped namespaces
        link_groups = data["results"]["result"]["linkGroups"]["linkGroup"]
        self.assertIsInstance(link_groups, list)
        self.assertEqual(len(link_groups), 2)
        self.assertEqual(link_groups[0]["holdingData"]["providerName"], "JSTOR")

        # Verify CORS headers
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "https://library.cca.edu"
        )

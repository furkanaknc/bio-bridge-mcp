import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from servers import register_all_tools
from workflows.geo_sample_analysis import analyze_sample
from shared.env import load_project_env


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator


class RegistrationTests(unittest.TestCase):
    def test_load_project_env_is_safe(self):
        load_project_env()

    def test_registers_all_tools(self):
        mcp = FakeMCP()
        register_all_tools(mcp)
        self.assertEqual(len(mcp.tools), 30)

    def test_search_pubmed_wrapper_formats_results(self):
        mcp = FakeMCP()
        register_all_tools(mcp)
        fake_results = [
            {
                "id": "123",
                "title": "Example paper",
                "authors": ["A. One", "B. Two", "C. Three", "D. Four"],
                "journal": "Nature",
                "pub_date": "2025",
            }
        ]
        fake_client = type("FakeNcbiClient", (), {"search_pubmed": lambda self, query: fake_results})()

        with patch("servers.ncbi.literature.get_ncbi_client", return_value=fake_client):
            output = mcp.tools["search_pubmed_papers"]("crispr")

        self.assertIn("PMID:123", output)
        self.assertIn("Authors: A. One, B. Two, C. Three...", output)

    def test_workflow_geo_sample_analysis_extracts_gsm_id(self):
        fake_payload = {
            "accession": "GSM12345",
            "title": "Sample title",
            "organism": "Homo sapiens",
            "condition": "treated",
            "dosage": "5 uM",
            "summary": "Sample summary",
        }
        fake_client = type(
            "FakeNcbiClient",
            (),
            {"fetch_geo_details": lambda self, accession: fake_payload},
        )()

        with patch("workflows.geo_sample_analysis.get_ncbi_client", return_value=fake_client):
            output = analyze_sample("please inspect gsm12345")

        self.assertIn("### Analysis for GSM12345", output)
        self.assertIn("Dosage Detected", output)

    def test_convert_structure_file_creates_obj(self):
        mcp = FakeMCP()
        register_all_tools(mcp)
        pdb_text = "\n".join(
            [
                "TITLE     HEMOGLOBIN TEST",
                "ATOM      1  N   GLY A   1      11.104  13.207   9.447  1.00 20.00           N",
                "ATOM      2  CA  GLY A   1      12.560  13.207   9.447  1.00 20.00           C",
                "HETATM    3  FE  HEM A 201      13.000  14.000  10.000  1.00 20.00          FE",
                "END",
            ]
        )

        with TemporaryDirectory() as temp_dir:
            pdb_path = Path(temp_dir) / "sample.pdb"
            pdb_path.write_text(pdb_text, encoding="utf-8")
            result = mcp.tools["convert_structure_to_obj"](str(pdb_path))

        self.assertEqual(result["protein"], "HEMOGLOBIN TEST")
        self.assertTrue(result["artifacts"]["obj"].endswith(".obj"))
        self.assertEqual(result["chains"], 1)
        self.assertEqual(result["atoms"], 3)
        self.assertGreater(result["mesh"]["faces"], 0)


if __name__ == "__main__":
    unittest.main()

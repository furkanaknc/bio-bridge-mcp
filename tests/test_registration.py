import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp import Client, StdioServerParameters
from prompts import register_prompts
from server import mcp as real_mcp
from servers import register_all_tools
from workflows.geo_sample_analysis import analyze_sample
from shared.env import load_project_env


class FakeMCP:
    def __init__(self):
        self.tools = {}
        self.tool_metadata = {}
        self.prompts = {}

    def tool(self, **metadata):
        def decorator(func):
            self.tools[func.__name__] = func
            self.tool_metadata[func.__name__] = metadata
            return func

        return decorator

    def prompt(self, **metadata):
        def decorator(func):
            self.prompts[func.__name__] = func
            return func

        return decorator


class RegistrationTests(unittest.TestCase):
    def test_load_project_env_is_safe(self):
        load_project_env()

    def test_registers_all_tools(self):
        mcp = FakeMCP()
        register_all_tools(mcp)
        self.assertEqual(len(mcp.tools), 27)
        self.assertTrue(all(item.get("title") for item in mcp.tool_metadata.values()))
        self.assertTrue(all(item.get("annotations") for item in mcp.tool_metadata.values()))

    def test_registers_useful_prompts(self):
        mcp = FakeMCP()
        register_prompts(mcp)
        self.assertEqual(len(mcp.prompts), 3)
        prompt = mcp.prompts["investigate_protein_structure"]("P04637")
        self.assertIn("pdb_search_by_uniprot", prompt)
        self.assertIn("P04637", prompt)

    def test_v2_server_publishes_metadata_and_output_schemas(self):
        async def inspect_server():
            async with Client(real_mcp) as client:
                tools = (await client.list_tools()).tools
                prompts = (await client.list_prompts()).prompts
                return tools, prompts

        tools, prompts = asyncio.run(inspect_server())
        self.assertEqual(len(tools), 27)
        self.assertEqual(len(prompts), 3)
        self.assertTrue(all(tool.title for tool in tools))
        self.assertTrue(all(tool.annotations for tool in tools))
        self.assertTrue(all(tool.output_schema for tool in tools))

    def test_server_runs_over_stdio(self):
        async def inspect_stdio_server():
            params = StdioServerParameters(
                command=sys.executable,
                args=["src/server.py"],
                cwd=ROOT,
            )
            async with Client(params, read_timeout_seconds=20) as client:
                tools = (await client.list_tools()).tools
                prompts = (await client.list_prompts()).prompts
                return tools, prompts

        tools, prompts = asyncio.run(inspect_stdio_server())
        self.assertEqual(len(tools), 27)
        self.assertEqual(len(prompts), 3)

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


if __name__ == "__main__":
    unittest.main()

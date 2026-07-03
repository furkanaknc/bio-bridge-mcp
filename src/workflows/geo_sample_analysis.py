import re

from shared.clients import get_ncbi_client


def analyze_sample(input_text: str) -> str:
    ncbi_client = get_ncbi_client()
    if not ncbi_client:
        return "Error: NCBI Client is not initialized."

    match = re.search(r"(GSM\d+)", input_text, re.IGNORECASE)
    if not match:
        return (
            f"Error: No valid GSM ID found in input '{input_text}'. "
            "Please provide a valid GEO Sample ID (e.g., GSM12345)."
        )

    geo_id = match.group(1).upper()

    try:
        data = ncbi_client.fetch_geo_details(geo_id)
        if "error" in data:
            return f"Error fetching data for {geo_id}: {data['error']}"

        output = [f"### Analysis for {data['accession']}"]
        output.append(f"**Title:** {data['title']}")
        output.append(f"**Organism:** {data['organism']}")
        output.append("---")
        output.append(f"**Condition:** {data['condition']}")

        if data["dosage"]:
            output.append(f"**Dosage Detected:** {data['dosage']}")
        else:
            output.append("**Dosage:** Not found / Not Applicable")

        output.append("---")
        output.append(f"**Summary:**\n{data['summary']}")
        return "\n".join(output)
    except Exception as exc:
        return f"An unexpected error occurred: {exc}"

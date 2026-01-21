from mcp.server.fastmcp import FastMCP

from parsing_logic import get_geo_sample_metadata

mcp = FastMCP("Bio-Bridge")

@mcp.tool()
def analyze_sample(geo_id: str) -> str:
    if not geo_id.startswith("GSM"):
        return f"Error: Invalid GEO ID format '{geo_id}'. Expected ID starting with 'GSM'."

    try:
        data = get_geo_sample_metadata(geo_id)
        
        if "error" in data:
            return f"Error fetching data for {geo_id}: {data['error']}"
            
        output = []
        output.append(f"### Analysis for {data['accession']}")
        output.append(f"**Title:** {data['title']}")
        output.append(f"**Organism:** {data['organism']}")
        output.append("---")
        output.append(f"**Condition:** {data['condition']}")
        
        if data['dosage']:
            output.append(f"**Dosage Detected:** {data['dosage']}")
        else:
            output.append("**Dosage:** Not found / Not Applicable")
            
        output.append("---")
        output.append(f"**Summary:**\n{data['summary']}")
        
        return "\n".join(output)

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    mcp.run()

import re
import os
import requests
from Bio import Entrez

def search(query: str, limit: int = 5) -> list:
    try:
        if not Entrez.email:
             Entrez.email = os.getenv("NCBI_EMAIL")
        
        handle = Entrez.esearch(db="gds", term=query, retmax=limit)
        results = Entrez.read(handle)
        handle.close()
        
        id_list = results.get("IdList", [])
        if not id_list:
            return []
            
        summary_handle = Entrez.esummary(db="gds", id=",".join(id_list))
        summaries = Entrez.read(summary_handle)
        summary_handle.close()
        
        output = []
        for item in summaries:
            output.append({
                "id": item.get("Accession", item.get("Id")),
                "title": item.get("Title", "Unknown Title"),
                "summary": item.get("pdat", item.get("summary", "No summary available")) 
            })
        return output
    except Exception as e:
        return [{"error": str(e)}]

def fetch_metadata(geo_accession: str) -> dict:
    try:
        if not Entrez.email:
            Entrez.email = os.getenv("NCBI_EMAIL")
            if not Entrez.email:
                return {"error": "Configuration Error: NCBI_EMAIL is not set."}

        clean_id = geo_accession.strip().replace("'", "").replace('"', "").upper()

        url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={clean_id}&targ=self&form=text&view=full"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        full_text_data = response.text

        if not full_text_data or "could not be found" in full_text_data.lower():
            return {"error": f"No record found for accession {clean_id}"}

        lines = full_text_data.split('\n')
        
        title = "Unknown"
        organism = "Unknown"
        source_name = ""
        characteristics = []
        growth_protocol = ""
        treatment_protocol = ""
        description = []
        
        for line in lines:
            if line.startswith('!Sample_title'):
                title = line.split('=', 1)[1].strip() if '=' in line else "Unknown"
            elif line.startswith('!Sample_organism'):
                organism = line.split('=', 1)[1].strip() if '=' in line else "Unknown"
            elif line.startswith('!Sample_source_name'):
                source_name = line.split('=', 1)[1].strip() if '=' in line else ""
            elif line.startswith('!Sample_characteristics'):
                char_value = line.split('=', 1)[1].strip() if '=' in line else ""
                characteristics.append(char_value)
            elif line.startswith('!Sample_growth_protocol'):
                growth_protocol = line.split('=', 1)[1].strip() if '=' in line else ""
            elif line.startswith('!Sample_treatment_protocol'):
                treatment_protocol = line.split('=', 1)[1].strip() if '=' in line else ""
            elif line.startswith('!Sample_description'):
                desc_value = line.split('=', 1)[1].strip() if '=' in line else ""
                if desc_value:
                    description.append(desc_value)

        all_text = full_text_data.lower()
        
        dosage_pattern = r'(\d+(\.\d+)?\s?((m|u|µ|n|p)g/(kg|ml)|(m|u|µ|n|p)M|IU/ml|%))'
        dosage = None
        dosage_match = re.search(dosage_pattern, " ".join(characteristics), re.IGNORECASE)
        if dosage_match:
            dosage = dosage_match.group(0)
        else:
            dosage_match = re.search(dosage_pattern, growth_protocol + treatment_protocol, re.IGNORECASE)
            if dosage_match:
                dosage = dosage_match.group(0)

        condition = "Unknown"
        control_keywords = ['control', 'placebo', 'untreated', 'vehicle', 'mock', 
                            'healthy', 'baseline', 'pbs', 'saline', 'wt', 'naive', 'normal']
        treated_keywords = ['treated', 'drug', 'dose', 'administered', 'exposure', 
                            'inhibitor', 'stimulation', 'compound', 'injected', 
                            'treatment', 'infected', 'patient', 'disease', 'estradiol', 'e2']

        control_score = sum(1 for k in control_keywords if k in all_text)
        treated_score = sum(1 for k in treated_keywords if k in all_text)

        if dosage and not dosage.startswith("0"):
            condition = "Treated"
        elif any("drug treatment" in char.lower() for char in characteristics):
            condition = "Treated"
        else:
            if 'pbs' in all_text or 'vehicle' in all_text:
                if treated_score > control_score:
                    condition = "Treated (PBS/Vehicle mentioned)"
                else:
                    condition = "Control (Vehicle/PBS)"
            elif treated_score > 0:
                condition = "Treated"
            elif control_score > treated_score:
                condition = "Control"

        summary_parts = []
        if source_name: summary_parts.append(f"Source: {source_name}")
        if characteristics:
            summary_parts.append("Characteristics:")
            for char in characteristics: summary_parts.append(f"  - {char}")
        if treatment_protocol: summary_parts.append(f"Treatment Protocol: {treatment_protocol}")
        if growth_protocol: summary_parts.append(f"Growth Protocol: {growth_protocol}")
        if description: summary_parts.append(f"Description: {' '.join(description)}")

        return {
            "accession": clean_id,
            "title": title,
            "organism": organism,
            "condition": condition,
            "dosage": dosage,
            "summary": "\n".join(summary_parts)
        }

    except Exception as e:
        return {"error": str(e)}

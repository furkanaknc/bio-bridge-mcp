import requests
import statistics

RCSB_DATA_API = "https://data.rcsb.org/rest/v1/core/entry/"
RCSB_GRAPHQL_API = "https://data.rcsb.org/graphql"

def get_pdb_summary(pdb_id: str) -> dict:
    pdb_id = pdb_id.upper()
    url = f"{RCSB_DATA_API}{pdb_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": f"Could not fetch data for {pdb_id}. Status: {response.status_code}"}
    
    data = response.json()
    
    title = data.get("struct", {}).get("title", "Unknown Title")
    classification = data.get("struct_keywords", {}).get("pdbx_keywords", "Unknown")
    
    mutations = []
    has_mutation_flag = False
 
    gql_query = """
    query($pdbId: String!) {
      entry(entry_id: $pdbId) {
        polymer_entities {
          rcsb_polymer_entity_container_identifiers {
            entity_id
          }
          rcsb_entity_source_organism {
            ncbi_scientific_name
          }
          rcsb_polymer_entity_annotation {
            type
            description
            annotation_id
          }
        }
      }
    }
    """
    
    gql_resp = requests.post(RCSB_GRAPHQL_API, json={"query": gql_query, "variables": {"pdbId": pdb_id}})
    
    gql_data = {}
    if gql_resp.status_code == 200:
        json_resp = gql_resp.json()
        if not json_resp or "data" not in json_resp or not json_resp["data"]:
             print(f"DEBUG: GraphQL Error in Summary: {json_resp.get('errors')}")
             gql_data = {}
        else:
             gql_data = json_resp["data"].get("entry") or {}

    polymer_entities = gql_data.get("polymer_entities", [])
            
    for entity in polymer_entities:
        annotations = entity.get("rcsb_polymer_entity_annotation") or []
        mutation_anns = [a for a in annotations if a.get("type") == "mutation"]
        
        entity_id = entity.get("rcsb_polymer_entity_container_identifiers", {}).get("entity_id")
        
        count = len(mutation_anns)
        
        if mutation_anns:
            has_mutation_flag = True
            details = [a.get("description") for a in mutation_anns]
            mutations.append({
                "entity_id": entity_id,
                "official_count": count,
                "details": details
            })

    return {
        "pdb_id": pdb_id,
        "title": title,
        "classification": classification,
        "has_mutations": has_mutation_flag,
        "mutation_details": mutations,
        "note": "RCSB summary might show 0 mutations while details show otherwise. Check 'mutation_details'."
    }

def get_pdb_ligands(pdb_id: str) -> list:

    pdb_id = pdb_id.upper()
    
    gql_query = """
    query($pdbId: String!) {
      entry(entry_id: $pdbId) {
        nonpolymer_entities {
          rcsb_nonpolymer_entity_container_identifiers {
            entity_id
            auth_asym_ids
          }
          pdbx_entity_nonpoly {
            comp_id
            name
            rcsb_prd_id
          }
          rcsb_nonpolymer_entity {
            formula_weight
          }
          rcsb_nonpolymer_entity_annotation {
             type
             description
          }
        }
      }
    }
    """
    
    response = requests.post(RCSB_GRAPHQL_API, json={"query": gql_query, "variables": {"pdbId": pdb_id}})
    if response.status_code != 200:
        return []

    json_resp = response.json()
    if "data" not in json_resp or json_resp["data"] is None:
        print(f"DEBUG: GraphQL Error in Ligands: {json_resp.get('errors')}")
        return []
        
    data = json_resp["data"].get("entry")
    if not data:
        print("DEBUG: GraphQL entry is null.")
        return []
        
    non_polymers = data.get("nonpolymer_entities") or []
    results = []
    
    for np in non_polymers:
        info = np.get("pdbx_entity_nonpoly", {})
        comp_id = info.get("comp_id")
        name = info.get("name")
        
        if comp_id == "HOH":
            continue
            
        weight = np.get("rcsb_nonpolymer_entity", {}).get("formula_weight", 0) or 0
        try:
             weight = float(weight)
        except (ValueError, TypeError):
             weight = 0
           
        if weight < 20: 
             weight *= 1000
             
        if weight < 50: 
            continue
            
        annotations = np.get("rcsb_nonpolymer_entity_annotation") or []
        binding_data = [a.get("description") for a in annotations if "binding" in (a.get("type") or "").lower()]
        
        identifiers = np.get("rcsb_nonpolymer_entity_container_identifiers", {})
        asym_ids = identifiers.get("auth_asym_ids", [])
        
        results.append({
            "ligand_id": comp_id,
            "name": name,
            "entity_id": identifiers.get("entity_id"),
            "chains": asym_ids,
            "binding_info": binding_data
        })
        
    return results

def get_binding_pocket(pdb_id: str, ligand_id: str = None) -> dict:
    pdb_id = pdb_id.upper()
    
    if not ligand_id:
        ligands = get_pdb_ligands(pdb_id)
        if not ligands:
            return {"error": "No significant ligands found to define a pocket."}
        target_ligand = ligands[0]
        ligand_id = target_ligand["ligand_id"]
    
    ligands = get_pdb_ligands(pdb_id)
    target_ligand = next((l for l in ligands if l["ligand_id"] == ligand_id), None)
    
    if not target_ligand:
        return {"error": f"Ligand {ligand_id} not found in {pdb_id}."}
        
    chains = target_ligand["chains"]
    if not chains:
         return {"error": f"No chains found for ligand {ligand_id}."}

    results = []

    for target_chain in chains:
        
        map_query = """
        query($pdbId: String!) {
          entry(entry_id: $pdbId) {
            nonpolymer_entities {
              nonpolymer_entity_instances {
                rcsb_nonpolymer_entity_instance_container_identifiers {
                  auth_asym_id
                  asym_id
                }
              }
            }
          }
        }
        """
        
        pass

    map_query = """
    query($pdbId: String!) {
      entry(entry_id: $pdbId) {
        nonpolymer_entities {
          nonpolymer_entity_instances {
            rcsb_nonpolymer_entity_instance_container_identifiers {
              auth_asym_id
              asym_id
            }
          }
        }
      }
    }
    """
    resp = requests.post(RCSB_GRAPHQL_API, json={"query": map_query, "variables": {"pdbId": pdb_id}})
    
    mapping_data = {} 
    try:
        data = resp.json()
        if data and "data" in data and data["data"]:
            entities = data["data"]["entry"]["nonpolymer_entities"] or []
            for entity in entities:
                instances = entity.get("nonpolymer_entity_instances") or []
                for inst in instances:
                    ids = inst.get("rcsb_nonpolymer_entity_instance_container_identifiers", {})
                    auth = ids.get("auth_asym_id")
                    label = ids.get("asym_id")
                    if auth and label:
                        mapping_data[auth] = label
    except Exception:
        pass 
        
    pockets = []
    
    for target_chain in chains:
        label_asym_id = mapping_data.get(target_chain)
        if not label_asym_id:
            pockets.append(f"Could not map chain {target_chain} to internal ID.")
            continue
            
        ms_url = f"https://models.rcsb.org/v1/{pdb_id.lower()}/atoms?label_asym_id={label_asym_id}"
        ms_resp = requests.get(ms_url, headers={"Accept": "application/json"})
        
        if ms_resp.status_code != 200:
             pockets.append(f"Chain {target_chain}: Failed to fetch coords ({ms_resp.status_code})")
             continue
             
        lines = ms_resp.text.splitlines()
        parsing_atoms = False
        headers = []
        x_idx, y_idx, z_idx = -1, -1, -1
        xs, ys, zs = [], [], []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                if parsing_atoms: break
                continue
            if line.startswith("loop_"): continue
            if line.startswith("_atom_site."):
                headers.append(line.split(".")[1])
                if "Cartn_x" in line: x_idx = len(headers) - 1
                if "Cartn_y" in line: y_idx = len(headers) - 1
                if "Cartn_z" in line: z_idx = len(headers) - 1
                parsing_atoms = True
                continue
            if parsing_atoms:
                parts = line.split()
                if len(parts) < max(x_idx, y_idx, z_idx): continue
                try:
                    if x_idx != -1: xs.append(float(parts[x_idx]))
                    if y_idx != -1: ys.append(float(parts[y_idx]))
                    if z_idx != -1: zs.append(float(parts[z_idx]))
                except ValueError: continue

        if xs:
            avg_x = statistics.mean(xs)
            avg_y = statistics.mean(ys)
            avg_z = statistics.mean(zs)
            pockets.append({
                "chain_id": target_chain,
                "center": {"x": round(avg_x, 3), "y": round(avg_y, 3), "z": round(avg_z, 3)}
            })
        else:
            pockets.append(f"Chain {target_chain}: No atoms found.")

    return {
        "ligand_id": ligand_id,
        "pockets": pockets,
        "description": f"Geometric centers for {len(pockets)} instances of {ligand_id}."
    }

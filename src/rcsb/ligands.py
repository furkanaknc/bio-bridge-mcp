import statistics
import requests
from .utils import post_graphql, parse_mmcif_atom_site_coords
from .constants import COMMON_JUNK, RCSB_MODELSERVER, TIMEOUT

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
        }
      }
    }
    """

    try:
        json_resp = post_graphql(gql_query, {"pdbId": pdb_id})
    except Exception:
        return []

    data = json_resp.get("entry")
    if not data:
        return []

    non_polymers = data.get("nonpolymer_entities") or []
    results = []

    for np in non_polymers:
        info = np.get("pdbx_entity_nonpoly") or {}
        comp_id = info.get("comp_id")
        name = info.get("name")

        if not comp_id:
            continue

        if comp_id in COMMON_JUNK:
            continue

        weight = (np.get("rcsb_nonpolymer_entity") or {}).get("formula_weight")
        try:
            weight = float(weight) if weight is not None else None
        except (ValueError, TypeError):
            weight = None

        identifiers = np.get("rcsb_nonpolymer_entity_container_identifiers") or {}
        asym_ids = identifiers.get("auth_asym_ids") or []

        results.append({
            "ligand_id": comp_id,
            "name": name,
            "entity_id": identifiers.get("entity_id"),
            "chains": asym_ids,
            "formula_weight": weight,
        })

    return results

def get_binding_pocket(pdb_id: str, ligand_id: str = None) -> dict:
    pdb_id = pdb_id.upper()

    ligands = get_pdb_ligands(pdb_id)
    if not ligands:
        return {"error": "No significant ligands found."}

    if not ligand_id:
        ligand_id = ligands[0]["ligand_id"]

    target_ligand = next((l for l in ligands if l["ligand_id"] == ligand_id), None)
    if not target_ligand:
        return {"error": f"Ligand {ligand_id} not found in {pdb_id}."}

    chains = target_ligand.get("chains") or []
    if not chains:
        return {"error": f"No auth_asym_id instances found for ligand {ligand_id}."}

    pockets = []

    for auth_asym_id in chains:
        params = {
            "label_comp_id": ligand_id,
            "auth_asym_id": auth_asym_id,
            "encoding": "cif",  # text mmCIF
        }
        ms_url = f"{RCSB_MODELSERVER}/{pdb_id}/atoms"

        try:
            ms_resp = requests.get(ms_url, params=params, timeout=TIMEOUT)
            ms_resp.raise_for_status()
        except Exception as e:
            pockets.append(f"Chain {auth_asym_id}: ModelServer request failed ({str(e)})")
            continue

        coords = parse_mmcif_atom_site_coords(ms_resp.text)
        if not coords:
            pockets.append(f"Chain {auth_asym_id}: No ligand atoms found (check ligand_id/auth_asym_id).")
            continue

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        zs = [c[2] for c in coords]

        pockets.append({
            "chain_id": auth_asym_id,
            "atom_count": len(coords),
            "center": {
                "x": round(statistics.mean(xs), 3),
                "y": round(statistics.mean(ys), 3),
                "z": round(statistics.mean(zs), 3),
            }
        })

    return {
        "ligand_id": ligand_id,
        "pockets": pockets,
        "description": f"Geometric centers (centroids) of ligand atoms for each auth_asym_id instance of {ligand_id}.",
        "note": "This is a practical binding-site center proxy (ligand centroid), not a computed pocket volume/mesh."
    }

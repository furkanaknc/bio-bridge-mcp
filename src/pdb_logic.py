import requests
import statistics
import shlex

RCSB_DATA_API = "https://data.rcsb.org/rest/v1/core/entry/"
RCSB_GRAPHQL_API = "https://data.rcsb.org/graphql"
RCSB_MODELSERVER = "https://models.rcsb.org/v1"

TIMEOUT = 20

# Yaygın çözücü/iyon/katkılar (default filtre)
COMMON_JUNK = {
    "HOH", "DOD",
    "NA", "K", "CL", "BR", "I",
    "CA", "MG", "ZN", "MN", "CU", "NI", "CO", "FE",
    "SO4", "PO4", "NO3",
    "GOL", "EDO", "MPD", "DMS", "IPA",
    # PEG kodları entry’ye göre değişebilir; bunlar sık görülen bazıları
    "PEG", "PGE", "PE4", "PE5", "PE6", "PE7", "PE8",
}

def _get_json(url: str) -> dict:
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def _post_graphql(query: str, variables: dict) -> dict:
    r = requests.post(RCSB_GRAPHQL_API, json={"query": query, "variables": variables}, timeout=TIMEOUT)
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload.get("data") or {}

def _parse_mmcif_atom_site_coords(cif_text: str):
    """
    Minimal mmCIF parser for a loop_ containing _atom_site.Cartn_{x,y,z}.
    ModelServer çıktısı genelde temiz ve bu parser yeterli oluyor.
    """
    lines = [ln.strip() for ln in cif_text.splitlines() if ln.strip() and not ln.strip().startswith("#")]

    in_atom_loop = False
    headers = []
    x_idx = y_idx = z_idx = None
    coords = []

    for ln in lines:
        if ln == "loop_":
            # yeni loop başlangıcı
            in_atom_loop = False
            headers = []
            x_idx = y_idx = z_idx = None
            continue

        if ln.startswith("_atom_site."):
            in_atom_loop = True
            headers.append(ln)  # full tag
            if ln.endswith(".Cartn_x"):
                x_idx = len(headers) - 1
            elif ln.endswith(".Cartn_y"):
                y_idx = len(headers) - 1
            elif ln.endswith(".Cartn_z"):
                z_idx = len(headers) - 1
            continue

        if in_atom_loop and headers and not ln.startswith("_"):
            # data row
            if x_idx is None or y_idx is None or z_idx is None:
                continue
            parts = shlex.split(ln)  # quote-safe
            if len(parts) <= max(x_idx, y_idx, z_idx):
                continue
            try:
                coords.append((float(parts[x_idx]), float(parts[y_idx]), float(parts[z_idx])))
            except ValueError:
                continue

    return coords

def get_pdb_summary(pdb_id: str) -> dict:
    pdb_id = pdb_id.upper()
    try:
        data = _get_json(f"{RCSB_DATA_API}{pdb_id}")
    except Exception as e:
        return {"error": f"Could not fetch data for {pdb_id}: {str(e)}"}

    title = data.get("struct", {}).get("title", "Unknown Title")
    classification = data.get("struct_keywords", {}).get("pdbx_keywords", "Unknown")

    # Minimum bozmayarak: senin annotation yaklaşımın duruyor,
    # ama bu her entry’de güvenilir olmayabilir (bunu not’ta belirtiyorum).
    gql_query = """
    query($pdbId: String!) {
      entry(entry_id: $pdbId) {
        polymer_entities {
          rcsb_polymer_entity_container_identifiers { entity_id }
          rcsb_polymer_entity_annotation { type description annotation_id }
        }
      }
    }
    """
    mutations = []
    has_mutation_flag = False

    try:
        gql_data = _post_graphql(gql_query, {"pdbId": pdb_id})
        polymer_entities = (gql_data.get("entry") or {}).get("polymer_entities", []) or []
        for entity in polymer_entities:
            annotations = entity.get("rcsb_polymer_entity_annotation") or []
            mutation_anns = [a for a in annotations if (a.get("type") or "").lower() == "mutation"]
            entity_id = (entity.get("rcsb_polymer_entity_container_identifiers") or {}).get("entity_id")
            if mutation_anns:
                has_mutation_flag = True
                mutations.append({
                    "entity_id": entity_id,
                    "count": len(mutation_anns),
                    "details": [a.get("description") for a in mutation_anns if a.get("description")]
                })
    except Exception as e:
        # Summary yine de dönsün
        return {
            "pdb_id": pdb_id,
            "title": title,
            "classification": classification,
            "has_mutations": None,
            "mutation_details": [],
            "warning": f"GraphQL mutation query failed: {str(e)}",
        }

    return {
        "pdb_id": pdb_id,
        "title": title,
        "classification": classification,
        "has_mutations": has_mutation_flag,
        "mutation_details": mutations,
        "note": "Mutation annotations are not always complete; if needed, switch to rcsb_mutation_count-based check.",
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
        }
      }
    }
    """

    try:
        json_resp = _post_graphql(gql_query, {"pdbId": pdb_id})
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

        # daha geniş junk filtre
        if comp_id in COMMON_JUNK:
            continue

        # weight: sadece yardımcı sinyal olsun, hack yok
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
            "chains": asym_ids,  # auth_asym_id listesi
            "formula_weight": weight,
        })

    return results

def get_binding_pocket(pdb_id: str, ligand_id: str = None) -> dict:
    """
    FIXED:
    - Zincirin tüm atomlarını çekmek yerine ligand atomlarını filtreleyip centroid alır.
    - Mapping kaldırıldı; auth_asym_id ile direkt filtreler.
    """
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
        # IMPORTANT: ligand filter + auth_asym_id filter
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

        coords = _parse_mmcif_atom_site_coords(ms_resp.text)
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

# quick test
if __name__ == "__main__":
    pdb = "1M17"
    print(get_pdb_summary(pdb))
    print(get_pdb_ligands(pdb)[:5])
    # ligand_id vermeden ilk ligandla dener
    print(get_binding_pocket(pdb))

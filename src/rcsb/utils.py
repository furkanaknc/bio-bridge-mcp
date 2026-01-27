import requests
import shlex
from .constants import TIMEOUT, RCSB_GRAPHQL_API

def get_json(url: str) -> dict:
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def post_graphql(query: str, variables: dict) -> dict:
    r = requests.post(RCSB_GRAPHQL_API, json={"query": query, "variables": variables}, timeout=TIMEOUT)
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload.get("data") or {}

def parse_mmcif_atom_site_coords(cif_text: str):
    lines = [ln.strip() for ln in cif_text.splitlines() if ln.strip() and not ln.strip().startswith("#")]

    in_atom_loop = False
    headers = []
    x_idx = y_idx = z_idx = None
    coords = []

    for ln in lines:
        if ln == "loop_":
            in_atom_loop = False
            headers = []
            x_idx = y_idx = z_idx = None
            continue

        if ln.startswith("_atom_site."):
            in_atom_loop = True
            headers.append(ln) 
            if ln.endswith(".Cartn_x"):
                x_idx = len(headers) - 1
            elif ln.endswith(".Cartn_y"):
                y_idx = len(headers) - 1
            elif ln.endswith(".Cartn_z"):
                z_idx = len(headers) - 1
            continue

        if in_atom_loop and headers and not ln.startswith("_"):
            if x_idx is None or y_idx is None or z_idx is None:
                continue
            parts = shlex.split(ln) 
            if len(parts) <= max(x_idx, y_idx, z_idx):
                continue
            try:
                coords.append((float(parts[x_idx]), float(parts[y_idx]), float(parts[z_idx])))
            except ValueError:
                continue

    return coords

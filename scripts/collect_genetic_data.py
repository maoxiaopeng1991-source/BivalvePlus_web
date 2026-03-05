#!/usr/bin/env python3
"""
Genetic Resources Collector for BivalvePlus.
Queries NCBI, ENA and BOLD APIs for genome assemblies, population genome data,
and DNA marker sequences for 4 target bivalve species.
Writes results to src/data/genetic-*.json files.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SPECIES = {
    104385: "Ruditapes decussatus",
    129788: "Ruditapes philippinarum",
    29158: "Mytilus galloprovincialis",
    29159: "Magallana gigas",
}

MARKERS = {
    "COI": "cytochrome oxidase subunit I",
    "16S": "16S ribosomal RNA",
    "18S": "18S ribosomal RNA",
    "28S": "28S ribosomal RNA",
    "ITS": "internal transcribed spacer",
    "ITS1": "internal transcribed spacer 1",
    "ITS2": "internal transcribed spacer 2",
    "cytb": "cytochrome b",
    "COII": "cytochrome oxidase subunit II",
    "H3": "histone H3",
    "EF1": "elongation factor 1-alpha",
}

# Resolve output directory (relative to this script)
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "src" / "data"

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_DATASETS = "https://api.ncbi.nlm.nih.gov/datasets/v2"
ENA_PORTAL = "https://www.ebi.ac.uk/ena/portal/api"
BOLD_API = "https://v4.boldsystems.org/index.php/API_Public"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "BivalvePlus-Collector/1.0"})


def _sleep():
    """Rate-limit: NCBI allows 3 req/sec without API key."""
    time.sleep(0.4)


# ---------------------------------------------------------------------------
# 1. Genome Assemblies (NCBI Datasets API + ENA)
# ---------------------------------------------------------------------------

def fetch_ncbi_genomes():
    """Fetch genome assemblies from NCBI Datasets API."""
    rows = []
    for taxid, species in SPECIES.items():
        url = f"{NCBI_DATASETS}/genome/taxon/{taxid}/dataset_report"
        params = {"page_size": 100}
        try:
            resp = SESSION.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [WARN] NCBI Datasets failed for {species} ({taxid}): {e}")
            _sleep()
            continue

        for asm in data.get("reports", []):
            info = asm.get("assembly_info", {})
            stats = asm.get("assembly_stats", {})
            accession = asm.get("accession", "")
            size_bp = stats.get("total_sequence_length")
            size_str = f"{int(size_bp) / 1e6:.0f} Mb" if size_bp else "—"
            rows.append({
                "species": species,
                "assembly": info.get("assembly_name", "—"),
                "version": accession.split(".")[-1] if "." in accession else "1",
                "size": size_str,
                "level": info.get("assembly_level", "—"),
                "database": "NCBI",
                "accession": accession,
                "link": f"https://www.ncbi.nlm.nih.gov/datasets/genome/{accession}/",
            })
        _sleep()
    return rows


def fetch_ena_assemblies():
    """Fetch genome assemblies from ENA Portal API."""
    rows = []
    for taxid, species in SPECIES.items():
        url = f"{ENA_PORTAL}/search"
        params = {
            "result": "assembly",
            "query": f"tax_tree({taxid})",
            "fields": "accession,assembly_name,assembly_level,genome_representation,base_count",
            "format": "json",
            "limit": 100,
        }
        try:
            resp = SESSION.get(url, params=params, timeout=30)
            if resp.status_code == 204 or not resp.text.strip():
                _sleep()
                continue
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [WARN] ENA assemblies failed for {species} ({taxid}): {e}")
            _sleep()
            continue

        for rec in data:
            accession = rec.get("accession", "")
            base_count = rec.get("base_count")
            size_str = f"{int(base_count) / 1e6:.0f} Mb" if base_count else "—"
            rows.append({
                "species": species,
                "assembly": rec.get("assembly_name", "—"),
                "version": accession.split(".")[-1] if "." in accession else "1",
                "size": size_str,
                "level": rec.get("assembly_level", "—"),
                "database": "ENA",
                "accession": accession,
                "link": f"https://www.ebi.ac.uk/ena/browser/view/{accession}",
            })
        _sleep()
    return rows


def collect_genomes():
    """Merge NCBI + ENA genome assemblies, deduplicate by accession."""
    print("[1/3] Collecting genome assemblies...")
    ncbi = fetch_ncbi_genomes()
    print(f"  NCBI: {len(ncbi)} assemblies")
    ena = fetch_ena_assemblies()
    print(f"  ENA:  {len(ena)} assemblies")

    seen = set()
    merged = []
    for row in ncbi + ena:
        acc = row["accession"].split(".")[0]  # normalize GCA_xxx vs GCA_xxx.1
        if acc and acc not in seen:
            seen.add(acc)
            merged.append(row)
    print(f"  Merged: {len(merged)} unique assemblies")
    return merged


# ---------------------------------------------------------------------------
# 2. Population Genome / WGS (NCBI SRA via Entrez + ENA read runs)
# ---------------------------------------------------------------------------

def fetch_ncbi_sra():
    """Fetch WGS/resequencing SRA runs from NCBI Entrez."""
    rows = []
    for taxid, species in SPECIES.items():
        # Search SRA for WGS strategy runs
        query = f"txid{taxid}[Organism] AND (WGS[Strategy] OR WGA[Strategy] OR OTHER[Strategy])"
        search_url = f"{NCBI_BASE}/esearch.fcgi"
        params = {
            "db": "sra",
            "term": query,
            "retmax": 500,
            "retmode": "json",
        }
        try:
            resp = SESSION.get(search_url, params=params, timeout=30)
            resp.raise_for_status()
            ids = resp.json().get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            print(f"  [WARN] NCBI SRA search failed for {species}: {e}")
            _sleep()
            continue
        _sleep()

        if not ids:
            continue

        # Fetch summaries in batches of 50
        for i in range(0, len(ids), 50):
            batch = ids[i:i + 50]
            summary_url = f"{NCBI_BASE}/esummary.fcgi"
            params = {
                "db": "sra",
                "id": ",".join(batch),
                "retmode": "json",
            }
            try:
                resp = SESSION.get(summary_url, params=params, timeout=30)
                resp.raise_for_status()
                result = resp.json().get("result", {})
            except Exception as e:
                print(f"  [WARN] NCBI SRA summary failed: {e}")
                _sleep()
                continue
            _sleep()

            for uid in batch:
                rec = result.get(uid, {})
                runs_xml = rec.get("runs", "")
                expxml = rec.get("expxml", "")

                # Extract run accession from the runs field
                run_acc = ""
                if 'acc="' in runs_xml:
                    run_acc = runs_xml.split('acc="')[1].split('"')[0]

                # Extract platform
                platform = "—"
                if 'Platform instrument_model="' in expxml:
                    platform = expxml.split('Platform instrument_model="')[1].split('"')[0]
                elif "<Platform>" in expxml:
                    platform = expxml.split("<Platform>")[1].split("<")[0] if "</Platform>" in expxml else "—"

                # Extract bioproject
                bioproject = "—"
                if 'Bioproject>' in expxml:
                    bp_part = expxml.split("Bioproject>")
                    if len(bp_part) > 1:
                        bioproject = bp_part[1].split("<")[0]

                # Extract total bases
                total_bases = ""
                if 'total_bases="' in runs_xml:
                    tb = runs_xml.split('total_bases="')[1].split('"')[0]
                    try:
                        total_bases = f"{int(tb) / 1e9:.1f} Gb"
                    except (ValueError, TypeError):
                        total_bases = "—"

                if run_acc:
                    r1 = f"https://sra-pub-run-odp.s3.amazonaws.com/sra/{run_acc}/{run_acc}"
                    rows.append({
                        "species": species,
                        "bioproject": bioproject,
                        "platform": platform,
                        "data_size": total_bases or "—",
                        "samples": "1",
                        "database": "NCBI SRA",
                        "accession": run_acc,
                        "link_r1": f"https://www.ncbi.nlm.nih.gov/sra/{run_acc}",
                        "link_r2": f"https://trace.ncbi.nlm.nih.gov/Traces/sra/?run={run_acc}",
                    })
    return rows


def fetch_ena_reads():
    """Fetch WGS read runs from ENA Portal API."""
    rows = []
    for taxid, species in SPECIES.items():
        url = f"{ENA_PORTAL}/search"
        params = {
            "result": "read_run",
            "query": f"tax_tree({taxid}) AND (library_strategy=\"WGS\" OR library_strategy=\"WGA\")",
            "fields": "run_accession,experiment_accession,study_accession,instrument_platform,instrument_model,base_count,fastq_ftp",
            "format": "json",
            "limit": 500,
        }
        try:
            resp = SESSION.get(url, params=params, timeout=30)
            if resp.status_code == 204 or not resp.text.strip():
                _sleep()
                continue
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [WARN] ENA reads failed for {species} ({taxid}): {e}")
            _sleep()
            continue

        for rec in data:
            run_acc = rec.get("run_accession", "")
            base_count = rec.get("base_count")
            size_str = f"{int(base_count) / 1e9:.1f} Gb" if base_count else "—"

            # Parse R1/R2 from fastq_ftp
            ftp_files = (rec.get("fastq_ftp") or "").split(";")
            link_r1 = f"https://{ftp_files[0]}" if len(ftp_files) > 0 and ftp_files[0] else ""
            link_r2 = f"https://{ftp_files[1]}" if len(ftp_files) > 1 and ftp_files[1] else ""

            platform = rec.get("instrument_model") or rec.get("instrument_platform") or "—"

            rows.append({
                "species": species,
                "bioproject": rec.get("study_accession", "—"),
                "platform": platform,
                "data_size": size_str,
                "samples": "1",
                "database": "ENA",
                "accession": run_acc,
                "link_r1": link_r1 or f"https://www.ebi.ac.uk/ena/browser/view/{run_acc}",
                "link_r2": link_r2 or "NUL",
            })
        _sleep()
    return rows


def collect_population():
    """Merge NCBI SRA + ENA read runs, deduplicate by run accession."""
    print("[2/3] Collecting population genome data...")
    ncbi = fetch_ncbi_sra()
    print(f"  NCBI SRA: {len(ncbi)} runs")
    ena = fetch_ena_reads()
    print(f"  ENA:      {len(ena)} runs")

    seen = set()
    merged = []
    # Prefer ENA (has direct fastq links), then NCBI
    for row in ena + ncbi:
        acc = row["accession"]
        if acc and acc not in seen:
            seen.add(acc)
            merged.append(row)
    print(f"  Merged: {len(merged)} unique runs")
    return merged


# ---------------------------------------------------------------------------
# 3. DNA Markers (NCBI Nucleotide + BOLD)
# ---------------------------------------------------------------------------

def fetch_ncbi_markers():
    """Fetch DNA marker sequence counts from NCBI Nucleotide via Entrez.

    Uses [Title] search for broader coverage (many sequences lack proper
    [Gene] annotation but have marker names in their titles).
    """
    rows = []
    for taxid, species in SPECIES.items():
        for marker, gene_name in MARKERS.items():
            # Use [Title] for broader matching (COI also try [Gene] for accuracy)
            query = f"txid{taxid}[Organism] AND {marker}[Title]"
            search_url = f"{NCBI_BASE}/esearch.fcgi"
            params = {
                "db": "nucleotide",
                "term": query,
                "retmax": 0,
                "retmode": "json",
            }
            try:
                resp = SESSION.get(search_url, params=params, timeout=30)
                resp.raise_for_status()
                count = int(resp.json().get("esearchresult", {}).get("count", 0))
            except Exception as e:
                print(f"  [WARN] NCBI nucleotide search failed for {species} {marker}: {e}")
                _sleep()
                continue
            _sleep()

            if count > 0:
                rows.append({
                    "species": species,
                    "marker": marker,
                    "gene": gene_name,
                    "sampling_site": "Various",
                    "samples": str(count),
                    "database": "NCBI Nucleotide",
                    "accession": f"txid{taxid}+{marker}",
                    "link": f"https://www.ncbi.nlm.nih.gov/nuccore/?term=txid{taxid}%5BOrganism%5D+AND+{marker}%5BTitle%5D",
                })
    return rows


def fetch_bold_markers():
    """Fetch barcode record counts from BOLD v4 API."""
    rows = []
    for taxid, species in SPECIES.items():
        url = f"{BOLD_API}/stats"
        params = {"taxon": species}
        try:
            resp = SESSION.get(url, params=params, timeout=30)
            if resp.status_code == 204 or not resp.text.strip():
                _sleep()
                continue
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [WARN] BOLD stats failed for {species}: {e}")
            _sleep()
            continue

        total = data.get("total_records", 0)

        if total and int(total) > 0:
            rows.append({
                "species": species,
                "marker": "COI",
                "gene": "cytochrome oxidase subunit I",
                "sampling_site": "Various",
                "samples": str(total),
                "database": "BOLD",
                "accession": species.replace(" ", "_"),
                "link": f"https://www.boldsystems.org/index.php/Taxbrowser_Taxonpage?taxon={species.replace(' ', '+')}",
            })
        _sleep()
    return rows


def collect_markers():
    """Merge NCBI nucleotide + BOLD marker data."""
    print("[3/3] Collecting DNA marker data...")
    ncbi = fetch_ncbi_markers()
    print(f"  NCBI Nucleotide: {len(ncbi)} marker entries")
    bold = fetch_bold_markers()
    print(f"  BOLD: {len(bold)} entries")
    merged = ncbi + bold
    print(f"  Total: {len(merged)} marker entries")
    return merged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_json(filename, rows):
    """Write data to a JSON file in src/data/."""
    output = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    filepath = DATA_DIR / filename
    filepath.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(f"  Written: {filepath} ({len(rows)} rows)")


def main():
    print("=" * 60)
    print("BivalvePlus Genetic Resources Collector")
    print(f"Target species: {len(SPECIES)}")
    print(f"Output directory: {DATA_DIR}")
    print("=" * 60)

    if not DATA_DIR.exists():
        print(f"ERROR: Data directory not found: {DATA_DIR}")
        sys.exit(1)

    genome_rows = collect_genomes()
    write_json("genetic-genome.json", genome_rows)

    population_rows = collect_population()
    write_json("genetic-population.json", population_rows)

    marker_rows = collect_markers()
    write_json("genetic-markers.json", marker_rows)

    print("\nDone!")


if __name__ == "__main__":
    main()

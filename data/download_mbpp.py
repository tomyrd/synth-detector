# data/download_mbpp.py
import json
from pathlib import Path

import requests


def download_mbpp():
    """Download MBPP dataset from GitHub"""
    url = "https://raw.githubusercontent.com/google-research/google-research/refs/heads/master/mbpp/mbpp.jsonl"

    output_dir = Path("data/mbpp")
    output_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(url)
    with open(output_dir / "mbpp.jsonl", "w") as f:
        f.write(response.text)

    samples = [json.loads(line) for line in response.text.strip().split("\n")]

    # Take first 100 for quick MVP
    data = samples[:100]

    with open(output_dir / "data.json", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Downloaded {len(samples)} samples")
    print(f"Data: {len(data)}")


if __name__ == "__main__":
    download_mbpp()

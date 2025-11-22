# Synthetic Code Detection Scripts

This directory contains scripts that replicate the functionality of the proof-of-concept notebooks, providing a more production-ready workflow.

## Main Script: synth_detector.py

The `synth_detector.py` script combines all the notebook functionality into a single command-line tool:

1. **Dataset Preparation** - Generates synthetic code from human-written samples
2. **Code Rewriting** - Creates variations of each code sample
3. **Similarity Computation** - Calculates similarity scores between originals and rewrites
4. **Detection** - Classifies code as human or synthetic based on similarity threshold

### Features

- Continuous status messages throughout the process
- Flexible pipeline execution (run full pipeline or individual steps)
- Generates JSON output with similarity scores
- Configurable parameters (number of rewrites, detection threshold, etc.)

### Usage Examples

#### Run Full Pipeline

Process MBPP data through all stages:

```bash
python scripts/synth_detector.py \
  --input data/mbpp/data.json \
  --full-pipeline \
  --num-samples 10 \
  --output-dir scripts
```

With custom parameters:

```bash
python scripts/synth_detector.py \
  --input data/mbpp/data.json \
  --full-pipeline \
  --num-samples 10 \
  --model codellama:7b-instruct \
  --gen-temperature 0.7 \
  --gen-top-p 0.9 \
  --n-rewrites 5 \
  --rewrite-temperature 0.9 \
  --rewrite-top-p 0.95 \
  --threshold 0.85
```

#### Run Individual Steps

**1. Prepare Dataset Only:**
```bash
python scripts/synth_detector.py \
  --input data/mbpp/data.json \
  --prepare-only \
  --num-samples 10
```

**2. Rewrite Code Only:**
```bash
python scripts/synth_detector.py \
  --detection-data scripts/detection_data.json \
  --rewrite-only \
  --n-rewrites 4
```

With custom rewrite parameters:
```bash
python scripts/synth_detector.py \
  --detection-data scripts/detection_data.json \
  --rewrite-only \
  --n-rewrites 6 \
  --rewrite-temperature 1.0 \
  --rewrite-top-p 0.98 \
  --rewrite-seed 42
```

**3. Compute Similarities Only:**
```bash
python scripts/synth_detector.py \
  --rewritten-data scripts/rewritten_data.json \
  --similarity-only
```

**4. Run Detection Only:**
```bash
python scripts/synth_detector.py \
  --similarity-data scripts/similarity_data.json \
  --detect-only \
  --threshold 0.9
```

### Command-Line Arguments

**General Parameters:**
- `--input`: Input MBPP data file (JSON format)
- `--num-samples`: Number of samples to process (default: all)
- `--output-dir`: Output directory for generated files (default: scripts)

**LLM Parameters:**
- `--model`: LLM model to use (default: codellama:7b-instruct)

**Generation Parameters** (for synthetic code generation):
- `--gen-temperature`: Temperature for synthetic code generation (default: None)
- `--gen-top-p`: Top-p value for synthetic code generation (default: None)

**Rewrite Parameters** (for code rewriting):
- `--n-rewrites`: Number of rewrites per code sample (default: 4)
- `--rewrite-temperature`: Temperature for code rewriting (default: 0.8)
- `--rewrite-top-p`: Top-p value for code rewriting (default: 0.95)
- `--rewrite-seed`: Seed for code rewriting (default: None for random)

**Detection Parameters:**
- `--threshold`: Detection threshold for classification (default: 0.7)

**Pipeline Options:**
- `--full-pipeline`: Run complete pipeline
- `--prepare-only`: Only prepare dataset
- `--rewrite-only`: Only rewrite code
- `--similarity-only`: Only compute similarities
- `--detect-only`: Only run detection

**Input Files for Partial Pipeline:**
- `--detection-data`: Input detection_data.json for rewrite step
- `--rewritten-data`: Input rewritten_data.json for similarity step
- `--similarity-data`: Input similarity_data.json for detection step

### Output Files

The script generates the following files in the output directory:

1. **detection_data.json** - Balanced dataset of human and synthetic code
2. **rewritten_data.json** - Code samples with their rewrites
3. **similarity_data.json** - Final output with similarity scores

### Parameter Tuning Guide

Understanding the configurable parameters:

**Temperature** (`--gen-temperature`, `--rewrite-temperature`):
- Lower values (0.1-0.5): More deterministic, focused outputs
- Medium values (0.6-0.8): Balanced creativity and consistency
- Higher values (0.9-1.5): More creative and varied outputs
- Use lower temperature for generation to make synthetic code more consistent
- Use higher temperature for rewrites to create more diverse variations

**Top-p** (`--gen-top-p`, `--rewrite-top-p`):
- Controls nucleus sampling
- Lower values (0.5-0.8): More focused, less diversity
- Higher values (0.9-0.99): More diversity in output
- Usually paired with temperature for better control

**Number of Rewrites** (`--n-rewrites`):
- More rewrites = more reliable similarity scores
- Typical range: 3-10
- Trade-off between accuracy and processing time

**Detection Threshold** (`--threshold`):
- Lower threshold: More sensitive, catches more synthetic code (higher false positives)
- Higher threshold: More conservative, fewer false positives (higher false negatives)
- Tune based on your precision/recall requirements

**Seed** (`--rewrite-seed`):
- Set for reproducible results
- Leave unset (None) for varied outputs across runs

### Requirements

Make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

The script requires:
- `ollama` package and CodeLlama model
- `numpy` for similarity calculations
- Python 3.7+

### Example Output

```
[STATUS] ============================================================
[STATUS] Synthetic Code Detection Pipeline
[STATUS] ============================================================
[STATUS] Starting dataset preparation...
[STATUS] Loaded 10 samples from data/mbpp/data.json
[STATUS] Generating synthetic code samples...
[STATUS] Generating synthetic code 1/10
[STATUS] Generating synthetic code 2/10
...
[STATUS] Dataset created: 20 total samples
[STATUS]   Human: 10
[STATUS]   Synthetic: 10
[STATUS] Saved dataset to scripts/detection_data.json
[STATUS] Starting code rewriting process...
[STATUS] Rewriting code sample 1/20
[STATUS]   Generated 4 rewrites
...
[STATUS] Starting similarity computation...
[STATUS] Computing similarity 1/20
[STATUS]   Similarity score: 0.9875
...
[STATUS] Saved similarity data to scripts/similarity_data.json
[STATUS] Similarity computation complete!
[STATUS] ============================================================
[STATUS] Pipeline completed successfully!
[STATUS] ============================================================
```

## Comparison with Notebooks

The notebooks are preserved in their original locations:
- `data/prepare_dataset.ipynb` → Corresponds to dataset preparation step
- `detector/rewritter.ipynb` → Corresponds to code rewriting step
- `detector/similarity.ipynb` → Corresponds to similarity computation step
- `detector/detector.ipynb` → Corresponds to detection step

The script provides the same functionality with:
- Better status messages and progress tracking
- Command-line interface for automation
- Modular design for running individual steps
- Easier integration into pipelines

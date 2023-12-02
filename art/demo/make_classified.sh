#!/usr/bin/env bash

# Define the base directory
base_dir="classified_documents"

# Create the base directory
mkdir -p "$base_dir"

# Create subdirectories and files
mkdir -p "$base_dir/AreaZ"
touch "$base_dir/AreaZ/extraterrestrial_technology.txt"
touch "$base_dir/AreaZ/interstellar_communications.pdf"

mkdir -p "$base_dir/IlluminatedOnes"
touch "$base_dir/IlluminatedOnes/members_only.csv"
touch "$base_dir/IlluminatedOnes/strategy_for_global_influence.docx"

mkdir -p "$base_dir/PrimalSightings"
touch "$base_dir/PrimalSightings/encrypted_evidence.png"
touch "$base_dir/PrimalSightings/hidden_cameras_locations.zip"

mkdir -p "$base_dir/TheKingLives"
touch "$base_dir/TheKingLives/coordinates_of_last_sighting.txt"
touch "$base_dir/TheKingLives/presley_dna_analysis.md"

# Output the result
echo "Created classified documents directory structure:"
ls -R "$base_dir"

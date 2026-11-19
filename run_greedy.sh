#!/bin/bash

mkdir -p images
SIZES=(1 2 4 8 16 32)

for size in "${SIZES[@]}"; do
    MAP="maze-map/maze512-${size}-0.map"
    SCEN="maze-scen/maze512-${size}-0.map.scen"
    
    if [ -f "$MAP" ] && [ -f "$SCEN" ]; then
        echo "----------------------------------------"
        echo "Running Greedy on scale: $size"
        echo "----------------------------------------"
        python3 main.py "$MAP" "$SCEN"
    else
        echo "Skipping scale $size: Files not found."
    fi
done

echo "Done"
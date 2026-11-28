import os
import numpy as np
import matplotlib.pyplot as plt

def visualize_search(grid, scenario, explored_coords, path, output_dir="images", filename="result.png"):
   
    save_path = os.path.join(output_dir, filename)

    # convert flat bytearray (1=passable, 0=blocked) to 2D RGB image
    base = np.frombuffer(grid.cells, dtype=np.uint8).reshape((grid.height, grid.width))
    img = np.stack([base * 255] * 3, axis=-1)  # White paths, black walls

    # color explored/visited states light blue
    for x, y in explored_coords:
        img[y, x] = [173, 216, 230]

    # color the final shortest path red
    if path:
        for x, y in path:
            img[y, x] = [255, 0, 0]

    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.scatter(*scenario.start, color="green", s=10, label="Start")
    plt.scatter(*scenario.goal, color="orange", s=10, label="Goal")
    plt.title(f"{grid.name} | Explored: {len(explored_coords)} states")
    plt.legend(loc="upper right")
    plt.axis("off")
    plt.tight_layout()
    
    # save directly to your specified folder
    plt.savefig(save_path, dpi=200)
    plt.close()  
    print(f"Saved visualization to: {save_path}")
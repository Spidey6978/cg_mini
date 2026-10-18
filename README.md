# Fractal Explorer

A small interactive fractal visualizer built with Python and Pygame. Explore three different recursive patterns, adjust their detail, and move around the canvas.

## Fractal modes

- **Tree** — a recursive branching tree. Adjust the branch angle and explore its changing shape.
- **Sierpinski** — a triangle subdivided recursively into smaller triangles.
- **Koch** — a snowflake outline built by repeatedly replacing line segments with triangular bumps.

## Requirements

- Python 3
- Pygame

Install Pygame if needed:

```bash
python -m pip install pygame
```

## Run

From the project directory:

```bash
python fractal_tree.py
```

## Controls

| Input | Action |
| --- | --- |
| Click a mode button | Switch between Tree, Sierpinski, and Koch |
| Hold **Left** / **Right** (Tree mode) | Continuously decrease / increase the branch angle |
| **Up** / **+** | Increase depth or iterations |
| **Down** / **−** | Decrease depth or iterations |
| Drag on the canvas | Pan the fractal |
| Mouse wheel | Zoom in or out around the pointer |
| **P** | Cycle through the three color palettes |
| **R** | Toggle automatic rotation |
| **C** | Reset zoom, pan, and rotation |
| **Esc** or close the window | Quit |

The branch angle has no imposed limit. Maximum recursion depth is limited per mode to keep rendering responsive: 12 for Tree, 8 for Sierpinski, and 6 for Koch.

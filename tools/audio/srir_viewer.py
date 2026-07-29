#!/usr/bin/env python3
"""
FLOW SRIR Vulkan-like Viewer
Displays PPM output from FLOW SRIR demo in a window
Self-contained with no external dependencies except pygame
"""

import sys
import os
import subprocess
import tempfile
import time
from pathlib import Path

try:
    import pygame
    from pygame.locals import *
except ImportError:
    print("Error: pygame is required. Install with: pip install pygame")
    sys.exit(1)

def load_ppm(filename):
    """Load PPM P3 format image, skipping SRIR/RPlan dumps"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find the P3 header (skip SRIR/RPlan dumps)
    ppm_start = -1
    for i, line in enumerate(lines):
        if line.strip() == 'P3':
            ppm_start = i
            break
    
    if ppm_start == -1:
        raise ValueError("No P3 header found in file")
    
    # Parse PPM data
    idx = ppm_start
    format_line = lines[idx].strip()
    if format_line != 'P3':
        raise ValueError(f"Unsupported format: {format_line}")
    
    idx += 1
    
    # Read dimensions
    while idx < len(lines) and lines[idx].strip().startswith('#'):
        idx += 1
    width, height = map(int, lines[idx].strip().split())
    idx += 1
    
    # Read max value
    max_val = int(lines[idx].strip())
    idx += 1
    
    # Read pixel data
    pixels = []
    for y in range(height):
        row = []
        for x in range(width):
            # Each line contains "R G B" values
            if idx >= len(lines):
                raise ValueError("Not enough pixel data")
            rgb_line = lines[idx].strip()
            if rgb_line:
                r, g, b = map(int, rgb_line.split())
            else:
                # Handle empty lines
                idx += 1
                continue
            idx += 1
            
            # Scale to 0-255 (already scaled in PPM)
            row.append((r, g, b))
        pixels.append(row)
    
    return width, height, pixels

def compile_and_run_flow(flow_file):
    """Compile FLOW file and get PPM output"""
    # Find the transpiler
    transpiler_path = Path(__file__).parent / "flow" / "transpiler.py"
    if not transpiler_path.exists():
        # Try from installed package
        transpiler_path = Path(__file__).parent.parent / "src" / "flow" / "transpiler.py"
    
    if not transpiler_path.exists():
        raise FileNotFoundError("FLOW transpiler not found")
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(transpiler_path.parent.parent)
    
    # Run transpiler with JIT
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'flow.transpiler', str(flow_file), '--jit'],
            capture_output=True,
            text=True,
            env=env,
            cwd=transpiler_path.parent.parent.parent
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FLOW compilation failed: {result.stderr}")
        
        return result.stdout
    except Exception as e:
        raise RuntimeError(f"Failed to run FLOW transpiler: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: srir_viewer.py <flow_file> [ppm_file]")
        print("  flow_file: FLOW source file to compile and display")
        print("  ppm_file:  Optional pre-compiled PPM file")
        return 1
    
    flow_file = Path(sys.argv[1])
    ppm_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load or generate PPM
    if ppm_file:
        try:
            width, height, pixels = load_ppm(ppm_file)
            print(f"Loaded PPM: {width}x{height}")
        except Exception as e:
            print(f"Error loading PPM: {e}")
            return 1
    else:
        try:
            print(f"Compiling FLOW: {flow_file}")
            ppm_output = compile_and_run_flow(flow_file)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ppm', delete=False) as f:
                f.write(ppm_output)
                temp_ppm = f.name
            
            try:
                width, height, pixels = load_ppm(temp_ppm)
                print(f"Generated PPM: {width}x{height}")
            finally:
                os.unlink(temp_ppm)
                
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    # Initialize Pygame
    pygame.init()
    
    # Create window (scale up if image is small)
    scale = max(1, min(4, 800 // width, 600 // height))
    window_width = width * scale
    window_height = height * scale
    
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("FLOW UI Demo")
    clock = pygame.time.Clock()
    
    # Create surface from pixel data
    surface = pygame.Surface((width, height))
    for y in range(height):
        for x in range(width):
            surface.set_at((x, y), pixels[y][x])
    
    # Scale surface to window size
    scaled_surface = pygame.transform.scale(surface, (window_width, window_height))
    
    # Font for UI
    try:
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
    except:
        font = pygame.font.SysFont('arial', 24)
        small_font = pygame.font.SysFont('arial', 18)
    
    # Main loop
    running = True
    show_info = True
    last_compile = time.time()
    
    print(f"Displaying FLOW SRIR render: {width}x{height} pixels (scaled {scale}x)")
    print("Controls:")
    print("  ESC or close window - Exit")
    print("  SPACE - Toggle info overlay")
    print("  R - Recompile FLOW (if source file provided)")
    
    while running:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    show_info = not show_info
                elif event.key == K_r and ppm_file is None:
                    # Recompile FLOW
                    if current_time - last_compile > 1.0:  # Prevent spam
                        try:
                            print("Recompiling...")
                            ppm_output = compile_and_run_flow(flow_file)
                            
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.ppm', delete=False) as f:
                                f.write(ppm_output)
                                temp_ppm = f.name
                            
                            try:
                                width, height, pixels = load_ppm(temp_ppm)
                                surface = pygame.Surface((width, height))
                                for y in range(height):
                                    for x in range(width):
                                        surface.set_at((x, y), pixels[y][x])
                                scaled_surface = pygame.transform.scale(surface, (window_width, window_height))
                                print("Recompiled successfully")
                            finally:
                                os.unlink(temp_ppm)
                                
                            last_compile = current_time
                        except Exception as e:
                            print(f"Recompile failed: {e}")
        
        # Clear screen with dark background
        screen.fill((10, 10, 15))
        
        # Draw image
        screen.blit(scaled_surface, (0, 0))
        
        # Draw UI overlay
        if show_info:
            # Semi-transparent background for text
            info_surface = pygame.Surface((350, 120))
            info_surface.set_alpha(200)
            info_surface.fill((20, 20, 30))
            screen.blit(info_surface, (10, 10))
            
            # Draw text
            info_text = font.render(f"FLOW UI Demo", True, (255, 255, 255))
            screen.blit(info_text, (20, 20))
            
            size_text = small_font.render(f"Resolution: {width}x{600}", True, (200, 200, 200))
            screen.blit(size_text, (20, 50))
            
            vulkan_text = small_font.render("Vulkan-like Render Context", True, (100, 255, 100))
            screen.blit(vulkan_text, (20, 75))
            
            if ppm_file is None:
                hotkey_text = small_font.render("Press R to recompile, SPACE to toggle info", True, (150, 150, 150))
                screen.blit(hotkey_text, (20, 100))
        
        # FPS counter
        fps = clock.get_fps()
        fps_text = small_font.render(f"FPS: {fps:.1f}", True, (255, 255, 100))
        screen.blit(fps_text, (window_width - 80, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

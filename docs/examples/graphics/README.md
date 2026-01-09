# Graphics Examples

This directory contains graphics programming examples in FLOW, including rendering, image generation, and visual effects.

## Files

- **srir_demo_phase0_final.flow** - SRIR (Simple Rendering Interface) demo
- **clean_ppm.flow** - PPM image generation
- **srir_demo.flow** - Basic SRIR rendering demonstration

## Running Examples

```bash
# Generate SRIR scene graph
flow run srir_demo_phase0_final.flow > output.ppm

# Create PPM image
flow run clean_ppm.flow > image.ppm

# Basic SRIR demo
flow run srir_demo.flow
```

## What You'll Learn

1. **Scene Graph Rendering**: How to build and render scene graphs
2. **Image Generation**: Creating PPM format images programmatically
3. **Graphics Primitives**: Basic drawing operations
4. **Color Management**: Working with colors and color spaces
5. **Transformations**: Translating and scaling graphics objects

## Graphics Concepts

### SRIR (Simple Rendering Interface)
SRIR is FLOW's built-in graphics system that provides:
- Scene graph representation
- Hierarchical transformations
- Efficient rendering pipeline
- Cross-platform support

### PPM Image Format
PPM (Portable Pixmap) is a simple image format:
- Plain text or binary format
- RGB color values
- Easy to generate programmatically
- Widely supported

## Key Examples

### Scene Graph Construction
```flow
# Create rectangles with transforms
let panel_rect = Rect2D { x: 0, y: 0, width: 104, height: 72 };
let panel_color = color_rgba(32, 40, 60, 255);
```

### Image Generation
```flow
# Generate PPM header
printf("P3\n%d %d\n255\n", width, height);

# Generate pixel data
for y in range(0, height) {
    for x in range(0, width) {
        printf("%d %d %d\n", r, g, b);
    }
}
```

## Graphics Pipeline

1. **Scene Definition**: Create graphics objects and hierarchy
2. **Transform Application**: Apply translations, rotations, scaling
3. **Rendering**: Convert scene graph to draw operations
4. **Output**: Generate image or display on screen

## Color Systems

FLOW supports multiple color representations:
- **RGBA**: 8-bit per channel (0-255)
- **Normalized**: Float values (0.0-1.0)
- **Indexed**: Color palette lookup

## Performance Considerations

1. **Batch Operations**: Group similar drawing operations
2. **Culling**: Skip off-screen objects
3. **Level of Detail**: Adjust complexity based on zoom
4. **Memory Management**: Efficient buffer usage

## Prerequisites

- Understanding of FLOW structs and functions
- Basic mathematics (geometry, linear algebra)
- [Data Structures](../data-structures/) completed

## Related Topics

- [Performance Examples](../performance/) - Graphics optimization
- [Graphics Module](../../library/stdlib-reference.md) - Graphics API reference
- [Language Reference - Graphics](../../language/graphics.md) - Graphics language features

## Viewing Output

Most examples generate PPM images. View them with:
- Image viewers (GIMP, Photoshop)
- Command line tools: `display image.ppm`
- Web browsers (most support PPM)
- Convert to other formats: `convert image.ppm image.png`

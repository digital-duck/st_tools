# Using Mermaid CLI to Specify Image Resolution and Size

When using the Mermaid CLI (Command Line Interface) to generate images, you can control the output resolution and size through several methods:

## Basic Command Structure

The basic command to generate an image with Mermaid CLI is:
```
mmdc -i input.mmd -o output.png
```

## Specifying Image Size and Resolution

### 1. Using Width and Height Parameters

You can directly specify the dimensions of the output image:

```
mmdc -i input.mmd -o output.png -w 1200 -h 800
```

- `-w` or `--width`: Sets the width in pixels
- `-h` or `--height`: Sets the height in pixels

### 2. Using Scale Factor

To scale the output while maintaining aspect ratio:

```
mmdc -i input.mmd -o output.png -s 2
```

- `-s` or `--scale`: Sets the scale factor (default is 1)

### 3. Setting Background Color

You can also specify the background color:

```
mmdc -i input.mmd -o output.png -b transparent
```

- `-b` or `--backgroundColor`: Sets the background color (can be color name, hex code, or "transparent")

### 4. Using SVG for Vector Graphics

For better scalability, consider outputting as SVG first:

```
mmdc -i input.mmd -o output.svg
```

Then you can convert the SVG to your desired resolution using other tools like Inkscape:

```
inkscape -w 1200 -h 800 output.svg -o output.png
```

## Example with Multiple Options

```
mmdc -i diagram.mmd -o diagram.png -w 1600 -h 900 -s 1.5 -b "#ffffff"

mmdc -i image_viewer-arch-design.mmd -o image_viewer-arch-design.png --width 1600 --height 800 -s 2.0 # -b "#ffffff"

mmdc -i image_viewer-arch-design.mmd -o image_viewer-arch-design.pdf -e pdf --width 1600 --height 800 -s 2.0 -b "#ffffff"

# issue: text not rendered
mmdc -i image_viewer-arch-design.mmd -o image_viewer-arch-design.svg -e svg --width 1600 --height 800 -s 2.0 -b "#ffffff"

```

This command generates a PNG image with:
- Width of 1600 pixels
- Height of 900 pixels
- Scale factor of 1.5
- White background

## Notes

- The actual output quality also depends on the complexity of your diagram
- For high-resolution outputs, SVG might be a better intermediate format
- Some Mermaid themes and configurations might affect the final appearance

Remember to check the Mermaid CLI documentation for the most up-to-date options as the tool continues to evolve.
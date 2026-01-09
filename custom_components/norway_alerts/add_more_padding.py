#!/usr/bin/env python3
"""Add more padding to varsom warning icons for better display in circular masks."""

import base64
import re
from pathlib import Path

# 8px padding (25% of original 32x32)
PADDING = 8
ORIGINAL_SIZE = 32
NEW_SIZE = ORIGINAL_SIZE + (PADDING * 2)  # 48x48

def add_padding_to_svg(svg_content: str) -> str:
    """Add padding to SVG by expanding viewBox."""
    # Replace width and height
    svg_content = re.sub(
        r'width="32"',
        f'width="{NEW_SIZE}"',
        svg_content
    )
    svg_content = re.sub(
        r'height="32"',
        f'height="{NEW_SIZE}"',
        svg_content
    )
    
    # Add viewBox to center the original content with padding
    svg_content = re.sub(
        r'(<svg[^>]*?)>',
        rf'\1 viewBox="-{PADDING} -{PADDING} {NEW_SIZE} {NEW_SIZE}">',
        svg_content
    )
    
    return svg_content

def process_icons():
    """Process all icon files and update icon_data.py."""
    icon_dir = Path(__file__).parent / "icons"
    icons = {}
    
    for svg_file in sorted(icon_dir.glob("icon-warning-*.svg")):
        # Extract name: icon-warning-flood-orange.svg -> flood-orange
        name = svg_file.stem.replace("icon-warning-", "")
        
        # Read and process SVG
        svg_content = svg_file.read_text(encoding='utf-8')
        padded_svg = add_padding_to_svg(svg_content)
        
        # Encode to base64
        b64_data = base64.b64encode(padded_svg.encode('utf-8')).decode('ascii')
        data_url = f"data:image/svg+xml;base64,{b64_data}"
        
        icons[name] = data_url
        print(f"Processed {name}")
    
    # Generate icon_data.py content
    output = ['"""Base64-encoded SVG icon data for varsom warnings.',
              '',
              'Icons are from NVE (Norwegian Water Resources and Energy Directorate).',
              'License: CC BY 4.0',
              '',
              f'Note: Icons have {PADDING}px padding added (48x48 canvas with 32x32 content)',
              'to fit better in circular masks without cutting corners.',
              '"""',
              '',
              'ICONS = {']
    
    for name, data_url in icons.items():
        output.append(f'    "{name}": "{data_url}",')
    
    output.append('}')
    
    # Write to icon_data.py
    icon_data_file = Path(__file__).parent / "icon_data.py"
    icon_data_file.write_text('\n'.join(output) + '\n', encoding='utf-8')
    print(f"\nGenerated {icon_data_file} with {len(icons)} icons")

if __name__ == "__main__":
    process_icons()

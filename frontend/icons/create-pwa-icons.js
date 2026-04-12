/**
 * Apple Design System PWA Icon Generator
 * Creates all required icon sizes for iOS and Android devices
 * 
 * Usage: node create-pwa-icons.js
 */

const fs = require('fs');
const path = require('path');

// SVG template for yoga logo (lotus flower)
const svgTemplate = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {{size}} {{size}}" width="{{size}}" height="{{size}}">
  <defs>
    <linearGradient id="grad-{{size}}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0071e3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#58a6ff;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background with rounded corners -->
  <rect width="{{size}}" height="{{size}}" rx="{{radius}}" fill="url(#grad-{{size}})"/>
  
  <!-- Lotus flower petals (Apple Blue on gradient) -->
  <g fill="white">
    <ellipse cx="{{centerX}}" cy="{{topY}}" rx="{{petalWidth}}" ry="{{petalHeight}}"/>
    <ellipse cx="{{rightX}}" cy="{{centerY}}" rx="{{petalWidth}}" ry="{{petalHeight}}" transform="rotate(90 {{rightX}} {{centerY})"/>
    <ellipse cx="{{centerX}}" cy="{{bottomY}}" rx="{{petalWidth}}" ry="{{petalHeight}}" transform="rotate(180 {{centerX}} {{bottomY})"/>
    <ellipse cx="{{leftX}}" cy="{{centerY}}" rx="{{petalWidth}}" ry="{{petalHeight}}" transform="rotate(-90 {{leftX}} {{centerY})"/>
  </g>
</svg>`;

// Icon sizes required by Apple and Android
const iconSizes = [
  { size: 40, name: 'apple-touch-icon-40x40', radius: 8, type: 'ios' },
  { size: 76, name: 'apple-touch-icon-76x76', radius: 12, type: 'ios' },
  { size: 120, name: 'apple-touch-icon-120x120', radius: 20, type: 'ios' },
  { size: 152, name: 'apple-touch-icon-152x152', radius: 24, type: 'ios' },
  { size: 167, name: 'apple-touch-icon-167x167', radius: 30, type: 'ios' },
  { size: 180, name: 'apple-touch-icon-180x180', radius: 32, type: 'ios' },
  { size: 192, name: 'icon-192x192', radius: 36, type: 'pwa' },
  { size: 512, name: 'icon-512x512', radius: 80, type: 'pwa' }
];

console.log('🎨 Creating PWA icons for Apple Design System...\n');

// Generate SVG files (since we can't create actual PNGs without canvas)
iconSizes.forEach(icon => {
  const centerX = icon.size / 2;
  const topY = icon.size * 0.35;
  const bottomY = icon.size * 0.65;
  const leftX = icon.size * 0.35;
  const rightX = icon.size * 0.65;
  
  // Adjust petal sizes based on icon size
  const petalWidth = icon.size * 0.2;
  const petalHeight = icon.size * 0.3;

  const svgContent = svgTemplate
    .replace(/{{size}}/g, icon.size)
    .replace(/{{radius}}/g, icon.radius)
    .replace(/{{centerX}}/g, centerX.toFixed(1))
    .replace(/{{topY}}/g, topY.toFixed(1))
    .replace(/{{bottomY}}/g, bottomY.toFixed(1))
    .replace(/{{leftX}}/g, leftX.toFixed(1))
    .replace(/{{rightX}}/g, rightX.toFixed(1))
    .replace(/{{petalWidth}}/g, petalWidth.toFixed(1))
    .replace(/{{petalHeight}}/g, petalHeight.toFixed(1));

  const filePath = path.join(__dirname, `${icon.name}.svg`);
  
  fs.writeFileSync(filePath, svgContent);
  console.log(`✅ Created: ${filePath}`);
});

console.log('\n📱 Icon sizes generated for Apple and Android devices');
console.log('💡 Note: For production, convert SVGs to PNG using a tool like Sharp or ImageMagick');

// Create README with conversion instructions
const readmeContent = `# PWA Icons - Apple Design System

This directory contains all icons required for iOS and Android PWA support.

## Generated Files (SVG)
- apple-touch-icon-40x40.svg
- apple-touch-icon-76x76.svg
- apple-touch-icon-120x120.svg
- apple-touch-icon-152x152.svg
- apple-touch-icon-167x167.svg
- apple-touch-icon-180x180.svg
- icon-192x192.svg
- icon-512x512.svg

## Conversion to PNG (Required for iOS)

### Using Sharp (Node.js):
\`\`\`bash
npm install sharp
npx sharp apple-touch-icon-40x40.svg -o apple-touch-icon-40x40.png
# Repeat for all SVG files
\`\`\`

### Using ImageMagick:
\`\`\`bash
convert -background none apple-touch-icon-40x40.svg -resize 40x40 apple-touch-icon-40x40.png
# Repeat for all SVG files
\`\`\`

## Apple Touch Icon Requirements

### iPhone (Retina):
- 180x180 pixels (iOS 7+)

### iPad Pro:
- 167x167 pixels (iPad Pro)

### iPad (Non-Pro):
- 152x152 pixels (iPad Retina)
- 76x76 pixels (iPad non-Retina)

### Legacy iOS:
- 120x120 pixels (iPhone pre-Retina)

## Android/Chrome Requirements

- 192x192 pixels (standard PWA icon)
- 512x512 pixels (high-res icon for Play Store)

## Color Scheme (Apple Design System)
- Primary: #0071e3 (Apple Blue)
- Secondary: #58a6ff (Bright Blue)
- Background: #f5f5f7 (Light Gray - not white!)

## Usage in HTML
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon-180x180.png">
`;

fs.writeFileSync(path.join(__dirname, 'README.md'), readmeContent);
console.log('✅ Created: README.md with conversion instructions');

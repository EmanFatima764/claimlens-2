# LightRays Integration - ClaimLens 2.0

## Overview
The **LightRays** component has been successfully integrated into ClaimLens 2.0, providing a cinematic WebGL-powered atmospheric background effect that enhances the visual appeal of your application.

## Component Location
```
frontend/src/components/LightRays.tsx
```

## Current Integration

### 1. Global Layout Integration
The component is integrated at the root layout level (`frontend/src/app/layout.tsx`):

```tsx
<LightRays
  raysOrigin="bottom-center"
  raysColor="#62d7ff"
  raysSpeed={0.8}
  lightSpread={1}
  rayLength={1.7}
  followMouse
  mouseInfluence={0.22}
  noiseAmount={0.015}
  distortion={0.05}
/>
```

### 2. Styling
The component uses CSS classes defined in `frontend/src/app/globals.css`:

```css
.light-rays {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.78;
  mix-blend-mode: screen;
}
```

## Features Implemented

### ✅ Performance Optimizations
- **Intersection Observer**: Only renders when visible in viewport
- **Optimized DPR**: Caps at 2x device pixel ratio for balanced quality/performance
- **Smooth Cleanup**: Proper WebGL context disposal

### ✅ Interactive Features
- **Mouse Following**: Rays smoothly follow cursor movement with momentum
- **Smooth Interpolation**: 95% smoothing for buttery animations
- **Responsive**: Automatically resizes with viewport

### ✅ Visual Effects
- **Origin**: `bottom-center` - rays emanate from bottom
- **Color**: `#62d7ff` - cyan matching your brand
- **Pulsating**: Gentle breathing effect enabled by default
- **Noise**: Film grain texture (0.015)
- **Distortion**: Organic wave effect (0.05)

## Component Props

| Prop | Type | Default | Current Value | Description |
|------|------|---------|---------------|-------------|
| `raysOrigin` | `RaysOrigin` | `'top-center'` | `'bottom-center'` | Origin point of rays |
| `raysColor` | `string` | `'#62d7ff'` | `'#62d7ff'` | Hex color of rays |
| `raysSpeed` | `number` | `0.65` | `0.8` | Animation speed |
| `lightSpread` | `number` | `1.2` | `1` | Width of light beam |
| `rayLength` | `number` | `1.8` | `1.7` | Length of rays |
| `followMouse` | `boolean` | `true` | `true` | Enable mouse tracking |
| `mouseInfluence` | `number` | `0.14` | `0.22` | Mouse tracking strength |
| `noiseAmount` | `number` | `0.015` | `0.015` | Film grain intensity |
| `distortion` | `number` | `0.05` | `0.05` | Wave distortion |
| `pulsating` | `boolean` | `true` | (default) | Breathing effect |
| `fadeDistance` | `number` | `1` | (default) | Fade out distance |
| `saturation` | `number` | `1` | (default) | Color saturation |

## Alternative Origin Options

You can change where the rays emanate from:

```tsx
// Top origins
raysOrigin="top-center"    // Straight down from top center
raysOrigin="top-left"      // From top-left corner
raysOrigin="top-right"     // From top-right corner

// Side origins
raysOrigin="left"          // From left side, center
raysOrigin="right"         // From right side, center

// Bottom origins (current)
raysOrigin="bottom-center" // Current - from bottom center
raysOrigin="bottom-left"   // From bottom-left corner
raysOrigin="bottom-right"  // From bottom-right corner
```

## Customization Examples

### Subtle Background Effect
```tsx
<LightRays
  raysOrigin="top-center"
  raysColor="#7c9cff"
  raysSpeed={0.5}
  lightSpread={0.8}
  rayLength={1.5}
  mouseInfluence={0.1}
  noiseAmount={0.01}
  distortion={0.02}
/>
```

### Dramatic Cinematic Effect
```tsx
<LightRays
  raysOrigin="bottom-center"
  raysColor="#00ffff"
  raysSpeed={1.5}
  lightSpread={1.5}
  rayLength={2}
  followMouse={true}
  mouseInfluence={0.4}
  noiseAmount={0.03}
  distortion={0.1}
/>
```

### Multi-colored Gradient (using multiple instances)
```tsx
<>
  <LightRays
    raysOrigin="top-left"
    raysColor="#7c9cff"
    lightSpread={0.8}
  />
  <LightRays
    raysOrigin="bottom-right"
    raysColor="#62d7ff"
    lightSpread={0.8}
  />
</>
```

## Theme Integration

The component respects your theme system:

```css
/* Dark mode (current) */
.light-rays {
  opacity: 0.78;
  mix-blend-mode: screen;
}

/* Light mode */
html[data-mode="light"] .light-rays {
  opacity: 0.16;
  mix-blend-mode: multiply;
}
```

## Performance Notes

1. **WebGL Acceleration**: Runs on GPU for smooth 60fps
2. **Intersection Observer**: Pauses when not visible
3. **Optimized Render Loop**: Minimal CPU usage
4. **Proper Cleanup**: No memory leaks

## Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Opera
- ⚠️ IE11 (WebGL 1.0 required)

## Technical Details

### WebGL Shaders
- **Vertex Shader**: Full-screen triangle technique
- **Fragment Shader**: Ray marching with organic noise
- **Uniforms**: Real-time parameter updates

### Animation Loop
- Uses `requestAnimationFrame` for optimal timing
- Smooth interpolation for mouse tracking
- Time-based animation (device-independent)

## Future Enhancements

Potential improvements you could add:

1. **Multiple Ray Layers**: Stack multiple instances with different colors
2. **Audio Reactivity**: Sync with audio input
3. **Custom Gradients**: Multi-color ray support
4. **Particle System**: Add floating particles
5. **Performance Modes**: Low/Medium/High quality presets

## Troubleshooting

### Rays not visible?
- Check z-index conflicts in CSS
- Verify WebGL is supported in browser
- Check opacity settings in globals.css

### Performance issues?
- Reduce `rayLength` and `lightSpread`
- Lower DPR in component (change `Math.min(window.devicePixelRatio, 2)` to `1`)
- Reduce `noiseAmount` and `distortion`

### Color doesn't match brand?
- Update `raysColor` prop with your brand color
- Adjust in `frontend/src/app/layout.tsx`

## Color Palette Recommendations

Based on your existing theme:

```tsx
// Primary Blue
raysColor="#7c9cff"  // var(--primary)

// Cyan (current)
raysColor="#62d7ff"  // var(--cyan)

// Green
raysColor="#73f0c1"  // var(--green)

// Violet
raysColor="#b89bff"  // var(--violet)

// Amber
raysColor="#ffc777"  // var(--amber)
```

## Summary

The LightRays component is **fully integrated** and working in your ClaimLens 2.0 application. It provides:

✅ Cinematic atmospheric lighting
✅ Interactive mouse following
✅ Performance-optimized WebGL rendering
✅ Theme-aware styling
✅ Responsive design
✅ Zero layout shift (fixed position)

The effect enhances your UI without interfering with content or interactions, creating a premium, high-end feel for your evidence intelligence platform.

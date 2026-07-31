# Glassmorphism & Liquid Glass Design System (`design.md`)

This document provides a comprehensive, framework-agnostic specification and component reference for recreating the exact **Liquid Glass** and **Glassmorphism** visual effects used in this application on any target website or web app.

> **Note**: Theme colors (brand primary/accent palette) and font family definitions have been intentionally omitted per specification. All glass structures are presented with neutral opacity layers, refractions, specular highlights, and backdrop blurs that adapt seamlessly to any color palette or typography system.

---

## 1. Architectural Overview

The liquid glass architecture operates across **4 layered depth levels**:

```
 ┌─────────────────────────────────────────────────────────┐
 │ Layer 4: WebGL 3D Physical Liquid Glass Lens (Three.js) │  <-- Physical optical refraction & chromatic dispersion
 ├─────────────────────────────────────────────────────────┤
 │ Layer 3: Dynamic Scroll Liquid Distortion Filter (SVG)  │  <-- Velocity-based fractal noise wave displacement
 ├─────────────────────────────────────────────────────────┤
 │ Layer 2: SVG Displacement Map & Refraction Surface      │  <-- Sub-pixel RGB channel splitting & edge reflection
 ├─────────────────────────────────────────────────────────┤
 │ Layer 1: CSS Backdrop-Filter Glassmorphism              │  <-- Multi-inset specular shadows, blur & saturation
 └─────────────────────────────────────────────────────────┘
```

---

## 2. Core Glass Design Tokens & Utilities

### 2.1 Neutral Glass Tokens (CSS Custom Properties)

Add these neutral tokens to your global CSS stylesheet (`:root` / `.dark`):

```css
:root {
  /* Surface translucency levels */
  --glass-surface-base: rgba(19, 22, 28, 0.85);
  --glass-surface-accent: rgba(28, 32, 39, 0.90);
  
  /* Border highlight reflection */
  --glass-border: rgba(255, 255, 255, 0.12);

  /* SVG Refraction Surface defaults */
  --glass-frost: 0;
  --glass-saturation: 1;
}
```

---

### 2.2 Framework-Agnostic CSS Utility Classes

```css
@layer utilities {
  /* -------------------------------------------------------------
   * 1. GLASS PANEL
   * Used for cards, navigation bars, modals, and floating containers.
   * ------------------------------------------------------------- */
  .glass-panel {
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    background: var(--glass-surface-base);
    border: 1px solid var(--glass-border);
    border-radius: 1.5rem;
    box-shadow: 
      inset 1px 1px 0.5px 0 rgba(255, 255, 255, 0.15),
      inset -1px -1px 0.5px 0 rgba(255, 255, 255, 0.05),
      0 8px 32px 0 rgba(0, 0, 0, 0.12);
  }

  /* -------------------------------------------------------------
   * 2. GLASS PILL / CAPSULE
   * Used for active buttons, genre tags, and view toggles.
   * ------------------------------------------------------------- */
  .glass-pill {
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    background: var(--glass-surface-accent);
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-radius: 9999px;
    box-shadow: 
      inset 1px 1px 0.5px 0 rgba(255, 255, 255, 0.5),
      inset -1px -1px 0.5px 0 rgba(0, 0, 0, 0.15),
      0 4px 12px rgba(0, 0, 0, 0.08);
  }

  /* -------------------------------------------------------------
   * 3. ACTIVE HIGHLIGHT GLASS CAPSULE (Tailwind Equivalent)
   * High-contrast glass indicator for active tab/toggle items.
   * ------------------------------------------------------------- */
  .glass-active-capsule {
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    background-color: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.20);
    box-shadow: 
      inset 1px 1px 1px 0 rgba(255, 255, 255, 0.40),
      0 2px 8px 0 rgba(0, 0, 0, 0.20);
    border-radius: 9999px;
  }
}
```

---

## 3. Component Specifications & Code Reference

### 3.1 SVG Refraction & Chromatic Aberration (`GlassSurface`)

This component dynamically computes an SVG displacement map rendered as a data URI and applies RGB channel-splitting chromatic aberration via standard SVG filter primitives (`feDisplacementMap` + `feColorMatrix`).

#### `GlassSurface.css`

```css
.glass-surface {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: opacity 0.26s ease-out;
}

.glass-surface__filter {
  width: 100%;
  height: 100%;
  pointer-events: none;
  position: absolute;
  inset: 0;
  opacity: 0;
  z-index: -1;
}

.glass-surface__content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: inherit;
  position: relative;
  z-index: 1;
}

/* SVG Refraction Filter Mode */
.glass-surface--svg {
  background: light-dark(hsl(0 0% 100% / var(--glass-frost, 0)), hsl(0 0% 0% / var(--glass-frost, 0)));
  backdrop-filter: var(--filter-id, url(#glass-filter)) saturate(var(--glass-saturation, 1));
  box-shadow:
    0 0 2px 1px light-dark(color-mix(in oklch, black, transparent 85%), color-mix(in oklch, white, transparent 65%)) inset,
    0 0 10px 4px light-dark(color-mix(in oklch, black, transparent 90%), color-mix(in oklch, white, transparent 85%)) inset,
    0px 4px 16px rgba(17, 17, 26, 0.05),
    0px 8px 24px rgba(17, 17, 26, 0.05),
    0px 16px 56px rgba(17, 17, 26, 0.05),
    0px 4px 16px rgba(17, 17, 26, 0.05) inset,
    0px 8px 24px rgba(17, 17, 26, 0.05) inset,
    0px 16px 56px rgba(17, 17, 26, 0.05) inset;
}

/* Fallback Mode (for WebKit Safari / Firefox where SVG backdrop filters are limited) */
.glass-surface--fallback {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px) saturate(1.8) brightness(1.2);
  -webkit-backdrop-filter: blur(12px) saturate(1.8) brightness(1.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow:
    inset 0 1px 0 0 rgba(255, 255, 255, 0.2),
    inset 0 -1px 0 0 rgba(255, 255, 255, 0.1);
}
```

#### `GlassSurface.tsx`

```tsx
import React, { useEffect, useState, useRef, useId } from 'react';
import './GlassSurface.css';

export interface GlassSurfaceProps {
  children?: React.ReactNode;
  width?: number | string;
  height?: number | string;
  borderRadius?: number;
  borderWidth?: number;
  brightness?: number;
  opacity?: number;
  blur?: number;
  displace?: number;
  backgroundOpacity?: number;
  saturation?: number;
  distortionScale?: number;
  redOffset?: number;
  greenOffset?: number;
  blueOffset?: number;
  xChannel?: 'R' | 'G' | 'B';
  yChannel?: 'R' | 'G' | 'B';
  mixBlendMode?: GlobalCompositeOperation | string;
  className?: string;
  style?: React.CSSProperties;
}

const GlassSurface: React.FC<GlassSurfaceProps> = ({
  children,
  width = 200,
  height = 80,
  borderRadius = 20,
  borderWidth = 0.07,
  brightness = 50,
  opacity = 0.93,
  blur = 11,
  displace = 0,
  backgroundOpacity = 0,
  saturation = 1,
  distortionScale = -180,
  redOffset = 0,
  greenOffset = 10,
  blueOffset = 20,
  xChannel = 'R',
  yChannel = 'G',
  mixBlendMode = 'difference',
  className = '',
  style = {}
}) => {
  const uniqueId = useId().replace(/:/g, '-');
  const filterId = `glass-filter-${uniqueId}`;
  const redGradId = `red-grad-${uniqueId}`;
  const blueGradId = `blue-grad-${uniqueId}`;

  const [svgSupported, setSvgSupported] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const feImageRef = useRef<SVGFEImageElement>(null);
  const redChannelRef = useRef<SVGFEDisplacementMapElement>(null);
  const greenChannelRef = useRef<SVGFEDisplacementMapElement>(null);
  const blueChannelRef = useRef<SVGFEDisplacementMapElement>(null);
  const gaussianBlurRef = useRef<SVGFEGaussianBlurElement>(null);

  const generateDisplacementMap = () => {
    const rect = containerRef.current?.getBoundingClientRect();
    const actualWidth = rect?.width || 400;
    const actualHeight = rect?.height || 200;
    const edgeSize = Math.min(actualWidth, actualHeight) * (borderWidth * 0.5);

    const svgContent = `
      <svg viewBox="0 0 ${actualWidth} ${actualHeight}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="${redGradId}" x1="100%" y1="0%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#0000"/>
            <stop offset="100%" stop-color="red"/>
          </linearGradient>
          <linearGradient id="${blueGradId}" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#0000"/>
            <stop offset="100%" stop-color="blue"/>
          </linearGradient>
        </defs>
        <rect x="0" y="0" width="${actualWidth}" height="${actualHeight}" fill="black"></rect>
        <rect x="0" y="0" width="${actualWidth}" height="${actualHeight}" rx="${borderRadius}" fill="url(#${redGradId})" />
        <rect x="0" y="0" width="${actualWidth}" height="${actualHeight}" rx="${borderRadius}" fill="url(#${blueGradId})" style="mix-blend-mode: ${mixBlendMode}" />
        <rect x="${edgeSize}" y="${edgeSize}" width="${actualWidth - edgeSize * 2}" height="${actualHeight - edgeSize * 2}" rx="${borderRadius}" fill="hsl(0 0% ${brightness}% / ${opacity})" style="filter:blur(${blur}px)" />
      </svg>
    `;

    return `data:image/svg+xml,${encodeURIComponent(svgContent)}`;
  };

  const updateDisplacementMap = () => {
    feImageRef.current?.setAttribute('href', generateDisplacementMap());
  };

  useEffect(() => {
    updateDisplacementMap();
    [
      { ref: redChannelRef, offset: redOffset },
      { ref: greenChannelRef, offset: greenOffset },
      { ref: blueChannelRef, offset: blueOffset }
    ].forEach(({ ref, offset }) => {
      if (ref.current) {
        ref.current.setAttribute('scale', (distortionScale + offset).toString());
        ref.current.setAttribute('xChannelSelector', xChannel);
        ref.current.setAttribute('yChannelSelector', yChannel);
      }
    });

    gaussianBlurRef.current?.setAttribute('stdDeviation', displace.toString());
  }, [width, height, borderRadius, borderWidth, brightness, opacity, blur, displace, distortionScale, redOffset, greenOffset, blueOffset, xChannel, yChannel, mixBlendMode]);

  useEffect(() => {
    if (!containerRef.current) return;
    const resizeObserver = new ResizeObserver(() => setTimeout(updateDisplacementMap, 0));
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    const isWebkit = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
    const isFirefox = /Firefox/.test(navigator.userAgent);
    setSvgSupported(!isWebkit && !isFirefox);
  }, []);

  const containerStyle = {
    ...style,
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
    borderRadius: `${borderRadius}px`,
    '--glass-frost': backgroundOpacity,
    '--glass-saturation': saturation,
    '--filter-id': `url(#${filterId})`
  } as React.CSSProperties;

  return (
    <div
      ref={containerRef}
      className={`glass-surface ${svgSupported ? 'glass-surface--svg' : 'glass-surface--fallback'} ${className}`}
      style={containerStyle}
    >
      <svg className="glass-surface__filter" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id={filterId} colorInterpolationFilters="sRGB" x="0%" y="0%" width="100%" height="100%">
            <feImage ref={feImageRef} x="0" y="0" width="100%" height="100%" preserveAspectRatio="none" result="map" />
            <feDisplacementMap ref={redChannelRef} in="SourceGraphic" in2="map" id="redchannel" result="dispRed" />
            <feColorMatrix in="dispRed" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="red" />
            <feDisplacementMap ref={greenChannelRef} in="SourceGraphic" in2="map" id="greenchannel" result="dispGreen" />
            <feColorMatrix in="dispGreen" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="green" />
            <feDisplacementMap ref={blueChannelRef} in="SourceGraphic" in2="map" id="bluechannel" result="dispBlue" />
            <feColorMatrix in="dispBlue" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="blue" />
            <feBlend in="red" in2="green" mode="screen" result="rg" />
            <feBlend in="rg" in2="blue" mode="screen" result="output" />
            <feGaussianBlur ref={gaussianBlurRef} in="output" stdDeviation="0.7" />
          </filter>
        </defs>
      </svg>
      <div className="glass-surface__content">{children}</div>
    </div>
  );
};

export default GlassSurface;
```

---

### 3.2 Scroll-Induced Liquid Ripple Distortion (`GlassFilter`)

Adds dynamic fluid inertia to glass elements on scroll by linking scroll velocity to an SVG fractal noise displacement filter.

```tsx
import React, { useEffect, useRef } from 'react';

export const GlassFilter: React.FC = () => {
  return (
    <svg className="fixed pointer-events-none w-0 h-0" aria-hidden="true">
      <defs>
        <filter id="container-glass" x="0%" y="0%" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence id="liquid-turbulence" type="fractalNoise" baseFrequency="0.05 0.05" numOctaves="1" seed="1" result="turbulence" />
          <feGaussianBlur id="liquid-noise-blur" in="turbulence" stdDeviation="2" result="blurredNoise" />
          <feDisplacementMap id="liquid-displacement" in="SourceGraphic" in2="blurredNoise" scale="0" xChannelSelector="R" yChannelSelector="B" result="displaced" />
          <feGaussianBlur in="displaced" stdDeviation="4" result="finalBlur" />
          <feComposite in="finalBlur" in2="finalBlur" operator="over" />
        </filter>
      </defs>
    </svg>
  );
};

export function useScrollDistortion() {
  const displacementRef = useRef<SVGFEDisplacementMapElement | null>(null);
  const lastScrollY = useRef(window.scrollY);
  const velocityRef = useRef(0);
  const animationFrameRef = useRef(0);

  useEffect(() => {
    displacementRef.current = document.getElementById('liquid-displacement') as SVGFEDisplacementMapElement | null;

    const onScroll = () => {
      const currentScrollY = window.scrollY;
      const delta = currentScrollY - lastScrollY.current;
      velocityRef.current = Math.min(Math.max(delta * 2, -100), 100);
      lastScrollY.current = currentScrollY;
    };

    window.addEventListener('scroll', onScroll, { passive: true });

    const loop = () => {
      velocityRef.current *= 0.9; // decay factor
      if (displacementRef.current) {
        const scale = Math.abs(velocityRef.current);
        displacementRef.current.setAttribute('scale', scale.toFixed(2));
      }
      animationFrameRef.current = requestAnimationFrame(loop);
    };
    loop();

    return () => {
      window.removeEventListener('scroll', onScroll);
      cancelAnimationFrame(animationFrameRef.current);
    };
  }, []);
}
```

---

### 3.3 WebGL 3D Physical Liquid Glass Lens (`FluidGlass`)

Renders a 3D physical glass lens sphere using `@react-three/fiber` and `Three.js` `MeshPhysicalMaterial`. The lens dynamically tracks mouse position with spring damping physics and refracts underlying page elements.

> **Dependencies**: `three`, `@react-three/fiber`, `maath`

```tsx
import * as THREE from 'three';
import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { easing } from 'maath';

export interface FluidGlassProps {
  mode?: 'lens' | 'bar' | 'cube';
  scale?: number;
  ior?: number;
  thickness?: number;
  transmission?: number;
  roughness?: number;
  chromaticAberration?: number;
  anisotropy?: number;
  style?: React.CSSProperties;
  className?: string;
}

function GlassLens({
  shape = 'sphere',
  followPointer = true,
  modeProps = {}
}: {
  shape?: 'sphere' | 'box' | 'cylinder';
  followPointer?: boolean;
  modeProps?: Record<string, any>;
}) {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {
    const { viewport, pointer } = state;
    const destX = followPointer ? (pointer.x * viewport.width) / 4 : 0;
    const destY = followPointer ? (pointer.y * viewport.height) / 4 : 0;

    if (meshRef.current) {
      easing.damp3(meshRef.current.position, [destX, destY, 0], 0.15, delta);
      meshRef.current.rotation.y += delta * 0.4;
      meshRef.current.rotation.x += delta * 0.2;
    }
  });

  const {
    scale = 2.2,
    ior = 1.25,
    thickness = 1.2,
    roughness = 0.05,
    transmission = 0.98,
    chromaticAberration = 0.05,
    anisotropy = 0.01
  } = modeProps;

  return (
    <mesh ref={meshRef} scale={scale} rotation-x={shape === 'cylinder' ? Math.PI / 2 : 0}>
      {shape === 'sphere' && <sphereGeometry args={[1, 64, 64]} />}
      {shape === 'box' && <boxGeometry args={[1.5, 1.5, 1.5]} />}
      {shape === 'cylinder' && <cylinderGeometry args={[1, 1, 0.5, 64]} />}
      
      <meshPhysicalMaterial
        transmission={transmission}
        opacity={1}
        transparent={true}
        roughness={roughness}
        ior={ior}
        thickness={thickness}
        anisotropy={anisotropy}
        dispersion={chromaticAberration}
        specularColor={new THREE.Color('#ffffff')}
        specularIntensity={1}
        clearcoat={1}
        clearcoatRoughness={0}
        color={new THREE.Color('#ffffff')}
        attenuationColor={new THREE.Color('#ffffff')}
        attenuationDistance={1}
      />
    </mesh>
  );
}

export default function FluidGlass({
  mode = 'lens',
  style = {},
  className = '',
  scale,
  ior,
  thickness,
  transmission,
  roughness,
  chromaticAberration,
  anisotropy
}: FluidGlassProps) {
  const overrides = { scale, ior, thickness, transmission, roughness, chromaticAberration, anisotropy };
  const shape = mode === 'bar' ? 'cylinder' : mode === 'cube' ? 'box' : 'sphere';

  return (
    <div className={`w-full h-full relative overflow-hidden pointer-events-none ${className}`} style={style}>
      <Canvas
        camera={{ position: [0, 0, 10], fov: 45 }}
        gl={{ alpha: true, antialias: true, powerPreference: 'high-performance' }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={2} />
        <directionalLight position={[10, 10, 10]} intensity={3} />
        <directionalLight position={[-10, -10, -10]} intensity={1.5} color="#ffffff" />
        <pointLight position={[0, 0, 5]} intensity={2} color="#ffffff" />
        <GlassLens shape={shape} followPointer={mode !== 'bar'} modeProps={overrides} />
      </Canvas>
    </div>
  );
}
```

---

### 3.4 Interactive Glass Navigation & Pill Indicators (`Navbar`)

Smooth spring-animated glass capsule indicators for tab bars using Framer Motion.

#### Hover/Active Fluid Glass Pill (Framer Motion)

```tsx
import { motion } from 'framer-motion';

// Insert this inside an active or hovered nav button container
<motion.div
  layoutId="fluid-glass-nav-pill"
  className="absolute inset-0 rounded-full bg-white/20 dark:bg-white/15 border border-white/20 shadow-[inset_1px_1px_1px_rgba(255,255,255,0.4),0_2px_8px_rgba(0,0,0,0.2)] backdrop-blur-md -z-10 pointer-events-none"
  transition={{
    type: 'spring',
    stiffness: 450,
    damping: 35
  }}
/>
```

#### Mobile Touch-Sliding Glass Bar

```tsx
/* Mobile Floating Bottom Glass Tab Bar */
<div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-2rem)] max-w-md pointer-events-auto">
  <div className="glass-panel bg-black/60 backdrop-blur-2xl border border-white/15 rounded-full p-2.5 shadow-2xl flex items-center justify-around select-none touch-none">
    {/* Navigation Items with motion.div layoutId="fluid-glass-mobile-pill" */}
  </div>
</div>
```

---

## 4. Quick Implementation Checklist for Another Project

1. **Include CSS Tokens & Utilities**: Copy Section 2 (`--glass-surface-base`, `.glass-panel`, `.glass-pill`, `.glass-active-capsule`) directly into your app's global CSS file.
2. **Add Refraction Filter**: Drop `GlassFilter.tsx` into your root app layout to activate global scroll fluid distortion.
3. **Use Glass Panels**: Replace solid card backgrounds with `class="glass-panel"`.
4. **Use Glass Capsules**: Style active navigation items, badges, and toggle switches with `class="glass-pill"` or `.glass-active-capsule`.
5. **Add 3D Glass Lens (Optional)**: If WebGL is enabled in your project stack, mount `<FluidGlass mode="lens" />` in your hero or background container.

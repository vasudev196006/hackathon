# 🧊 Liquid Glass & Glassmorphism Design System — Complete Theme Guide (`theme.md`)

This document is the **complete design system reference and implementation guide** for replicating the **Pure Liquid Glass & Glassmorphism Theme** on any web application.

---

## 🎨 1. Core Color Palette Tokens (`:root`)

Copy and paste these CSS custom properties into your global stylesheet (e.g., `theme.css` or `index.css`).

```css
:root {
  /* --- BASE SURFACES --- */
  --bg-dark: #09090b;                            /* Deep Void Background */
  --glass-surface-base: rgba(15, 23, 42, 0.85);  /* Translucent Liquid Glass Surface */
  --glass-surface-accent: rgba(28, 32, 39, 0.90);/* Elevated Glass Surface & Hover */
  --bg-card: rgba(24, 24, 27, 0.65);             /* Glassmorphism Card Container */
  --bg-card-hover: rgba(39, 39, 42, 0.75);       /* Hover State Card Surface */

  /* --- SPECULAR GLASS BORDERS & REFLECTION --- */
  --border-glass: rgba(255, 255, 255, 0.14);    /* Subtle Glass Border */
  --border-bright: rgba(255, 255, 255, 0.28);   /* Refractive Edge Border */
  --border-glow: rgba(255, 205, 117, 0.25);     /* Ambient Gold Glow Specular Edge */

  /* --- TYPOGRAPHY HIERARCHY --- */
  --text-main: #f8fafc;                          /* Primary High-Contrast Text */
  --text-muted: #a1a1aa;                         /* Secondary Subtitle / Body Copy */
  --text-dim: #71717a;                           /* Low-Emphasis Metadata & Footers */

  /* --- SENTIMENT & ACCENT SPECTRUM --- */
  --accent-gold: #ffcd75;                        /* Gold Highlight / Gradient Accent */
  --accent-cyan: #06b6d4;                        /* Electric Cyan / Neutral Telemetry */
  --accent-emerald: #10b981;                     /* Emerald Green / Support Stance */
  --accent-rose: #f43f5e;                        /* Rose Red / Opposition Stance */
  --accent-amber: #f59e0b;                       /* Amber / Volatility Alert */
  --accent-indigo: #6366f1;                      /* Indigo / AI Assistant Accents */

  /* --- TYPOGRAPHY & SPACING TOKENS --- */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --radius-xl: 24px;
  --radius-lg: 16px;
  --radius-md: 10px;
  --radius-pill: 9999px;

  /* --- ANIMATION PHYSICS --- */
  --transition-smooth: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

## ✒️ 2. Typography & Fonts

### Font Import
Add this Google Fonts link in your `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
```

### Global Typography Rules
```css
body {
  background-color: var(--bg-dark);
  color: var(--text-main);
  font-family: var(--font-sans);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* Gradient Hero Headline */
.gradient-text {
  background: linear-gradient(135deg, #ffffff 0%, var(--accent-gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## 🧊 3. Core Reusable Glass Components

### A. Liquid Glass Panel (`.glass-panel`)
Use for main modal windows, floating cards, or primary dashboard panels.

```css
.glass-panel {
  background: var(--glass-surface-base);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-xl);
  box-shadow: 
    inset 1px 1px 0.5px 0 rgba(255, 255, 255, 0.20),
    inset -1px -1px 0.5px 0 rgba(255, 255, 255, 0.05),
    0 20px 50px rgba(0, 0, 0, 0.55);
}
```

---

### B. Liquid Glass Pill Capsule (`.glass-pill`)
Use for header tags, status capsules, chips, or pill buttons.

```css
.glass-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 1.35rem;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.14) 0%, rgba(255, 255, 255, 0.04) 50%, rgba(255, 255, 255, 0.09) 100%);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.30);
  color: var(--text-main);
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45), inset 0 1.5px 1px rgba(255, 255, 255, 0.40);
  transition: var(--transition-smooth);
  text-decoration: none;
  white-space: nowrap;
}

.glass-pill:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0.08) 50%, rgba(255, 255, 255, 0.16) 100%);
  border-color: rgba(255, 255, 255, 0.50);
  transform: translateY(-2px);
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.60), inset 0 2px 2px #ffffff;
  color: #ffffff;
}
```

---

### C. Floating Liquid Glass Orb Button (`.floating-map-btn` / `.chatbot-toggle-btn`)
Use for bottom floating action widgets (e.g. Map redirect, Chatbot, Help button).

```css
.floating-glass-btn {
  position: fixed;
  bottom: 24px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.28);
  color: #f8fafc;
  box-shadow: 
    inset 1px 1px 1px 0 rgba(255, 255, 255, 0.45),
    inset -1px -1px 1px 0 rgba(0, 0, 0, 0.25),
    0 10px 30px rgba(0, 0, 0, 0.35);
  cursor: pointer;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  transition: var(--transition-smooth);
}

.floating-glass-btn:hover {
  background: rgba(255, 255, 255, 0.16);
  border-color: rgba(255, 255, 255, 0.45);
  transform: scale(1.08) translateY(-2px);
  box-shadow: 
    inset 1px 1px 1.5px 0 rgba(255, 255, 255, 0.65),
    0 14px 36px rgba(0, 0, 0, 0.45);
  color: #ffffff;
}

.floating-glass-btn svg {
  width: 26px !important;
  height: 26px !important;
  stroke: #f8fafc !important;
  stroke-width: 2px !important;
  fill: none !important;
  flex-shrink: 0;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.4));
}
```

---

### D. Liquid Glass Search Input (`.liquid-glass-search`)
Use for primary search bars or prominent input forms.

```css
.liquid-glass-search {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.03) 50%, rgba(255, 255, 255, 0.08) 100%);
  backdrop-filter: blur(28px) saturate(200%);
  -webkit-backdrop-filter: blur(28px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: var(--radius-pill);
  padding: 0.4rem 0.5rem 0.4rem 1.25rem;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.30);
  transition: var(--transition-smooth);
}

.liquid-glass-search:focus-within {
  border-color: rgba(255, 255, 255, 0.45);
  box-shadow: 0 16px 44px rgba(0, 0, 0, 0.55), inset 0 1.5px 1.5px #ffffff;
}

.liquid-glass-search input {
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 0.95rem;
  width: 100%;
}
```

---

## 📱 4. Mobile Responsiveness Rules (Non-Stacking Capsules)

To keep top header navigation pills on a **single non-stacking horizontal row** across all mobile devices:

```css
@media (max-width: 768px) {
  /* Enforce Single Horizontal Row */
  .brand-pill-wrapper {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    gap: 0.5rem;
  }

  .header-capsule-group {
    display: inline-flex;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.35rem;
    flex-shrink: 0;
  }

  .glass-pill {
    padding: 0.38rem 0.75rem;
    font-size: 0.72rem;
    white-space: nowrap;
  }
}

@media (max-width: 420px) {
  /* Hide extra text labels on small phones to preserve horizontal fit */
  .brand-name {
    display: none;
  }

  .glass-pill {
    padding: 0.35rem 0.6rem;
    font-size: 0.7rem;
  }

  .capsule-arrow {
    display: none;
  }
}
```

---

## 📐 5. Key Vector Icons (SVG Source)

### Location Pin Icon (Live Map)
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
  <circle cx="12" cy="10" r="3"></circle>
</svg>
```

### Glass Chat Lens Icon (Assistant Widget)
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
</svg>
```

### Full Workstation Desktop Icon
```html
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
  <line x1="8" y1="21" x2="16" y2="21"></line>
  <line x1="12" y1="17" x2="12" y2="21"></line>
</svg>
```

---

## ⚡ Quick Implementation Steps for Any New Site

1. Paste section **1 (CSS Tokens)** into your main `.css` file.
2. Add the **Google Font Inter** tag to your HTML `<head>`.
3. Wrap your page containers in `.glass-panel` or use `.glass-pill` for navigation capsules and buttons.
4. Enjoy a 100% consistent, ultra-clean, high-specular **Liquid Glass** user experience!

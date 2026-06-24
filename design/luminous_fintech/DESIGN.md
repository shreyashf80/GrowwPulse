---
name: Luminous Fintech
colors:
  surface: '#0d150d'
  surface-dim: '#0d150d'
  surface-bright: '#333b32'
  surface-container-lowest: '#081008'
  surface-container-low: '#151e15'
  surface-container: '#192219'
  surface-container-high: '#242c23'
  surface-container-highest: '#2e372e'
  on-surface: '#dce5d7'
  on-surface-variant: '#bbcbb8'
  inverse-surface: '#dce5d7'
  inverse-on-surface: '#2a3329'
  outline: '#869583'
  outline-variant: '#3c4a3c'
  surface-tint: '#3ce36a'
  primary: '#3fe56c'
  on-primary: '#003912'
  primary-container: '#00c853'
  on-primary-container: '#004c1b'
  inverse-primary: '#006e2a'
  secondary: '#ffb77a'
  on-secondary: '#4c2700'
  secondary-container: '#ff8f00'
  on-secondary-container: '#623400'
  tertiary: '#ffb7b0'
  on-tertiary: '#680008'
  tertiary-container: '#ff8d84'
  on-tertiary-container: '#88000e'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#69ff87'
  primary-fixed-dim: '#3ce36a'
  on-primary-fixed: '#002108'
  on-primary-fixed-variant: '#00531e'
  secondary-fixed: '#ffdcc2'
  secondary-fixed-dim: '#ffb77a'
  on-secondary-fixed: '#2e1500'
  on-secondary-fixed-variant: '#6d3a00'
  tertiary-fixed: '#ffdad6'
  tertiary-fixed-dim: '#ffb3ac'
  on-tertiary-fixed: '#410003'
  on-tertiary-fixed-variant: '#930010'
  background: '#0d150d'
  on-background: '#dce5d7'
  surface-variant: '#2e372e'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system establishes a sophisticated, high-performance environment for fintech analytics. The brand personality is authoritative yet modern, blending the precision of a Bloomberg terminal with the sleek, user-centric aesthetics of contemporary SaaS platforms. It targets data-conscious investors who require clarity amidst complexity.

The visual style is **Glassmorphism**, characterized by depth, light refraction, and layered transparency. The UI avoids the heavy, opaque "blocks" typical of traditional finance apps, opting instead for a weightless, immersive feel where data floats on a deep, obsidian canvas. Key attributes include:
- **Translucency:** Use of backdrop filters to maintain context and depth.
- **Precision:** Fine details, subtle borders, and intentional use of negative space.
- **Fluidity:** Smooth transitions and reactive hover states that signal system responsiveness.

## Colors

The palette is engineered for a dark-room environment, minimizing eye strain while maximizing the "pop" of critical financial indicators.

- **Background (#0D0D0D):** A deep, true black that serves as the infinite canvas, allowing glass layers to stack effectively.
- **Primary Green (#00C853):** Reserved for growth, positive trends, and primary action calls.
- **Accent Amber (#FF8F00):** Used for warnings, pending states, or neutral-to-cautionary data points.
- **Accent Red (#D32F2F):** Strictly for decline, errors, and high-priority alerts.
- **Surface & Glass:** Interactive surfaces use varying opacities of white (3-8%) combined with a high-saturation backdrop blur (20px+) to create the glass effect.

## Typography

This design system utilizes **Inter** for its exceptional legibility in data-dense environments. The type scale is optimized for hierarchy, ensuring that large-scale figures (financial totals) are immediately distinct from granular metadata.

- **Monospaced feel:** While Inter is a neo-grotesque, its tabular numbers feature should be enabled for all data-heavy displays to ensure column alignment in tables.
- **Hierarchy:** Use `label-md` for secondary metadata and table headers, often in a muted grey (`rgba(255,255,255,0.6)`).
- **Headlines:** Keep headings tight and bold to contrast against the ethereal nature of the glass containers.

## Layout & Spacing

The layout follows a **fluid grid** model with standardized 24px outer margins and 16px gutters. 

- **Desktop (1440px+):** 12-column grid. Side navigation is fixed at 240px, with content expanding in the remaining space.
- **Tablet (768px - 1024px):** 8-column grid. Side navigation collapses to a 64px icon rail.
- **Mobile (<768px):** 4-column grid. All glass cards stack vertically with 16px spacing.

Avoid vertical dividers. Use spacing and varying levels of glass opacity to separate content areas. Use a 4px base unit for all padding and margin definitions to ensure rhythmic consistency.

## Elevation & Depth

Depth is not communicated via shadows, but through **Tonal Layers and Backdrop Blurs**. 

- **Level 0 (Base):** The solid #0D0D0D background.
- **Level 1 (Cards):** Surface: `rgba(255, 255, 255, 0.03)`, Border: `1px solid rgba(255, 255, 255, 0.08)`, Backdrop-blur: `24px`.
- **Level 2 (Hover/Modals):** Surface: `rgba(255, 255, 255, 0.06)`, Border: `1px solid rgba(255, 255, 255, 0.15)`, Backdrop-blur: `40px`.

Inner glows (top-down) can be used on primary cards to simulate light hitting the edge of the glass. Use a `1px` stroke for all borders to maintain the "terminal" precision.

## Shapes

The design system uses a **Rounded** aesthetic (0.5rem base) to soften the technical nature of fintech data. 

- **Cards:** Use `rounded-lg` (16px) to create a soft, premium container feel.
- **Buttons/Inputs:** Use `rounded-md` (8px) for a focused, interactive appearance.
- **Status Badges:** Use `rounded-full` (9999px) to differentiate them from interactive buttons.
- **Charts:** Line graphs should use a slight bezier curve (interpolation) rather than jagged angles to align with the soft shape language.

## Components

### Navigation Tabs
Tabs are presented as a horizontal list of text labels. The active state is indicated by a primary green underline (2px) and a subtle background glow behind the text.

### Data Cards
Glass-morphic containers with internal padding of 24px. Upon hover, the border opacity should increase from 0.08 to 0.2, and the backdrop-blur should intensify.

### Status Badges
Compact indicators for "High," "Medium," or "Low" risk/growth. Badges use a low-opacity fill of the semantic color (Green, Amber, Red) and high-contrast text of the same color.

### Input Fields
Dark, semi-transparent backgrounds with a 1px border. On focus, the border transitions to the Primary Green with a subtle outer glow. Use `label-md` for floating labels.

### Compact Visualizations
Sparklines and mini-donuts should be integrated directly into cards. Sparklines should use a gradient stroke (e.g., Green to Transparent) to emphasize movement over time.

### Buttons
- **Primary:** Solid #00C853 with black text for maximum prominence.
- **Secondary:** Glass background with a 1px white border (0.2 opacity).
- **Ghost:** No background, primary green text, icon-only or text-only.
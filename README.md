# TrueColorsTweaks 1.0.0

Graphics add-on for **Life is Strange: True Colors** (PC, Steam), for ReShade with add-on support.
Raises the game's lighting, shadow and detail settings beyond what its menu offers, adds Unreal's
own ray-traced effects and HDR output on DirectX 12, live, from an in-game overlay.

- **HDR**: the game's HDR switch only works on DirectX 11, so it can't be combined with ray
  tracing. The HDR tab turns on the engine's HDR10 output directly (1000 or 2000 nits), on
  DirectX 11 or 12. Windows HDR must be on; leave the game's own HDR setting off.
- **Ray tracing** (DirectX 12 launch option): cleaner ray-traced shadows (2 or 4 rays),
  ray-traced reflections, ambient occlusion, bounce light and glass. The game ships its ray
  tracing shaders, so these are Unreal's own effects.
- **Lighting**: screen-space bounce light, GTAO, finer lighting on translucent effects.
- **Shadows**: 4096 / 8192 shadow maps, longer shadow distance, contact-hardening shadows,
  full-resolution character shadows.
- **Characters and detail**: full skin shading, most detailed characters and models, texture
  memory beyond the game's 3 GB, 16x filtering, 8 anti-aliasing samples (Deck Nine lowered them to 4).
- **Post-processing**: film grain, lens flares, depth of field, motion blur, chromatic aberration,
  sharpening.
- **Quality presets**: *Ultra+* (everything that measured nearly free; about 8% slower) and
  *Cinematic* (Ultra+ plus ray-traced reflections and ambient occlusion and 8192 sun shadows;
  about 49% slower). Measured on an RTX 5080 at 4K native in one scene. **Measure preset costs**
  and **Measure each option** check them on your PC.
- **F8** switches every tweak off and on, to compare.

Every option starts at the game's own value, and its tooltip says what the game uses and what the
choice costs. The menu's highest setting already maxes draw distance, fog, screen-space reflections
and anti-aliasing quality, so those aren't offered. Ray-traced sky light isn't offered: it relights
the game's baked lighting and shifts the colours of the whole picture.

## Install

1. Install ReShade 6.8 or later with full add-on support for `Siren-Win64-Shipping.exe`, in
   `LifeIsStrange3\Siren\Binaries\Win64`.
2. Copy `TrueColorsTweaks.addon64` into that folder.
3. For ray tracing and HDR together, start the game with Steam's "Life is Strange: True Colors
   (DirectX 12)" option. Open ReShade (Home key), Add-ons tab, TrueColorsTweaks.

Settings are saved in `ReShade.ini` under `[TrueColorsTweaks]`. Log: `TrueColorsTweaks.log` next to
the game's exe (and `-probe.txt`, every setting's value). Tested with Steam build 8050014.

## Build

`.\build.ps1` (Visual Studio 2022 C++ tools); `.\build.ps1 -Install` copies the add-on into the game
folder (game closed).

## How it works

Everything goes through the game's console variables, set on the game thread (from the console
manager's once-per-frame sinks call), at console priority; letting go puts the game's value and
priority back. `docs/FINDINGS.md` has the UE 4.25 layout, the game's values, the measured costs and
the HDR finding.

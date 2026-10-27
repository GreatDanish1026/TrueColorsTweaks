# Life is Strange: True Colors: findings

Game: Life is Strange: True Colors (Deck Nine), Steam app 936790, build 8050014. Unreal Engine
**4.25Plus** (`++UE4+Release-4.25Plus`), project `Siren`.

Paths:
- Game: `E:\SteamLibrary\steamapps\common\LifeIsStrange3`
- Executable: `Siren\Binaries\Win64\Siren-Win64-Shipping.exe` (78 MB, PE timestamp `0x61e748ff`);
  `LifeIsStrange3.exe` in the root is the launcher stub.
- User config: `%LOCALAPPDATA%\Siren\Saved\Config\WindowsNoEditor\` (Engine.ini, GameUserSettings.ini).
  Shipping build: no log files in `Saved\Logs`.
- ReShade 6.8.0.2152 (add-on build) `dxgi.dll` in the exe folder (installed by the user 2026-10-27).

## Executable and renderer

- **Not protected**: normal `.text` / `.rdata` / `.data` sections, so static analysis works.
- RHIs: D3D11 (default), D3D12 and Vulkan compiled in. Steam has a second launch entry,
  "Life is Strange: True Colors (DirectX 12)", which passes `-dx12`.
- `Siren/Config/DefaultEngine.ini` (pak v9, unencrypted index, zlib; `tools/pak9.py` reads it)
  ships `r.RayTracing=1`, `r.RayTracing.Shadows=1`, AO and reflections 0,
  `r.SkinCache.CompileShaders=True`, `r.DefaultFeature.AntiAliasing=2` (TAA),
  `r.SSS.Checkerboard=1` ("fix for SIR-13450"), `r.HDR.UI.CompositeMode=0`.
  So the ray tracing shaders are cooked: on DirectX 12, Unreal's other ray-traced effects can be
  switched on by cvar, and no "test r.RayTracing on the next launch" step is needed (unlike
  Double Exposure and Reunion, where the RT shaders weren't shipped).
- The settings menu checks the command line for `d3d12`/`dx12` next to `r.RayTracing.Shadows`:
  ray-traced shadows are a DirectX 12 menu option.
- No DLSS, NGX, Streamline, FSR or XeSS. Upscaling is UE4's TAA (`r.TemporalAA.Upsampling`,
  TAAU), not TSR.

## HDR

The game's HDR switch only works on DirectX 11 (Deck Nine's support answer quoted on Steam:
HDR was fixed on DX11 only, so players choose between HDR and ray tracing). On DirectX 12 the
game leaves `r.HDR.EnableHDROutput` 0 (set by GameSetting priority 0x02 in the probe) and the
swap chain sRGB.

The engine itself handles HDR on DirectX 12: the back buffer is already `R10G10B10A2_UNORM`
(ResizeBuffers format 24, flags 0x802), and setting `r.HDR.EnableHDROutput=1`,
`r.HDR.Display.OutputDevice=3` (ACES 1000-nit ST-2084) or 4 (2000-nit), `r.HDR.Display.ColorGamut=2`
(Rec. 2020) on the game thread makes the engine resize the swap chain and switch it to HDR10 PQ
within about 80 ms (log 2026-10-27 12:14:20). The add-on's own SetColorSpace1 fallback wasn't
needed. Visual verdict from the user: pending.

## Console variables

From the exe's code (`tools`-free byte scans; scratch scripts in the session notes):
- `IConsoleManager::Singleton` RVA **0x492a1f0** (4 of 4 matches next to `L"r.ScreenPercentage"`).
- IConsoleManager: `+0x50` CallAllConsoleVariableSinks (6 call sites; RVA 0xfe7ae0), `+0x58`
  RegisterConsoleVariableSink, `+0xb0` FindConsoleVariable (3362 call sites).
- IConsoleObject: IsVariableBool at `+0x30` (found at run time), AsVariableInt/Float `+0x58/+0x60`;
  data cvars keep `TConsoleVariableData` at `+0x38`.
- IConsoleVariable: Set `+0x80`, GetBool `+0x88` (result tested with `test al`), GetInt `+0x90`
  (`test eax`), GetFloat `+0x98` (xmm0), GetString `+0xa0`. Same as UE 4.26/4.27.
- SetBy priorities passed to Set: 0x08000000 (code, 49 sites), 0x09000000 (console, 42 sites):
  the 4.2x enum. The add-on sets at 0x09.

Setting: all Sets run on the game thread from a vtable copy of the console manager whose
CallAllConsoleVariableSinks slot runs the add-on first (FrankStoneTweaks' design). In UE 4 a Set
off the game thread doesn't reach the renderer, and some change callbacks flush rendering (Jedi
Survivor hung on r.MaxAnisotropy). The game thread never holds the overlay's lock while it sets
anything (a callback can wait for the render thread, which may be presenting). First run
2026-10-27: layout check passed, Ultra+ applied 17 values, F8 off/on restored all of them.

## The game's values (probe 2026-10-27, menu at its highest everywhere: sg.* = 4)

| Setting | Game | Notes |
|---|---|---|
| r.ViewDistanceScale | 10 | Cinematic; no draw distance option needed |
| r.Shadow.MaxResolution / MaxCSMResolution | 2048 / 2048 | |
| r.Shadow.RadiusThreshold | 0 | every object casts shadows already |
| r.Shadow.DistanceScale | 1 | |
| r.Shadow.CSM.MaxCascades | 10 | |
| r.SSR.Quality | 4 | Cinematic already |
| r.SSGI.Enable / Quality | 0 / 4 | |
| r.VolumetricFog.GridPixelSize / HistoryMiss | 4 / 16 | Cinematic already |
| r.PostProcessAAQuality | 6 | |
| r.TemporalAASamples | 4 (code, 0x08) | Unreal's default is 8 |
| r.TemporalAA.Upsampling | 0 | screen percentage 100 |
| r.Tonemapper.Sharpen | 0.5 (code) | |
| r.Streaming.PoolSize | 3000 | |
| r.MaxAnisotropy | 8 | |
| r.SSS.Checkerboard | 1 (SystemSettingsIni 0x04) | |
| r.TranslucencyLightingVolumeDim | 64 | |
| r.RayTracing.Shadow.SamplesPerPixel | 1 | DX12: ~100 DispatchRays per second with RT shadows |
| r.RayTracing.Reflections / AO | 0 / 0 (ProjectSetting 0x03) | GI, translucency, sky light -1 (post-process volume) |
| D9.HDR.UI.Brightness / Desaturate | 1.4 / 0.5 | |

## Costs (Measure each option, 2026-10-27, RTX 5080, 3840x2160 native, DirectX 12, one scene)

Game 9.90 ms (101 fps) at the start and 9.89 ms at the end.

| Option | Frame time |
|---|---|
| Screen-space bounce light (SSGI) | +83% |
| RT bounce light, brute force | +63% |
| RT sky light | +48% (and a colour shift over the whole picture: removed in 0.2.1) |
| RT bounce light, final gather | +43% |
| RT reflections High / On | +28% / +26% |
| RT ambient occlusion 2 rays / On | +7% / +4% |
| 8192 sun shadows | +4% |
| RT glass (translucency) | +3% (scene without much glass) |
| Contact-hardening shadows (PCSS) | +3% |
| Translucency lighting 128 | +1% |
| everything else (4096 shadows, RT shadows 2/4 rays, TAA 8 samples, GTAO, capsule, skin, character/model detail, textures, 16x, shadow distance) | under 1% (noise: -2.5% to +0.4%) |

Presets as a whole (0.2.0): Game 9.73 ms (102.8 fps), Ultra+ 10.39 ms (96.3 fps, **+7%**),
Cinematic 27.33 ms (36.6 fps, +181%, with SSGI and RT sky light). 0.2.1 rebuilds Cinematic as
Ultra+ plus RT reflections, RT AO and 8192 sun shadows (expected about +40%, to be measured) and
adds 2-ray RT shadows to Ultra+. Measured 0.2.1 (same kind of scene): Game 8.58 ms (117 fps),
Ultra+ 9.27 ms (**+8%**), Cinematic 12.78 ms (78 fps, **+49%**).

## RT sky light shifts the colours

`r.RayTracing.SkyLight=1` visibly shifts the colours of the whole picture (user, 2026-10-27). In
4.25 it relights every surface from the sky light, including ones whose sky lighting is baked
into lightmaps, so the sky is counted twice. The option was removed.

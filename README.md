# monarchy-assets

The art studio for **Monarchy**. This repository holds concepts, editable models, sculpts, materials, rigs, animations, and the tools that turn them into assets engineering can ship. The sibling [`monarchy1`](../monarchy1) repository owns the game runtime and client integration.

Our goal is to conceive, sculpt, rig, and animate every `PieceConf`, one piece at a time. The models currently in `monarchy1/clients/web/public/models` are placeholders. A finished asset must work on the game board, including clients with limited bandwidth or rendering capacity.

For now, keep the studio and runtime repositories separate. Revisit combining them after we have shipped a complete piece and understand the workflow. An explicit export contract will be useful in either arrangement.

## Where we are starting

- `ideas/`: existing concept images.
- `logos/`: existing logo assets and explorations.
- `src/`: existing editable sources, including `monarchy-logo.ai` and `cleric.blend` (with a `.blend1` backup).
- No repeatable character export, optimization, or release pipeline has been established yet. The structure and conventions below are the proposed starting workflow, not implemented tooling.

The existing Cleric files were untracked when this README was written. Preserve and inspect them before moving or replacing anything; their contents and production readiness have not been reviewed.

## The roster

Use the runtime's [`PieceConf.scala`](../monarchy1/server/src/game/PieceConf.scala) as the gameplay authority, and [`PieceConfStringBijection.scala`](../monarchy1/server/src/marshalling/game/PieceConfStringBijection.scala) for serialized identifiers. Display names differ from code names. Use the serialized ID in handoff metadata so renaming a character does not silently change its identity.

- `ASSASSIN` — Royal Spearman; adjacent area attack.
- `KNIGHT` — Royal Guard; armored melee fighter.
- `SCOUT` — Royal Hunter; ranged, line-of-sight attack.
- `WITCH` — Shadow Bender; directional line attack.
- `PYROMANCER` — Burning Priestess; area attack.
- `MUD_GOLEM` — Gloom Sentinel; teleporting melee unit.
- `FURGON` — Grove Sentinel; grows plants.
- `CLERIC` — High Cleric; heals allies.
- `FROST_GOLEM` — Frost Sentinel; focused paralysis ability.
- `SHRUB` — Banyan; stationary plant summoned through gameplay.

These are gameplay cues, not approved visual designs. Every entry needs an art brief and an explicit animation decision, including Banyan. A plant may need only a growth/reaction animation rather than a walking skeleton. Ability effects, projectiles, and summoned plants should be tracked alongside their owning character, even when shipped as separate assets.

## The pipeline

A practical game-art pipeline separates an editable artistic source from the meshes rendered in real time:

**Brief → concepts → blockout → detailed source → game mesh → UVs and baking → materials → rig and skin → animations → quality variants → export → client review.**

For our first piece, take a simple blockout through export immediately, before spending days sculpting. That catches scale, orientation, material, and animation problems while changes are cheap. Then return to the artistic work.

### 1. Define the piece and its silhouette

Write a short brief: serialized ID, gameplay role, personality, proportions, equipment, colors, required motions, references, and what must read at board-camera distance. Make a few inexpensive sketches or concept images and choose one direction before modeling. Include front and side views where useful; resolve contradictions between views.

Start with stylized forms, broad color areas, and a distinctive silhouette. Tiny sculpted details may disappear on the board. Check the piece in grayscale and beside another silhouette; faction color alone should not identify the unit. AI images or generated meshes can help exploration, but still require art review, rights records, topology cleanup, and an export test.

### 2. Block out, then sculpt as needed

Use Blender primitives and simple meshes to establish proportions, pose, weapon, and footprint. Review from the actual game camera. Save a lightweight export for the first integration test.

Keep the highest-fidelity source editable. Use separate collections for the detailed source and export meshes, and preserve modifiers where practical. Sculpt only the detail that improves the design or can survive baking. A simple stylized character does not need a huge sculpt to be production quality.

### 3. Build the game mesh

Retopology means constructing a cleaner mesh over the sculpt. Place geometry where it preserves the silhouette and where joints bend. A dense sculpt is an artistic source, not the default client download.

Automatic decimation can help rigid props and initial reduced variants. It is not a reliable replacement for deliberate topology around shoulders, elbows, hands, and faces. Inspect the result in motion. Preserve a reviewed game mesh from which lower-detail variants can be derived; do not destructively simplify the master sculpt.

### 4. UV, bake, and color

UVs map the mesh surface onto texture images. Baking transfers surface detail from the detailed source onto textures for the game mesh. Use normal maps when useful; they change lighting detail, not the silhouette. Blender supports [retopology](https://docs.blender.org/manual/en/3.0/modeling/meshes/retopology.html) and [texture baking](https://docs.blender.org/manual/en/latest/render/cycles/baking.html).

Start with a small palette and few materials. Use Principled BSDF materials that export to glTF; bake procedural appearances that cannot travel to the client. Treat base color as sRGB and normal/roughness/metallic data as non-color data. Review under game lighting, not only a studio render.

Give faction-tinted regions a deliberate material such as `team_color`; keep skin, metal, wood, and effects independently authored. Avoid a separate full texture set for every team. Agree with engineering how that material is identified and tinted.

### 5. Rig, skin, and animate

A rig supplies controls and bones; skin weights determine which bones move each vertex. Begin with a small skeleton and test difficult poses before polishing animation. Blender's built-in tools are sufficient to start; Rigify is optional when a humanoid control rig will save work. Reuse a humanoid skeleton only where proportions and motion suit it.

Keep animator controls in the source. Export deform bones and baked motion; constraints and control rigs are not runtime behavior. For lower-detail meshes, transfer weights where useful, then inspect and correct them.

Proposed common clip names are `idle`, `move`, `ability`, `hit`, and `death`. Add `spawn`, `block`, or a focus loop only when the piece needs them. Start with `idle` and `ability` for Cleric. Record clip duration, looping, and the ability's impact time in the asset notes. Use an in-place movement convention initially: the client positions the piece on the board, and animation supplies the performance. Gameplay timing remains authoritative in the runtime.

### 6. Create quality variants

Keep artistic fidelity independent of client quality. Initially produce two separately downloadable variants:

- **Standard:** the reviewed game mesh, textures, rig, and animations.
- **Low:** fewer triangles, smaller textures, and fewer expensive materials, preserving the silhouette and required motion.

Distance-based LOD and download quality solve different problems. Distance LOD can reduce rendering cost but will not save transfer if all levels are bundled and fetched. Let engineering choose a quality package before downloading it. Start with an explicit quality preference and a safe default; adaptive selection and switching can follow measured need. Retain a lightweight fallback for loading or asset failure.

For a first experiment, aim for roughly 5–15k triangles in Standard, 1–3k in Low, one or two material slots, a texture atlas up to 1024 pixels per side in Standard and 256–512 in Low, and no more than four bone influences per vertex. These are provisional studio targets, not proven device budgets. Measure exported geometry, bytes, decoded texture memory, draw calls, skinning cost, and a full board's frame time before setting limits. A low-poly mesh with large textures can still be expensive.

Preserve bone and clip names across variants. Keep the same skeleton initially so integration stays simple; reduce bones later only if profiling justifies the extra contract. Review low-detail deformation, UV seams, and silhouette manually.

### 7. Export and hand off

Use glTF 2.0 binary (`.glb`) as the initial delivery format; the web client already loads GLBs. Keep `.blend` as the editable source. The [Blender glTF exporter documentation](https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html) describes supported materials and animation features. Export a small test in the installed Blender version rather than assuming every Blender feature survives.

Proposed studio convention: Blender units in meters, Z up, character facing -Y, origin at ground center. Export with the normal glTF axis conversion to Y up. Record the resulting facing and test it in the client; use one agreed conversion rather than accumulating per-piece scale and rotation patches. Agree the character's height and tile footprint with engineering using the first blockout. Apply intended transforms before rigging and verify bounds after export.

An engineering handoff should contain:

- Versioned Standard and Low GLBs, plus a preview image.
- A manifest with `pieceConf`, asset version, source commit, Blender/exporter/tool versions and settings, variant filenames and checksums, byte sizes, triangle/material/bone counts, dimensions, origin/facing, team-color material, and clip names/durations/loop and impact timing.
- Rights and attribution records, known limitations, and client review results.

Start with a small human-readable manifest; automate it once the fields have survived a real handoff. Use immutable paths such as `cleric/v001/standard.glb` and `cleric/v001/low.glb`. The runtime should pin a reviewed release and record its studio source commit. Initially, copying a reviewed export into the runtime in a separate PR is sufficient. CDN publication can come later.

**Current integration work:** [`clients/web/src/views/Game/pieces/index.tsx`](../monarchy1/clients/web/src/views/Game/pieces/index.tsx) clones GLB scenes and recolors every mesh material. It does not play animation clips. Production characters will need selective team tinting, skeleton-aware cloning for independent animated instances, clip playback, and quality selection. Loading a rigged GLB alone does not implement those behaviors.

### 8. Review in the client

A beautiful Blender render is a milestone, not acceptance. For each release:

- Validate the GLB with the [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator), and inspect it independently of the source scene.
- Check scale, facing, ground contact, silhouette, colors, lighting, and every clip in the actual client. Test multiple copies with independent animation and team colors.
- Exercise ability timing, looping, interrupted clips, and transitions. Make sure animation does not determine game results.
- Test Standard, Low, and asset failure/loading behavior. Measure cold-download size and full-board rendering on a modest device or a documented constrained test environment.
- Save screenshots, measurements, and any limitations with the release. Approve the asset before replacing a placeholder.

## Organizing the studio

Keep existing files in place until inspected. Add the following structure as the first piece progresses; these directories do not exist yet:

```text
pieces/
  cleric/
    brief.md             # design, gameplay cues, references, approval notes
    concepts/            # selected explorations and source images
    source/              # master .blend and editable texture sources
    textures/            # authored/baked texture inputs
    previews/            # board views and animation reviews
    asset.json           # handoff metadata once its contract is agreed
exports/
  cleric/v001/           # reviewed Standard/Low GLBs and release metadata
shared/                  # reusable palettes, materials, rigs, reference scale
tools/                  # future export, validation, and optimization scripts
```

Use lowercase folder names based on the code identity (`mud_golem`, not the display name); record the uppercase serialized ID in metadata. Keep source textures relative to the Blender file or pack them, so another machine can open the project. Record dependencies and avoid undocumented absolute paths. Treat one piece as one editor's responsibility at a time: binary `.blend` files cannot be meaningfully line-merged.

Use Git for briefs, scripts, metadata, and review history. [Git LFS](https://git-lfs.com/) is configured for `.blend` sources and the Healer/shared-concept raster images via `.gitattributes`. Install Git LFS and run `git lfs install --local` after cloning, then `git lfs pull` to retrieve the binary contents. Existing legacy images and Illustrator sources have not been migrated. Blender autosaves (`.blend1`, etc.), local `healer-before-*.blend` safety copies, and Python caches are ignored; the active `src/healer.blend` includes the preserved historical study collections. Check the host's storage and bandwidth allowance before adding many revisions; retain meaningful milestones and keep disposable renders/caches out of Git. Do not rewrite existing history just to begin. Keep a separate backup of irreplaceable sources; Git/LFS is not the only backup.

Record each external asset's creator, source URL, license, attribution, and permitted uses. Record generation tools and provenance for AI-assisted work too. The repository's MIT license does not grant rights to third-party inputs; preserve their notices and make the intended license for original artwork explicit before distribution.

## Working with very little money

Begin with Blender, its texture painting and animation tools, and hand-authored concepts or an existing image editor. Use local renders and manual GLB exports. No paid generator, commercial sculpting package, asset subscription, render farm, or hosted pipeline is required for the first piece.

Spend effort on silhouette, readable color, and a few good motions. Reuse palettes, base meshes, rigs, and export settings after they prove useful. Avoid cloth/hair simulations and complex shader graphs initially. Borrow properly licensed reference or test assets when they answer a specific question; record their provenance.

Automation should remove repetition we have actually encountered. After the first successful export, add a Blender Python exporter; then metadata/validation checks; then variant generation. [glTF Transform](https://gltf-transform.dev/cli) is a candidate for inspecting and optimizing exports. Mesh and KTX2 texture compression require corresponding client support and tests. Pin tool versions when introducing scripts and compare before/after visuals and metrics; an optimization command is not an art approval. Khronos's [real-time asset guidelines](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md) provide broader production guidance.

## Blender MCP: existing setup and next steps

The local Cursor configuration at `~/.cursor/mcp.json` contains this existing server entry:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

This is a record of the older setup, not a newly installed configuration. The current [upstream project](https://github.com/ahujasid/mcp-for-blender) documents its installation and connection workflow. Use matching server/add-on versions rather than mixing the older configuration with a new add-on without checking compatibility.

A Blender MCP tool connection is available in the current assistant environment, but its status check on November 7, 2026 could not reach Blender. The scene and installed add-on version could not be inspected.

To resume: open Blender, save a working copy of the existing Cleric file, check that the MCP add-on is installed and enabled, and start its connection from its Blender panel following the matching version's instructions. Then ask the assistant to check add-on status and inspect the scene before editing. Avoid running competing MCP sessions against the same scene. Save checkpoints before automated edits. MCP is useful for scene inspection, repetitive setup, exports, and preview checks; it does not replace art decisions or deformation review. Paid generation integrations are optional.

## Start here: finish Cleric before expanding the roster

1. **Recover the workspace.** Inspect `src/cleric.blend`, preserve the original and backup, reconnect MCP, and record the installed Blender/add-on versions. Decide whether the existing model is a useful starting point.
2. **Write the brief.** Create `pieces/cleric/brief.md` with `CLERIC`, the High Cleric's healing role, a few silhouette directions, a proposed palette/team-color region, references and rights, and an initial `idle`/`ability` clip plan. Choose the design before detailed sculpting.
3. **Prove the handoff.** Export a simple Cleric blockout GLB and place it on a local game board. Agree size, footprint, facing, origin, and tinting. Test one simple bone animation to expose exporter/playback issues early. This requires a small runtime integration change; it is not part of the README work.
4. **Complete one small production pass.** Refine or sculpt the selected model, make the game mesh and UVs, create simple materials, rig it, and finish idle and heal motions. Test the rig while working. Defer optional animation polish until the basic loop works.
5. **Make the Low variant.** Reduce geometry and textures, preserve the rig/clip contract, and compare both versions from the board camera. Record actual budgets and adjust the provisional targets.
6. **Release and integrate.** Validate both GLBs, attach provenance and metadata, test independent instances and ability timing in the client, and replace the Cleric placeholder through a reviewed runtime change. Tag or otherwise pin the studio source revision used for that release.
7. **Capture what we learned.** Record export settings, failure cases, time spent, and useful reusable parts. Turn only the repeated steps into tools. Pick the next `PieceConf` and repeat, checking the roster against the runtime as it evolves.

The first success is one recognizable, animated Cleric running correctly in the client at two quality levels, with an editable source and a reproducible handoff. That gives us a tested foundation for the rest of the studio.

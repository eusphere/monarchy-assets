# Healer — angel incarnation

Healer is an order whose spirits can be angels or demons, typically angels. Our first incarnation is angel-flavored: an elite spirit, among the rarest and most expensive summons. Its presence should convey rank, supernatural power, and the weight of being summoned.

This design is being developed in [`../../src/healer.blend`](../../src/healer.blend). Healer is the art direction name here; the runtime currently identifies its healing piece as `CLERIC` (High Cleric). This brief does not rename that gameplay identifier.

## Approved concept — v003

**[Angel Healer v003](concepts/angel-healer-v003.png) is the selected design for further development, with the latest fitting refinements below: clean cloth without soil, slender gloved hands, and a more legible feminine figure beneath the drapery.** This decision supersedes the later mask experiments and the earlier gold-crescent Blender studies.

Carry forward the slender silhouette, layered ivory garments and embroidery, fully concealed face behind a white textile veil, white inverted angular bowed headpiece with tapered descending ends, red blood-stained hands, restrained cloth staining, and soiled hem. No gold face mask, facial openings, jewel, or gold crown. Preserve the nearly approved garment design when developing supporting views.

V004 and v005 are retained as unselected explorations. The current `src/healer.blend` remains an earlier procedural study and does not yet match this approved concept. Next, develop consistent side and rear references from v003, resolve the garment layers and headpiece construction, then rebuild the source model against those references.

## Visual direction

Use abundant, layered cloth with a regal presence. The figure should feel sumptuous and ceremonial rather than austere: sweeping drapery, substantial folds, and a commanding silhouette. Study the imposing headpiece in [`elesh-norn.jpg`](elesh-norn.jpg) for its scale and architectural presence; develop our own shape and ornamentation.

Keep the face hidden. This is a rule for **all Monarchy characters**, not only this incarnation. Veils, layered fabric, a deep hood, or a ceremonial headpiece can conceal it. The mystery must hold from every gameplay camera angle and through animation.

The angelic aspect does not make the character immaculate or innocent. There is darkness in every character. Blood on the hands, scattered flecks on the drapery, wear, and unsettling details can coexist with regal cloth. These are possibilities to explore, not a requirement to cover the whole figure in gore. Preserve clear, readable shapes at board distance.

Healing comes through magic. Hands, posture, cloth movement, and a restrained magical effect can carry the performance; the character needs no healing tools. This incarnation has **no combat abilities, armor, or weapons**. Its status comes through bearing, silhouette, materials, and ritual presence.

## References

- [`elesh-norn.jpg`](elesh-norn.jpg): headpiece scale, ceremonial authority, and the tension between pale surfaces and unsettling red detail. The supplied image credits Igor Kieryluk and Wizards of the Coast. It is a visual reference, not a production texture or a character design to reproduce.
- [`draping.png`](draping.png): enveloping cloth, layered folds, flowing silhouette, and a concealed face. Creator/source have not yet been recorded.
- [`../world-concepts/`](../world-concepts/): shared Monarchy concept art, copied from the existing `eusphere` checkout. Use it to keep this character within the wider world, especially its concealed faces and dark spiritual tone. See that folder's README for provenance.

## First concept pass

Explore a few silhouettes combining a concealed face, a prominent ceremonial headpiece, and generous drapery. Compare front, side, and board-camera views before sculpting detail. A halo or wings are open design questions, not established requirements.

Choose the silhouette first, then settle a small palette, the areas available for team color, and where any blood or wear belongs. Try an unarmed idle pose and an open-handed healing gesture. The cloth and headpiece must remain readable and avoid obscuring neighboring tiles; account for how they will deform before committing to fine folds.

Start with `idle` and a healing `ability` animation. No combat animation is required for this incarnation. Review the face concealment in motion as well as in the resting pose.

## Selected direction: slimmer Vesper

The crescent-headpiece study C (Vesper) is the selected starting point. Refine it toward a slimmer, simpler figure with restrained ornament. Keep the face veil white as well as the surrounding drapery. Avoid the broad shoulder panels and wide bell sleeves of the initial blockout.

Additional references: [`bene-gesserit.jpg`](bene-gesserit.jpg) for the narrow silhouette, layered white cloth, and wrapped hood; [`bene-gesserit2.jpg`](bene-gesserit2.jpg) for ceremonial veiling, small ornaments, and expressive unarmed gestures. Their creator/source records remain to be established. Use these motifs to develop an original design.

The second blockout is saved as collection `C2 - Veiled Vesper` in `healer.blend`, with the original studies preserved but hidden. See [the revision preview](previews/vesper-v002.png). It remains a shape study with approximate hands and cloth, not a rigged or production-ready mesh.

## Material development: retain the darkness

The slimmer white-veiled direction is approved for further development. As materials and detail develop, retain the character's darker aspects: soil and grime at the hem and trailing cloth, traces of blood on the hands, and sparse blood flecks or stains on the drapery. Keep the white cloth legible and the regal silhouette intact. Place marks deliberately, with variation and a sense of history; avoid uniform dirt or an immaculate finish. These details remain to be authored in the model's materials and textures.

## First sculpt pass

`C3 - Vesper sculpt` in `src/healer.blend` develops the slim silhouette with denser shaped cloth folds, a fully opaque white face veil, articulated hand forms, restrained gold, soiled hems, irregular dried blood on the hands, and sparse veil flecks. The previous blockout is preserved in its hidden collection; `src/healer-before-sculpt-v002.blend` is a separate checkpoint.

Review images: [front three-quarter](previews/vesper-sculpt-v003.png) and [rear three-quarter](previews/vesper-sculpt-v003-rear.png). This is an initial sculpt/detail pass, with about 135,000 base vertices across the visible character meshes. Hands, cuff transitions, and cloth layering can receive further art refinement. It is not a finished game mesh: retopology, UV/baking, rigging, animation, and client validation remain. Current procedural weathering materials will need baking for GLB delivery.

## Fidelity pass C4

`C4 - Vesper detailed source` adds varied cloth folds and gathered tension, hem and hood seams, fitted cuffs, finer hand surfaces with finger creases and nails, and restrained crescent detailing with a central garnet and small temple drops. It retains the white veil, slender form, soil, and blood. The collection contains approximately 636,000 base mesh vertices; this is an editable art source, not a client budget.

See [full figure](previews/vesper-detail-v004.png) and [upper-body detail](previews/vesper-detail-v004-close.png). C3 is preserved hidden, with a separate `src/healer-before-detail-v003.blend` checkpoint. The shaping is still an iterative procedural sculpt pass; cloth layering and hand anatomy need continued review. Drapery form is developed now; cloth simulation, animation behavior, baking and shader/runtime optimization are later stages.

## Image-generated concept target

[Angel Healer v001](concepts/angel-healer-v001.png) is a 2D concept generated with the assistant's built-in image generation tool using `bene-gesserit.jpg`, `bene-gesserit2.jpg`, and `draping.png` as visual references. The [complete prompt](concepts/angel-healer-v001-prompt.txt) is saved alongside it. This is a new proposed visual target for review, not an approved design, a 3D asset, or evidence that the current Blender model has this fidelity.

The concept explores a slender white-veiled figure, a small crescent diadem, coherent layered wraps, edge embroidery, expressive unarmed hands, dried blood traces, and a soiled hem. Supporting views and garment construction still need to be resolved before rebuilding the model. Reference provenance limitations above continue to apply.

[Angel Healer v002](concepts/angel-healer-v002.png) revises v001 with a larger crescent crown and more visible dried blood on the hands, preserving the nearly approved clothing. Created with the built-in image editor from v001; [edit prompt](concepts/angel-healer-v002-prompt.txt). The larger crown and revised staining remain subject to review.

## Revised headpiece and blood direction

The gold crescent and jewel are rejected. The current direction is a **white, inverted, angular, tapered, bowed headpiece**, using the architectural form of the Elesh Norn reference at a smaller scale. No jewel. This supersedes the earlier gold/garnet concept notes and the existing Blender ornamentation, which have not yet been rebuilt to match.

Hands should read red from applying pressure while healing a wound, rather than carrying a few decorative flecks. Add blood marks on the white veil for a more unsettling presence while retaining the concealed face and nearly approved clothing.

[Angel Healer v003](concepts/angel-healer-v003.png), edited with the built-in image tool from v002 and the Elesh Norn reference, explores the white inverted headpiece and stronger hand staining. The veil staining remains subtle in this output. See the [edit prompt](concepts/angel-healer-v003-prompt.txt). This revision remains subject to art review; no matching Blender changes were made.

## Gold-mask alternative

[Angel Healer v004 — gold mask](concepts/angel-healer-v004-gold-mask.png) explores the requested final alternative: a heavier white inverted bowed headpiece, and an expressionless aged-gold mask replacing the face veil, with small blood specks. The mask conceals the real face entirely, including the eyes. Clothing, gestures, and stained hands follow v003. The white-veiled v003 remains preserved as the alternate design; this variant has not yet been selected for modeling.

Generated with the built-in image editor from v003 and the [user-supplied gold-mask reference](gold-mask-reference.png); [complete edit prompt](concepts/angel-healer-v004-prompt.txt). The reference was supplied as an image attachment; original creator/source and licensing remain unrecorded. The reference informs aged material and impassive facial planes, rather than its dark costume or crown.

## Featureless-mask refinement

[Angel Healer v005](concepts/angel-healer-v005-featureless-mask.png) refines v004 with a lighter white headpiece and a smooth convex worn-gold mask, with no facial features or eye openings and a few blood specks. This explored a featureless alternative to v004's human facial planes; both mask variants were subsequently passed over in favor of v003. Clothing and red-stained hands remain closely preserved. Generated with the built-in image editor using v004 as the edit target; [complete prompt](concepts/angel-healer-v005-prompt.txt). This variant is not selected; the Blender model has not been updated to match the approved v003 concept.

## V003 supporting views and construction

Generated using the built-in image tool with approved v003 as the reference:

- [Left-side view](concepts/angel-healer-v003-side.png), with [prompt](concepts/angel-healer-v003-side-prompt.txt).
- [Rear view](concepts/angel-healer-v003-rear.png), with [prompt](concepts/angel-healer-v003-rear-prompt.txt).

These are proposed interpretations of previously unseen surfaces, not exact orthographic projections or additional approved designs. The side view has some three-quarter drift; embroidery, fold placement, and headpiece depth differ between images. Keep the original front v003 authoritative, and reconcile these differences in the 3D construction rather than copying every generated feature.

Proposed separate garment components for the rebuild:

1. Slender underlying body and fitted long-sleeved gown, providing shoulders, elbows, wrists and a collision surface.
2. Asymmetrical torso/shoulder wrap with broad gravity-driven folds and clear attachment points.
3. Outer hood mantle down the back, with embroidered borders and a modest trailing hem.
4. Opaque face veil, distinct from the outer hood; no face or eyes should become visible from the side.
5. Hanging sleeve/drape layers over the fitted sleeves, preserving space for hand gestures.
6. White transverse bowed headpiece: a shallow front-to-back plate over the hood, angular central arch, descending tapered sides. The side image's pointed top is not a mandate for an extra fin or crest.

Preserve the right raised hand and left open lowered hand across views. Build actual garment surfaces and an anatomical foundation before adding embroidery or increasing mesh density. The supporting references do not update `healer.blend`; its current procedural studies remain historical work.

## V003 Blender reconstruction — construction pass

The active `V003 - garment construction` collection now replaces the old experiments for ongoing modeling. It contains a new white inverted bowed headpiece, separate opaque face veil, continuous open-front hood/mantle, foundation gown, shoulder wrap, bias-cut overskirt panel, fitted arm sleeves and hanging outer sleeves. Approved front and proposed side/rear images are packed into a hidden reference collection. A separate hidden body-fitting scaffold establishes approximate proportions; it is not a finished anatomical sculpt. Existing hands are reused temporarily and need replacement/refinement.

The earlier work is preserved hidden, with `src/healer-before-v003-rebuild.blend` as a separate checkpoint. See [construction front](previews/v003-rebuild-construction.png) and [construction side](previews/v003-rebuild-side.png).

A 24-frame shoulder-wrap cloth simulation was tested against the fitting surfaces. It produced dense compression wrinkles rather than the broad supported folds in the concept, so that result was rejected and preserved hidden; the fitting pattern remains visible. This demonstrates that simulation alone does not solve garment design. The wrap cut, attachment points, sleeve integration and hood/veil layering still need deliberate fitting. Other garments have not been simulated. No claim of concept fidelity or production readiness is made for this construction stage. Embroidery, material baking, retopology, rigging and animation remain pending.

## Fitting review 02 — November 8, 2026

The active working collection is `V003 - fitting 02`. Its predecessor remains hidden, with `src/healer-before-fit02.blend` as a separate checkpoint. [Front review](previews/v003-fitting02-front.png) and [profile review](previews/v003-fitting02-side.png) show the current construction without concept-art overlays.

Changes retained in this pass:

- A continuous shoulder cowl replaces the rigid initial wrap; a second correction reduces its inflated silhouette and depth.
- Continuous shoulder-to-cuff sleeves replace disconnected arm tubes. The right healing hand is raised closer to the reference, and the left palm faces upward.
- Outer sleeve drapes replace the original open pipe-like shells, and the upper veil extends beneath the headpiece to cover the earlier gap.
- The overskirt has a diagonal upper edge and an initial fan of folds. Hand staining is stronger; hand anatomy is still inherited from the earlier study.

Review findings: the arm gesture and upper-body continuity are closer to the concept. The cowl still reads too much like a molded collar; the skirt and mantle are too straight and the folds remain too regular. The current headpiece has excessive front-to-back depth in profile. Shoulder joins, fabric layering, hand anatomy and the hem/train remain unresolved. This is not a finished sculpt or a cloth simulation result, and the procedural fitting method has not yet achieved the approved image's garment quality.

Continue by fitting actual supported garment panels and correcting their primary folds, checking front/profile/rear silhouettes before refining each layer. Use this order: shoulder wrap and hood integration; waist gathers and overskirt; mantle and train; hands and cuffs; headpiece depth; then embroidery and material detail. Keep v003 authoritative, preserve checkpoints before each fitting change, and reject results that merely add density or wrinkles without improving the construction. Retopology, baking, animation and runtime optimization follow art acceptance.


## Fitting review 03 — clean cloth and slender gloves

The active collection is `V003 - fitting 03 gloved`. The latest direction supersedes earlier dirt/soiling notes: use clean ivory cloth, including the hem. Blood remains an intentional separate design detail, carried here as palm/finger staining on the gloves rather than general grime. The approved v003 images have not been edited to reflect these refinements.

The earlier thick bare-hand studies are replaced with newly constructed slender opaque ivory gloves, tapered fingers, opposing thumbs, and clean fitted wrists. The open hand was corrected after review so its fingers extend away from the sleeve and its palm faces upward. Foundation-gown tailoring now describes a modest covered bust, narrower waist, and fuller hips; mantle edges and the overskirt narrow at the waist to let the figure read beneath the cloth. This remains a construction-stage interpretation, not final anatomical or garment approval.

See [front](previews/v003-fitting03-front.png) and [profile](previews/v003-fitting03-side.png). Previous work is preserved hidden, with `src/healer-before-fit03.blend` as a separate checkpoint. All visible garment materials in this collection use new clean shaders; the historical weathered materials remain only with previous studies. Finer glove articulation/cuff fitting, garment folds and the headpiece profile still need refinement before production work.

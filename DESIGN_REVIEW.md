# Design review: Python migration

**Status:** review only; no application code or dependencies were changed.  
**Scope:** challenge the migration decisions in [MIGRATION_ANALYSIS.md](MIGRATION_ANALYSIS.md) and [MIGRATION_PLAN.md](MIGRATION_PLAN.md) against the original preview-only tool and the current Python implementation.

## Executive recommendation

Keep Dear ImGui Bundle for the current migration, but qualify the decision: it is a good fit for preserving the original docked desktop workflow, not an objectively best choice for every future version. The current three-pane UI is small enough that Tkinter could cover the basic controls and image display more simply, while Qt would be a stronger choice if the product grows into a polished, accessible, native-feeling desktop editor. A web UI would be a different product direction rather than a like-for-like replacement.

Preserve the current GUI-independent `Session`/imaging boundary and the behavior quirks that are part of parity. Simplify around packaging and maintenance, not by consolidating model, rendering, and GUI responsibilities. The strongest existing regression oracle is the unchanged Lua implementation: the tests already execute it directly, including seeded randomized geometry cases. Build on that differential approach rather than generating expected results from the Python implementation itself.

## 1. Is Dear ImGui actually the best UI choice?

“Best” depends on which goal is primary. The migration prioritizes a docked, immediately interactive preview utility and practical parity with the original LÖVE/ImGui application.

| Option | Advantages for this application | Costs and reasons not to switch now |
| --- | --- | --- |
| **Dear ImGui Bundle (current)** | Closest conceptual match to the original; dockable panes; compact immediate-mode UI; Hello ImGui owns the window/render loop; bundled cross-platform dialog bindings; existing GUI and real-window smoke tests exercise it. | Rendering is GPU/display dependent; controls and docking are less native and accessibility-oriented than conventional desktop widgets; Linux chooser availability depends on Zenity/KDialog; wheel/click integration and texture lifetime need custom care. Its native bundle is a significant runtime dependency for a small utility. |
| **Tkinter** | Ships with many standard Python distributions; native file chooser; simple controls and event loop; can display Pillow images on a canvas; lowers the GPU/OpenGL requirement. | Availability is not universal in minimal/system Python builds; lacks equivalent dockable panes without extra work; image scaling/canvas updates and high-DPI behavior still need care. It would be a simpler but visibly different UI, not a drop-in parity improvement. |
| **Qt (PySide6)** | Mature desktop widgets, image/canvas support, accessibility and DPI tooling, native dialogs, and richer paths to a full editor. | Much larger dependency and deployment footprint; more framework surface and packaging complexity; dock widgets are feasible but introduce a new UI architecture. Best justified by a broader product roadmap, not by the current three panes alone. |
| **Browser/local web UI** | Broad reach, responsive layout, easy visual iteration and potentially easy remote/headless clients. | Requires a server/browser interaction model and new input, file-access, lifecycle, and packaging decisions. Does not naturally preserve native chooser, desktop dock, and global wheel behavior. This is a product redesign. |

**Conclusion:** Dear ImGui is a defensible *parity-first* choice, and changing it now would add migration risk without improving the core slicing behavior. It is not the least-dependency option, the most accessible option, or the strongest long-term editor framework. Revisit only if the product goal changes (for example, no-GPU operation, native accessibility, or substantial editing/export workflows). Before claiming broad portability, keep the platform qualification in [VALIDATION.md](VALIDATION.md): Linux desktop runs were exercised locally; Windows native desktop acceptance remains outstanding; macOS is unvalidated.

## 2. Can functionality or structure be simplified without changing behavior?

The original behavior is narrow: load one sheet, adjust a grid, preview frozen slices, build a sequence through repeated double-clicks, and play it. There is no export, project persistence, or later “open another sheet” flow. The migration should resist adding abstractions for those absent features.

### Safe simplifications to consider

- **Keep the present three-layer split.** The GUI-independent model, Pillow imaging, and desktop shell are already a small, testable architecture. The direct `Session` model is simpler than adding a formal state-machine framework for only edit/sliced modes.
- **Treat repeated Lua comparisons as one differential test harness.** Common setup and conversion of Lua values can be factored into small test helpers, while assertions remain near each behavior. Do not hide which original function is the oracle.
- **Centralize only stable invariants.** Shared validation for image/canvas dimensions and a clear texture-cache key policy can reduce duplicated reasoning. Avoid a general plugin/render-backend abstraction until a second backend exists.
- **Keep expensive rendering event-driven.** The app already caches sheet and preview textures by keys. Preserve invalidation on parameter, slice, frame, and zoom changes; changing the immediate-mode UI does not require rendering every source pixel anew each frame.
- **Keep safety limits explicit.** Region and allocation limits are intentional hardening, not behavior to silently remove. They should remain documented and tested.

### Not safe to “clean up” during a parity pass

Do not normalize the inclusive multi-hit selection, duplicate IDs, strict `timer > interval`, one-step advancement, global wheel zoom, frozen source/live placement split, or the live X/Y field mutation after Slice. Those are surprising but observable compatibility behavior, recorded in [MIGRATION_ANALYSIS.md](MIGRATION_ANALYSIS.md). Removing them would be a behavior change and should require a separate redesign decision and tests.

The clearest simplification opportunity is process rather than runtime behavior: stop expanding migration scope, retain the current narrow model, and avoid parallel “clean” implementations of the same rules. No substantial behavior-preserving rewrite of the current application is warranted by this review.

## 3. Can the Python architecture be more portable?

The architecture is already meaningfully portable at its core: `model.py` is GUI-independent, Pillow owns pixel operations, and the original Windows DLLs are not loaded by Python. The present platform limitations mostly come from the desktop shell and its native dependencies, rather than from the model.

Recommended portability improvements, in priority order:

1. **Separate core and desktop install requirements.** Pillow/model use does not intrinsically require Dear ImGui Bundle or NumPy. Consider a `gui` optional dependency extra and make the GUI entry point report a clear install hint when that extra is absent. Preserve the existing all-in-one install instructions if ease of use for the primary desktop audience is more important. This changes packaging, not slicing behavior.
2. **Make file selection a replaceable boundary.** Keep loading and suffix validation in the core; isolate chooser behavior behind a small interface. This would allow a future Tk chooser, CLI-only test setup, or platform fallback without changing model/imaging code. Do not add a fallback toolkit until its maintenance and user experience are justified.
3. **State platform support precisely.** The project supports tested Windows/Linux Python environments only to the extent actually exercised. Native-dialog utilities, graphics drivers, Python wheels, and DPI behavior vary by platform. Keep macOS explicitly best-effort until tested, and complete real Windows acceptance before calling it validated.
4. **Revisit the Python floor only with dependency evidence.** Python 3.12+ is the stated and tested baseline. Lowering it could broaden adoption, but only after checking the required Dear ImGui Bundle wheels and every selected dependency on the target versions and adding those versions to CI. Do not lower it based on the GUI-independent model alone.
5. **Keep the GUI boundary thin.** NumPy currently bridges Pillow RGBA buffers to the GPU texture API. Avoid introducing a second graphics abstraction or platform-specific code in the model; if a future backend removes NumPy, measure that as a packaging tradeoff rather than preemptively maintaining two upload paths.

A fully portable, no-GPU application is not achievable by packaging changes alone while retaining the current Dear ImGui renderer. If that becomes a requirement, evaluate a different UI backend (Tkinter or Qt) explicitly, then compare interaction behavior and acceptance tests rather than trying to make the current native renderer pretend to be headless.

## 4. Can automated regression tests be generated from the existing implementation?

Yes—and the current suite already demonstrates the highest-value form of this idea. [tests/test_model.py](tests/test_model.py) compares geometry, animation, and state behavior against the unchanged Lua source via LuaJIT; its seeded 250-case geometry loop generates differential inputs. [tests/test_imaging.py](tests/test_imaging.py) exercises the original Lua draw functions through a software adapter and compares the resulting in-memory pixels. The rest of the suite covers image decoding, dialogs, UI field quirks, and an opt-in real GUI workflow. [VALIDATION.md](VALIDATION.md) records the current 42-test run and its limits.

The Lua source is a stronger oracle than manually transcribing expected output, but generated tests still need guardrails:

- **Pin the oracle.** Keep the baseline Lua unchanged as documented, and record or verify its baseline revision/hash in the differential test setup. If both implementations change together, a comparison can otherwise bless a regression.
- **Generate bounded, relevant inputs.** Expand seeded geometry and timer input ranges carefully; generate negative offsets/padding and edge/shared-boundary cases, but bound dimensions and counts to avoid accidental resource-heavy tests.
- **Use property-based generation as an optional enhancement.** Hypothesis can find and shrink counterexamples for geometry, hit tests, and timer transitions. Retain deterministic seeds or checked-in minimized failures so CI reproduces them. It is not necessary to replace the current deterministic randomized test with a new dependency immediately.
- **Keep explicit examples for semantics.** Strict timer boundary, exactly one advance after a long `dt`, repeated IDs, all-hit shared edges, frozen/live mutation, empty sequences, and Cancel should remain named tests. Random generation alone makes failures harder to diagnose.
- **Treat rendering comparisons as software parity only.** The adapter tests draw calls and pixel operations, not original LÖVE GPU rasterization, font rendering, or Windows driver output. Preserve that qualification; add actual engine screenshots only if an executable baseline becomes available and reproducible.
- **Continue testing intentional differences separately.** Safety rejections and recoverable decode errors are migration policy, not Lua parity. Their tests should assert the intended Python behavior rather than expect Lua to agree.

**Recommendation:** improve the current differential suite incrementally: add generated edge cases for imaging/live geometry and broader timer sequences; capture any shrunk failures as fixed regression examples. The original implementation cannot automatically supply trustworthy UI pixel goldens for GPU-specific details, and there is no exported-output corpus to generate; use explicit manual acceptance for those boundaries.

## Decision before continuing

Proceed with the current UI and architecture for the parity-focused migration. Do not modify the application as part of this review. A follow-up implementation phase may address packaging isolation and expand differential/property-based tests, each as a separately scoped change. Reopen the UI decision only when the target requirements prioritize accessibility/native widgets, no-GPU operation, or substantial new editor functionality over fidelity to the existing docked workflow.

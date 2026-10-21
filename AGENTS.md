# AGENTS.md — distro-omarchy

The **Omarchy image family** — charly's `box/omarchy`. It OWNS the Omarchy
base/builder stack, the streamed cstream desktop, the pacstrap/bootstrap path, and
the migration/suite test fixtures, discovered from `box/` and `candy/`. It imports
`opencharly/distro-arch` under the `arch` namespace; every shared candy is an
`@github.com/opencharly/<layer-*|pod-*|plugin-*>[:subdir]:<tag>` ref. Omarchy is
Arch-derived via the `distro: [omarchy, arch]` tag chain, so no candy needs an
`omarchy:` section unless a package *name* genuinely differs from Arch's.

Canonical files:

- `charly.yml` — the root manifest: the `arch` namespace import, the `discover:`
  tree, the `kind: jetkvm` installer device, and the inline VM and check-bed
  entities. It carries NO `skill:` node — every skill is owned by a candy.
- `candy/omarchy-skills/charly.yml` — the `omarchy-skills` bundle candy AND the
  three `skill:` routing entities (`omarchy`, `omarchy-cstream`, `omarchy-vm`),
  each with `owner: omarchy-skills`. `omarchy`/`omarchy-cstream` were owned by
  IMAGES, which the ruling forbids (opencharly/sdk#434): an image is a `candy:`
  node carrying `base:`/`from:`, so it has no source directory, its skill's prose
  can never be read and the node never reaches the `ai.opencharly.skill` label.
  `omarchy-vm` was owned by the `kind: vm` entity `omarchy-vm`, which has no
  source directory either, and no candy owns that VM's payload (the skill spans
  `omarchy-vm`, `omarchy-pacstrap-vm` and the `charly-omarchy` keeper), so the
  bundle owns it too. The candy is composed into both images that carry one of
  these skills, and all three bodies live beside it under
  `.agents/skills/<name>/SKILL.md`.
- `box/<name>/charly.yml` — one manifest per box (and nested fixture candies).
- `candy/<name>/charly.yml` — the Omarchy-exclusive candy layers.
- `scripts/omarchy-rollup.py` — the upstream-release rollup helper.
- `.github/workflows/tag-on-merge.yml` — CalVer tag + `CHANGELOG/` on merge.
- `README.md` — user overview only; never agent guidance.

## Load these skills first (R0)

- `/charly-distros:omarchy` — the Omarchy base image and its package sources.
- `/charly-distros:omarchy-cstream` — the streamed Omarchy desktop (Hyprland via
  cstream); `/charly-distros:omarchy-shell` and `/charly-distros:omarchy-base`
  for the shell and foundation layers.
- `/charly-vm:omarchy-vm` — the Omarchy VMs and their check beds.
- `/charly-image:image` + `/charly-image:layer` — composition and candy
  authoring (`charly.yml` schema, `plan:` step verbs, service declarations).
- `/charly-check:check` — the disposable check beds and `plan:` authoring.
- `/charly-check:jetkvm` — the `jetkvm:` check verb driving the console-installer
  device.

## Build / validate / test

- The merge gate is the **org-wide** `charly/pr-validator` (required check
  `validate / validate`, defined in `opencharly/.github`); this repo has **no
  per-repo candy gate** and ships only `.github/workflows/tag-on-merge.yml`.
- The functional evidence is the disposable check beds (`check-omarchy-pod`,
  `check-omarchy-vm`, `check-omarchy-cstream-pod`, …) and the `plan:` `check:`
  steps on every box. A docs-only change runs no runtime bed — the
  documentation-only change class runs the non-runtime standards only.

## Modify this repo

- Edit the box manifest under `box/<name>/charly.yml`, the skill's routing node
  in its OWNING candy's `charly.yml`, and the skill's body under that candy's
  `.agents/skills/<name>/` together — the body is the projected usage source, so
  a change not mirrored in it leaves the corpus stale.
- Keep Omarchy Arch-derived: add an `omarchy:` package arm only where a package
  name genuinely differs from Arch's; otherwise the `distro: arch:` arm applies.
- charly vendors no Omarchy configuration — do not add a `config/hypr/*.lua` or
  `themes/` copy; those live in `layer-omarchy-base`.
- New behaviour claims belong in a `plan:` as an observable `check:` step, and
  in the owning skill.

## Landing

- PR-only. Every change lands through a pull request; the org-required
  `charly/pr-validator` validates the diff and body and arms native auto-merge
  on PASS. Direct pushes to `main` are blocked.
- History lives in `CHANGELOG/` (written by `tag-on-merge` at merge time); the
  PR body IS the changelog.
- The authoritative rulebook is the umbrella `AGENTS.md` in
  `opencharly/opencharly` and `charly/AGENTS.md` in the charly repo. Do not
  restate its rules here.

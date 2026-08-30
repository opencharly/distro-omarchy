# distro-omarchy

The Omarchy image family — charly's `box/omarchy`.

[Omarchy](https://github.com/omacom/omarchy) is DHH's opinionated Linux distribution:
vanilla Arch + Hyprland, with its own package repository **and** its own pinned snapshot
of the Arch repositories.

## Boxes

| Box | Base | Role |
|---|---|---|
| `omarchy` | `arch.arch` | The canonical Omarchy base image, and the pod-safe floor |

## Building

```bash
charly -C box/omarchy box build omarchy      # from the charly superproject
charly --repo opencharly/distro-omarchy box build omarchy
charly box build omarchy                     # from inside this repo
```

Disposable R10 bed:

```bash
charly check run check-omarchy-pod
```

## How this repo stays small

**Arch-derived, via the tag chain.** Every box carries `distro: [omarchy, arch]`, so an
`omarchy:` package section wins where one exists and all 99 existing `distro: arch:`
candy sections apply unchanged everywhere else. No candy needs an `omarchy:` section; one
is added only where a package *name* genuinely differs from Arch's. This is the mechanism
`distro-cachyos` uses, and it is why this repo vendors almost nothing.

**charly vendors no Omarchy configuration.** The `omarchy` and `omarchy-settings`
packages ship `/usr/share/omarchy/{bin,shell,themes,default,install,migrations}` and all
of `/etc/skel`. There is no copy of `config/hypr/*.lua`, no `themes/` tree and no
`default/themed/*.tpl` anywhere in the org. The package sources, the runtime and the
`/etc/skel` seeding all live in
[`layer-omarchy-base`](https://github.com/opencharly/layer-omarchy-base).

## Why the base is `arch.arch`, not an Omarchy image

Omarchy publishes no container image — only an installer ISO. What makes this image
Omarchy is the package set and the sources it comes from, not a vendor base layer.

charly does **not** run Omarchy's own installer either. In 4.x there is no `install.sh`
at the repo root at all: `install/` is the machinery the ISO runs, and the ISO is the
install path. charly composes the same four packages the ISO installs (`omarchy`,
`omarchy-settings`, `omarchy-keyring`, `omarchy-nvim`) from the same repositories.

All 148 base packages resolve with **plain pacman** — 23 from `[omarchy]`, 125 from
`core`/`extra`/`multilib` served by Omarchy's own mirror snapshot — which is why the base
box is `build: [pac]` with **no AUR builder**.

## The boot stack is installed but inert

The `omarchy` package hard-depends on `limine`, `limine-mkinitcpio-hook`,
`limine-snapper-sync`, `snapper` and `sddm`, so a container gets the whole boot/display
stack whether it wants it or not. `layer-omarchy-base` keeps the limine alpm hooks a
container cannot satisfy off the image entirely, via pacman `NoExtract`, and no unit is
ever enabled.

Machine-only surfaces — limine on a real ESP, snapper subvolumes, plymouth in an
initramfs, an sddm seat, uwsm's systemd user manager, ufw's netfilter tables, dockerd,
dkms — belong to the machine images, not to this pod-safe base.

## x86_64 only

`pkgs.omarchy.org` publishes no `aarch64` tree, so every box pins
`platform: [linux/amd64]` and there is no `archarm` sibling.

## Landing changes

PR-only, via a `feat/` branch. The org-wide `charly/pr-validator` gates the PR and, on
PASS, its auto-merge companion squash-merges and `tag-on-merge` mints the CalVer tag.
Never push to `main`.

## License

MIT — see [LICENSE](LICENSE).

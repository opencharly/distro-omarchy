# Upstream test triage — what `omacom/omarchy@quattro` tests, and what charly asserts

This table exists so the split between "ported" and "not ported" is **reviewable**, not
asserted. Every count comes from greps over the upstream suite and a cross-reference
against the assertion targets actually present in this repo's `charly.yml`, so the
classification can be re-run and disputed rather than taken on trust.

## Method

Upstream suite measured at `omacom/omarchy@quattro`, `test/` — **224** entries in
`test/shell.d` (the plan that opened this work said 220; upstream moved).

Each file is classified by what it can observe, using signals in the file itself:

| Signal | Class |
|---|---|
| `run_node_test` / `requireFromRoot` | **C** — Node/QML unit test over upstream's source |
| `python3` / `import ast` | **C** — Python scanner over upstream's source |
| reads `$ROOT`, names no system surface | **C** — source-level |
| names `/etc/…`, `hyprctl`, `pacman`, `systemctl`, `nmcli`, `limine`, `snapper`, … | **B candidate** — the behaviour under test leaves an observable trace on an installed machine |

**Class C is out of scope, and the live-VM rule is not the only reason.** These tests read
`$ROOT` — omarchy's git checkout. `/usr/share/omarchy/` ships
`applications bin config default etc-overrides install migrations shell themes version`
and **no `test/`**, so running them at all would mean cloning upstream's source into the
guest. Re-implementing them in charly verbs would also duplicate upstream's own tests (R3)
and rot on every upstream release.

**Class B is not "port the test" — it is "assert the consequence".** Upstream mocks a
binary and asserts a call sequence; charly asserts the resulting system state, which is
strictly stronger: it proves the machine, not the call.

## Result

| Class | Count |
|---|---|
| C — Node/QML unit tests | 39 |
| C — Python source scanners | 13 |
| C — other source-level | 89 |
| **B — candidates** | **82** |

The 82 candidates were cross-referenced against the **43** distinct assertion targets this
repo's beds already carry (`file:`, `package:`, `service:`, `mount:` subjects extracted
from every deploy's plan):

| Outcome | Count | Basis |
|---|---|---|
| already covered | **4** | the test names an exact path a bed already asserts |
| gap, mechanically decidable | **21** | the test names only paths, none of which any bed asserts |
| **needs per-file judgement** | **57** | the test names a *command* surface (`hyprctl`, `pacman`, `systemctl`, `nmcli`…), which no automatic rule can match to a bed assertion |

### A rejected first cut, recorded so it is not repeated

The first pass matched bed targets to test signals by substring and reported **52 covered
/ 30 gaps**. That was wrong. The bed's target list contains `/` (a `mount:` subject), and
`/` is a substring of every path signal, so almost everything matched. Short name targets
(`charly`, `omarchy`, `snapper`, `limine`) matched unrelated tests the same way. The
numbers above use exact path equality, and command-only signals are reported as
**undecided** rather than guessed in either direction.

## Already covered — no work needed

- `cups-hardening-test.sh` — `/etc/cups/cups-browsed.conf,/etc/cups/cups-files.conf,/etc/systemd/system/cups-browsed.service.d/10-omarchy.conf,/etc/sysusers.d/omarchy-cups-browsed.conf`
- `snapper-test.sh` — `/etc/conf.d/snapper,/etc/limine-entry-tool.d/omarchy-defaults.conf,/etc/snapper/configs/root,/etc/snapper/config-templates/omarchy`
- `theme-staging-test.sh` — `/etc/hostname`
- `upgrade-to-quattro-test.sh` — `/etc/.,/etc/chromium/policies/managed,/etc/default/limine,/etc/kernel/cmdline`
## Gaps — mechanically decidable (21)

These name only filesystem paths, and no bed asserts any of them. Each is a candidate for
plan unit **U5**; the verdict per row is made when the assertion is written, since "no bed
asserts this path" is not the same as "this path is worth asserting".

#### etc config — 21

| upstream test | system surface named in the test |
|---|---|
| `brcmfmac-supplicant-test.sh` | `/etc/modprobe.d,/etc/modprobe.d/brcmfmac.conf` |
| `browser-policy-dir-test.sh` | `/etc/chromium,/etc/chromium/policies,/etc/chromium/policies/managed,/etc/ch…` |
| `browser-policy-sudoers-test.sh` | `/etc/brave/policies/managed,/etc/chromium/policies/managed,/etc/opt/chrome/…` |
| `chromium-ytdlp-test.sh` | `/etc/passwd` |
| `default-apps-test.sh` | `/etc/chromium,/etc/chromium/policies,/etc/chromium/policies/managed` |
| `dev-env-path-test.sh` | `/etc/omarchy.conf` |
| `dev-link-test.sh` | `/etc/sudoers` |
| `dev-unlink-test.sh` | `/etc/omarchy.conf,/etc/sudoers.d/omarchy-dev-path` |
| `fingerprint-invitation-test.sh` | `/etc/pam.d,/etc/pam.d/omarchy-lock-fingerprint` |
| `hyprland-keyboard-layout-test.sh` | `/etc/mkinitcpio.conf.d/omarchy_hooks.conf,/etc/vconsole.conf` |
| `legacy-power-udev-rules-migration-test.sh` | `/etc/udev/rules.d` |
| `locale-env-test.sh` | `/etc/profile.d/locale.sh` |
| `nvidia-kms-hook-test.sh` | `/etc/mkinitcpio.conf.d/omarchy_hooks.conf,/etc/vconsole.conf` |
| `privileged-heredoc-test.sh` | `/etc/...,/etc/file,/etc/omarchy/image,/etc/sddm.conf.d` |
| `provisioning-groups-test.sh` | `/etc/chromium/policies/managed` |
| `retired-installer-artifacts-migration-test.sh` | `/etc/resolv.conf,/etc/sudoers.d,/etc/sudoers.d/99-omarchy-installer-reboot,…` |
| `security-fido2-migration-test.sh` | `/etc/fido2/fido2` |
| `security-fido2-remove-test.sh` | `/etc/fido2` |
| `security-fido2-test.sh` | `/etc/fido2,/etc/fido2/fido2,/etc/pam.d/polkit-1,/etc/pam.d/sudo` |
| `sleep-lock-test.sh` | `/etc/systemd/logind.conf.d/20-inhibit-delay.conf` |
| `webapp-install-test.sh` | `/etc/passwd` |
## Needs per-file judgement (57)

These name a command surface rather than a path, so no mechanical rule decides them. The
hyprland-runtime cluster is the substantive one and is reachable with verbs that already
exist — `wl: hypr-monitors` for the `monitor-*` set, `wl: hypr-clients` for the
window/workspace/focus set, `wl: hypr-layers` for surfaces, `quickshell:` for shell
restart/reload. **No new charly capability is required for it.**

#### bootloader — 3

| upstream test | system surface named in the test |
|---|---|
| `limine-cmdline-migration-test.sh` | `/etc/limine-entry-tool.d/omarchy-defaults.conf,limine` |
| `nvidia-kms-migration-test.sh` | `/etc/mkinitcpio.conf.d/omarchy_hooks.conf,limine` |
| `plymouth-set-test.sh` | `/etc/omarchy.conf,limine` |

#### btrfs snapshots — 2

| upstream test | system surface named in the test |
|---|---|
| `snapper-timeline-leak-test.sh` | `snapper` |
| `snapshot-create-test.sh` | `snapper` |

#### hyprland runtime — 25

| upstream test | system surface named in the test |
|---|---|
| `acceptance-helpers-test.sh` | `hyprctl` |
| `brightness-display-test.sh` | `hyprctl` |
| `default-agent-test.sh` | `hyprctl` |
| `hyprland-focus-app-test.sh` | `hyprctl` |
| `hyprland-reload-guard-test.sh` | `hyprctl` |
| `hyprland-session-locked-test.sh` | `hyprctl` |
| `hyprland-window-close-all-test.sh` | `hyprctl` |
| `hyprland-window-test.sh` | `hyprctl` |
| `hyprland-workspace-layout-test.sh` | `hyprctl` |
| `keybindings-menu-test.sh` | `hyprctl` |
| `launch-about-test.sh` | `/etc/fastfetch/config.jsonc,hyprctl` |
| `launch-shell-test.sh` | `hyprctl,pacman` |
| `monitor-clamshell-scale-test.sh` | `hyprctl` |
| `monitor-modeless-test.sh` | `hyprctl` |
| `monitor-output-name-test.sh` | `hyprctl` |
| `monitor-recovery-test.sh` | `hyprctl` |
| `monitor-scaling-test.sh` | `hyprctl` |
| `monitor-state-test.sh` | `hyprctl` |
| `preinstalls-test.sh` | `hyprctl` |
| `provision-user-test.sh` | `hyprctl` |
| `restart-shell-test.sh` | `hyprctl,systemctl` |
| `runtime-smoke-test.sh` | `hyprctl` |
| `screenrecording-test.sh` | `hyprctl` |
| `system-lock-test.sh` | `hyprctl` |
| `toggle-input-device-test.sh` | `hyprctl` |

#### locale/time — 2

| upstream test | system surface named in the test |
|---|---|
| `setup-form-test.sh` | `timedatectl` |
| `timezone-test.sh` | `/etc/sudoers.d/omarchy-tzupdate,timedatectl` |

#### network — 2

| upstream test | system surface named in the test |
|---|---|
| `network-password-test.sh` | `nmcli` |
| `network-qr-test.sh` | `nmcli` |

#### package state — 12

| upstream test | system surface named in the test |
|---|---|
| `channel-test.sh` | `pacman` |
| `input-group-migration-test.sh` | `pacman` |
| `launcher-remove-test.sh` | `pacman` |
| `pkg-drop-test.sh` | `pacman` |
| `sudoless-docker-posture-test.sh` | `pacman` |
| `update-available-test.sh` | `pacman` |
| `update-file-conflict-test.sh` | `pacman` |
| `update-orphan-test.sh` | `pacman` |
| `update-package-conflict-test.sh` | `pacman` |
| `update-pacman-guard-test.sh` | `pacman` |
| `version-test.sh` | `pacman` |
| `zram-migration-test.sh` | `pacman` |

#### systemd units — 11

| upstream test | system surface named in the test |
|---|---|
| `dns-sudoers-test.sh` | `/etc/sudoers.d/omarchy-dns,nmcli,systemctl` |
| `firewall-config-test.sh` | `systemctl,ufw` |
| `installed-service-test.sh` | `systemctl` |
| `locate-test.sh` | `pacman,systemctl` |
| `network-manager-transition-test.sh` | `nmcli,systemctl` |
| `setup-security-sshd-test.sh` | `/etc/ssh/sshd_config.d/10-omarchy-hardening.conf,systemctl` |
| `sleep-lock-environment-migration-test.sh` | `systemctl` |
| `sshd-hardening-migration-test.sh` | `/etc/ssh/sshd_config.d/10-omarchy-hardening.conf,systemctl` |
| `system-power-test.sh` | `systemctl` |
| `systemd-test.sh` | `/etc/systemd,/etc/systemd/oomd.conf.d/10-omarchy.conf,pacman,systemctl` |
| `t2-hardware-test.sh` | `limine,systemctl` |
## Measured on a live guest — which candidate paths actually exist

The 21 mechanically-decidable gaps are not equally assertable. Most name **opt-in** surfaces
(fido2 enrolment, nvidia hardware, `omarchy dev-link`) that a stock unattended install never
creates, so asserting them would encode a false expectation and fail a correct guest.

Probed read-only over `charly vm ssh` against a freshly rebuilt `check-omarchy-desktop-vm`
guest (the `update` step's rebuild, so a machine built from nothing):

| path | on a stock guest | upstream test |
|---|---|---|
| `/etc/profile.d/locale.sh` | **present** | `locale-env-test.sh` |
| `/etc/systemd/logind.conf.d/20-inhibit-delay.conf` | **present** (`InhibitDelayMaxSec=15`) | `sleep-lock-test.sh` |
| `/etc/vconsole.conf` | **present** (`KEYMAP=us`, `XKBOPTIONS=terminate:ctrl_alt_bksp`) | `hyprland-keyboard-layout-test.sh` |
| `/etc/mkinitcpio.conf.d/omarchy_hooks.conf` | **present** (`HOOKS=(… plymouth … btrfs-overlayfs)`) | `nvidia-kms-hook-test.sh` |
| `/etc/chromium/policies/managed` | present but **EMPTY** (0 entries) | `browser-policy-dir-test.sh`, `default-apps-test.sh` |
| `/etc/omarchy.conf` | absent | `dev-env-path-test.sh` |
| `/etc/sudoers.d/omarchy-dev-path` | absent | `dev-unlink-test.sh` |
| `/etc/fido2` | absent | `security-fido2*-test.sh` |
| `/etc/pam.d/omarchy-lock-fingerprint` | absent | `fingerprint-invitation-test.sh` |
| `/etc/modprobe.d/brcmfmac.conf` | absent | `brcmfmac-supplicant-test.sh` |

**Consequences for U5.** Four rows carry assertable content and are worth adding. The chromium
policy directory exists but holds nothing, so only its existence is assertable — asserting a
policy *file* would fail a correct guest, which is exactly the trap this probe exists to catch.
Five rows are absent by design and get **"no live form on a stock guest"**; they would need a bed
that opts into the feature first, which is a different claim from the one these beds make.

## What this table does NOT claim

- It does not claim each listed gap is worth asserting — that is the U5 judgement, made
  per row when the assertion is written.
- "Already covered" means a bed asserts the same exact path. It does not mean the coverage
  is as strong as upstream's; where upstream asserts more detail, strengthening the
  existing step is preferable to adding a second one (R3).
- The signal-based classification is a filter, not a proof. A file naming no system surface
  can still have one.

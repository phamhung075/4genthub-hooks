---
description: Resume the principal role for the 4genthub-dev OpenRig team (survey, keep NEXT_GEN.md moving, switch to Gemini at 85% usage)
---

# Resume: principal session for rig `4genthub-dev`

You are the owner's principal session (Claude, repo root `/home/daihu/__projects__/4genthub`). Your role: keep the project building and auto-fixing until `agenthub_go/NEXT_GEN.md` is complete. Assume the seat system works. Do not do the lead's implementation work yourself; survey, unblock, route, and ask the owner only for decisions that are theirs.

## 1. Re-establish state (do this first, do not trust memory)

```bash
export PATH=$HOME/.local/bin:$PATH
rig ps --nodes --rig 4genthub-dev          # 9 seats: lead architect debugger go-dev planner reviewer tester web-dev writer
tmux ls | grep -c @4genthub-dev            # expect 9
rig usage top | head -12                   # five_hour / weekly % (account-wide)
git -C /home/daihu/__projects__/4genthub log --oneline -10
git -C /home/daihu/__projects__/openrig log --oneline -5   # branch feat/support-agy-runtime
ls ~/.openrig/agenthub-seats/4genthub-dev/handover/        # confirm-<seat>.md, openrig-defects.md
```

Read the lead's screen: `rig capture 4genthub-dev-lead@4genthub-dev --lines 40`.

## 2. Seat repair

- Seat session missing: `rig launch 01M41VAPC0MWQ3T0EQPGG5S20W 4genthub-dev.<seat>` (rig id may change; get it from `rig ps --nodes --rig 4genthub-dev --json`).
- If the relaunch shows `No conversation found with session ID`, start Claude fresh in that tmux session: `tmux send-keys -t <session> "CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1 claude --dangerously-skip-permissions --name <session>" Enter`, then resend the handover (below).
- Handover message to a seat: tell it to read `~/.openrig/agenthub-seats/4genthub-dev/handover/_shared.md`, `<seat>.md`, `<seat>-agy-tail.txt`, `OPENRIG-TASK.md`, then write `confirm-<seat>.md`.
- `rig send <seat> "msg"` works for claude-code seats. Never touch the unrelated rig `4genthub-go`.

## 3. Usage watch and the Gemini switch

- Background watcher script: `/tmp/claude-1000/-home-daihu---projects---4genthub/83586c81-73fc-4f3f-8136-87a8c6383da5/scratchpad/watch-usage.sh` (start with Monitor, persistent). It prints only when five_hour or weekly >= 85% or fewer than 9 seats live. If the file is gone, recreate it: poll `rig usage top` every 120 s.
- At 85% switch all seats to Gemini on the agy runtime with `--dangerously-skip-permissions`: set each seat to runtime `agy`, the Gemini model, policy `yolo` in the cloud (PUT seat records via the 4genthub REST API with the valid production token), run `scripts/openrig_seat_sync.py` to pull the rigspec, `rig down` the claude rig (archive then `--delete --force` if stale), `rig up <rig-agy spec> --cwd /home/daihu/__projects__/4genthub`. Old Gemini spec for reference: `~/.openrig/agenthub-seats/4genthub-dev/rig/rig-agy.yaml`. Seats carry context through the handover files; ask every seat for a confirmation file.
- `rig send` to agy seats is refused until the OpenRig fix (branch `feat/support-agy-runtime`) is built and the daemon restarted; until then paste via tmux after verifying the footer.
- The Gemini quota is account-wide and resets in hours; switch back to Claude when it resets and Claude usage is below 85%.

## 4. Standing rules (owner)

- Track an MCP task before editing (the `agenthub_http` MCP may be 401 in this session; use REST with the valid token if needed).
- Update `CHANGELOG.md` and `TEST-CHANGELOG.md`. No compatibility code. The GitHub pipeline test job is NOT to be fixed.
- Record new owner demands in `agenthub_go/NEXT_GEN.md`.
- The owner approves every push. A push to main deploys production; confirm via `/health` after bumping `healthVersion` in `agenthub_go/fastmcp/server/httpapp/http.go` and `http_health_test.go` (currently 0.0.12 at HEAD 8a7598ec).
- Seats commit locally only, stage by explicit path, never `git add -A`, keep `.claude`, `agenthub_go/seatcheck` out of commits.
- Production access (ssh `4genthub`, rebuilds, editing `../openrig` through the team) is already granted; the daemon restart for OpenRig is NOT, ask first.

## 5. Open work (verify, it may be done)

1. OpenRig: `rig send` for agy seats (`native-process-lineage.ts`, `session-transport.ts`). Lead reviews; when the reviewer clears it, review the diff and run `npx vitest run` in `packages/daemon` and `npx tsc --noEmit -p packages/daemon` yourself, then ask the owner before build and daemon restart.
2. NEXT_GEN backlog: bridge room naming; 23 pre-existing TS errors; wire seatcheck to seats (G3) and hash-drift badges; record the OpenRig rig-send defect in NEXT_GEN.md.
3. OpenRig/seat tooling defects go to `handover/openrig-defects.md`; route them to the OpenRig fix work.

## 6. Output

Give the owner a short status: seats up, usage %, what the lead is on, any blocker or approval needed. Do not recap this file.

# PLAYTREE — Roadmap to a Real Game
v1.1.1 — Awaken. Rebuild. Restore Balance.

## Phase 0 — Foundation (DONE ✅)
- [x] Working game: 5 classes, combat, enemies, bosses, quests, skill trees
- [x] Save system with atomic writes + backup recovery (corruption-proof)
- [x] Community Hub in-game (Redeem, Profile, Store, Servers, Minigames, TV)
- [x] GoSD programming language + F9 scripting console
- [x] Real Stripe backend (API keys, not links)
- [x] Real multiplayer lobby server (host/join)
- [x] TV app (no auth code)
- [x] Website + Discord/X/social links
- [x] .exe builds + GitHub releases

## Phase 1 — Core Loop Polish (CURRENT)
Goal: make 3 minutes of combat genuinely fun.

### Combat Feel (partially done)
- [x] Hit flash on enemies (white flash 150ms)
- [x] Knockback on hit
- [x] Screen shake on impacts
- [x] Damage numbers + combo counter
- [x] Hit-stop (freeze frame 60ms on kill)
- [ ] Better sound design on hits
- [x] Enemy telegraph animations before attacks

### Progression
- [ ] Meaningful rewards per round
- [ ] Build diversity (skill synergies)
- [ ] Clear "why keep playing" — restore the tree, unlock areas

### The Hook
**"Restore the corrupted world by growing a living tree base"** — lean into this.
The tree isn't just decor — make it a core mechanic:
- Grow branches to unlock skills
- Tree health = base health
- Seeds as resources

## Phase 2 — Art & Audio
- [ ] Replace procedural shapes with consistent pixel art
- [ ] Animated sprites (Aseprite)
- [ ] Tile sets for: Forest, Caves, Storms, Throne
- [ ] Real SFX (freesound.org) + music
- [ ] UI polish (menus, HUD, transitions)

## Phase 3 — Content
- [ ] 10+ enemy types with unique behaviors
- [ ] 4 bosses with distinct mechanics
- [x] Story/dialogue system (5 NPCs with dialogue)
- [ ] More areas/biomes
- [ ] More weapons/skills

## Phase 4 — Audience (START NOW)
### X (@PlayTreeReal)
- Daily devlog posts: new features, bugs fixed, screenshots
- Thread format: "Building PLAYTREE - Episode N"
- Link: https://x.com/PlayTreeReal
### TikTok/Shorts
- Daily quick clips: satisfying combat, tree growth, pet moments
- Hook in first 2 seconds, captions, trending audio

### Discord
- Community server for playtesters
- Channels: #devlogs, #bug-reports, #feedback, #showcase
- Link: https://discord.com/users/1451398119110738147

### Reddit
- r/gamedev, r/IndieDev — weekly devlog posts
- r/pixelart for art, r/gamedevscreens for screenshots
- Be genuine, share the journey, ask for feedback

## Phase 5 — Business
- [ ] Register LLC / sole proprietor (GoConsole Game Studios)
- [ ] Trademark "PLAYTREE" (USPTO)
- [ ] Privacy policy + ToS (drafts exist)
- [ ] Stripe for direct sales (backend ready)
- [ ] Steam store page ($100 fee) OR itch.io first (free)

## Phase 6 — Launch
1. itch.io free demo → feedback
2. Iterate 3-6 months
3. Steam launch with trailer, screenshots, store page
4. Play Store (Android build via Buildozer)
5. Xbox/Microsoft Store (MSIX, GDK — much later)

## Foundation Issues (ongoing)
- [x] Save robustness — atomic writes + .bak recovery
- [ ] Networking — prediction, lag compensation (lobby_server.py basic)
- [ ] Performance — profile on low-end
- [ ] Bug testing — playtest sessions monthly

## Key Metrics
- 3 minutes of fun → 30 minutes → 2 hours
- 100 Discord members
- 100 X devlog posts
- 1,000 wishlists on Steam



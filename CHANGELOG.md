# PLAYTREE Changelog

## [1.0.1] - 2026-11-22
### Added
- Touchscreen support with virtual controls (F8 toggle)
- GitHub Release workflow (.github/workflows/release.yml)
- create_github_release.bat for manual releases
- .env.example for secure API key management
- .gitignore for build artifacts and secrets
- Haptic feedback function for mobile touch controls
- Gradle-based Android build guide (GRADLE_ANDROID_GUIDE.md)
- Tree Points and Tree Coins currency system (src/currency.py)
- Store page for buying Tree Points and Tree Coins (website/store.html)
- Servers browser page (website/servers.html)
- Minigames page with install-as-app prompt (website/minigames.html)
- Stripe payment integration placeholder (demo mode)
- Friends list, profile, login/logout, and toast system (website/shared.js)
- Fully working buttons on Store, Servers, Minigames, Profile, Redeem pages
- TV mode page (website/tv.html) with pairing code and large-screen layout
- GoSD programming language embedded in the game (src/gosd.py) with F9 scripting console
- Android TV WebView wrapper app (playtree/android_tv/) + ADB connect/install scripts
- ADB deployment scripts: adb_tv_connect.bat, install_on_tv.bat, serve_website_local.bat
- Terms of Service page (website/tos.html)
- Cookie consent banner on website
- Privacy and Terms links in website footer
- Accessibility: ARIA labels, skip-to-content link
- Boss health bar resized (320px) to prevent HUD overlap
- Minimap resized (120px) for cleaner layout
- Message overlay repositioned to avoid quest tracker overlap
- All website pages cached in service worker (v4)

### Changed
- Rebranded: RQBBOX Game Studios → GoConsole Game Studios
- Rebranded: RHYSTECH/RTECH → GoStudios
- Rebranded: PlayTree Games → PlayTree Studios
- Package domain: org.rhystech → org.gostudios
- Website nav now includes Redeem, Profile, Store, Servers, Minigames links
- Service worker updated to v4 with tolerant caching
- Black screen fix: render surface always blitted to display

### Fixed
- Resolved git merge conflicts in index.html, styles.css, script.js, sw.js, sitemap.xml, downloads/index.html, pages.yml, PARTNER_CENTER_CHECKLIST.md that broke the website
- Permanent black screen (render surface only blitted when window size differed)
- Touch finger coordinate mapping to 1280×720 render surface
- Virtual control taps no longer fire UI clicks or stray attacks
- Website download buttons no longer overlap on mobile
- Merge conflicts in sw.js resolved

## [1.0.0] - 2026-06-14
### Added
- Initial release with 5 playable classes
- 4 campaign rounds with unique bosses
- Daily login rewards, leaderboards, skill trees
- Equipment, enchanting, fishing, taming, base building
- Weather system, day/night cycle, mount system
- New Game+ mode, 11-step tutorial
- USB auto-launch and auto-update support
- Xbox controller support with on-screen prompts
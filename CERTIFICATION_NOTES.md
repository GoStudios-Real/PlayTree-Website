# PLAYTREE Certification Notes

## General
- Consistent version across builds/manifests/store listings.
- Live privacy policy URL (`/privacy.html`) and working support contact.
- Accurate age rating; only required permissions; confirm asset rights.
- Test: clean install, launch, save/load, controls, audio, exit/resume, no crashes.

## Microsoft Store (Windows PC)
- Upload `.msix`/`.msixupload`, not raw `.exe`.
- Package Publisher must match Partner Center.
- Use valid signing; test certs are local only.
- Minimal capabilities; `runFullTrust` for desktop EXE.

## Xbox Console
- Desktop EXE/MSIX is not an Xbox console XVC package.
- Console release requires Xbox-compatible/GDK pipeline and XR certification.
- Test in Xbox Dev Mode before submission.

## Google Play
- Keep package ID `org.gostudios.playtree`.
- Meet target API, Play App Signing, Data safety, and privacy requirements.
- Test touch/back button/orientation/performance on multiple devices.

## Pre-submit
- [ ] No startup crash/black screen
- [ ] Save/settings/controls work
- [ ] Privacy policy live
- [ ] Screenshots match build
- [ ] Version numbers match
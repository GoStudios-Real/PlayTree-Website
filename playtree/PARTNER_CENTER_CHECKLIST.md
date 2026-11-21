# Microsoft Store / Partner Center Checklist

## Before packaging
- [ ] Run `build_playtree.bat` and verify `dist\PLAYTREE.exe` works.
- [ ] Create Store assets: icon 300x300, screenshots, trailer (optional).
- [ ] Have a Microsoft Partner Center developer account.

## MSIX package
- [ ] Install MSIX Packaging Tool (Microsoft Store).
- [ ] Create package from `dist\PLAYTREE.exe`.
- [ ] Use `AppxManifest.xml.template` as reference for identity/capabilities.
- [ ] Publisher must match Partner Center `CN=...`.
- [ ] Sign MSIX with a valid certificate (`sign_msix_test.ps1`).

## Partner Center submission
- [ ] Reserve app name: PLAYTREE.
- [ ] Product type: MSIX or EXE app.
- [ ] Pricing: Free.
- [ ] Category: Games > Action & adventure / RPG.
- [ ] Upload listing copy from `chrome_ext/store_description.txt`.
- [ ] Upload screenshots, icons, age rating questionnaire.
- [ ] Select device families (Windows Desktop; Xbox only if certified).
- [ ] Submit for certification.
- [ ] Add privacy policy URL (website/privacy.html).

## Xbox note
Full Xbox console Store availability requires Xbox certification and a compatible package. Desktop MSIX is the easiest starting point; test with Xbox Dev Mode before targeting console certification.
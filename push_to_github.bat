@echo off
setlocal EnableExtensions
cd /d "%~dp0" || exit /b 1

set "REPO_URL=https://github.com/GoStudios-Real/PlayTree-Website.git"
set "PUBLISH_DIR="
set "REPO_ROOT="
set "ORIGIN_URL="

for /f "delims=" %%R in ('git rev-parse --show-toplevel 2^>nul') do set "REPO_ROOT=%%R"
if not defined REPO_ROOT (
  echo ERROR: This folder is not inside a Git repository.
  exit /b 1
)

for /f "delims=" %%R in ('git remote get-url origin 2^>nul') do set "ORIGIN_URL=%%R"
if /i not "%ORIGIN_URL%"=="%REPO_URL%" (
  echo Setting origin remote to %REPO_URL%
  git remote remove origin 2>nul
  git remote add origin %REPO_URL%
)

if not exist "%REPO_ROOT%\website\index.html" (
  echo ERROR: %REPO_ROOT%\website\index.html was not found.
  exit /b 1
)

echo Pulling latest changes...
git -C "%REPO_ROOT%" fetch origin main
if errorlevel 1 (
  echo WARNING: Could not fetch origin/main. Continuing anyway...
)

git -C "%REPO_ROOT%" pull --rebase origin main 2>nul

set "PUBLISH_DIR=%TEMP%\playtree-pages-%RANDOM%-%RANDOM%"
git -C "%REPO_ROOT%" worktree add --detach "%PUBLISH_DIR%" refs/remotes/origin/main 2>nul
if errorlevel 1 (
  echo Creating new branch for publish...
  git -C "%REPO_ROOT%" worktree add --detach "%PUBLISH_DIR%" HEAD
)

robocopy "%REPO_ROOT%\website" "%PUBLISH_DIR%\website" /E /COPY:DAT /R:2 /W:1 >nul
if errorlevel 8 goto copy_failed

git -C "%PUBLISH_DIR%" add --all -- website
if errorlevel 1 goto git_failed

git -C "%PUBLISH_DIR%" diff --cached --quiet -- website
if errorlevel 2 goto git_failed
if errorlevel 1 goto has_changes
goto no_changes

:has_changes
git -C "%PUBLISH_DIR%" -c user.name="PLAYTREE Website Publisher" -c user.email="gostudios-real@users.noreply.github.com" commit -m "Update PLAYTREE website"
if errorlevel 1 goto git_failed

git -C "%PUBLISH_DIR%" push origin HEAD:main
if errorlevel 1 goto push_failed

echo Website published successfully. GitHub Pages deployment has been triggered.
goto cleanup_success

:no_changes
echo No website changes to publish.
goto cleanup_success

:copy_failed
echo ERROR: Could not copy the website into the publish worktree.
goto cleanup_failed

:git_failed
echo ERROR: Git could not prepare the website publish commit.
goto cleanup_failed

:push_failed
echo ERROR: Push failed. Check GitHub access and branch protection, then retry.
goto cleanup_failed

:cleanup_success
git -C "%REPO_ROOT%" worktree remove "%PUBLISH_DIR%" >nul 2>nul
exit /b 0

:cleanup_failed
git -C "%REPO_ROOT%" worktree remove --force "%PUBLISH_DIR%" >nul 2>nul
exit /b 1
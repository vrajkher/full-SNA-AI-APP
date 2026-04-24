; Custom NSIS hooks for Accotech AI
; electron-builder exposes these well-known macros; they run after the
; default install / uninstall stages.

!macro customInstall
  ; ----------------------------------------------------------------
  ; Always install Python 3.12 specifically. Users may already have
  ; Python 3.13 installed, which has no pandas/numpy wheels for some
  ; versions and will trigger a source build (and fail on machines
  ; without Visual C++ Build Tools).
  ; ----------------------------------------------------------------
  nsExec::ExecToStack 'cmd /c "py -3.12 --version"'
  Pop $0
  ${If} $0 != "0"
    DetailPrint "Installing Python 3.12 via winget..."
    nsExec::ExecToLog 'cmd /c "winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements"'
  ${EndIf}

  ; ----------------------------------------------------------------
  ; Create a per-user venv from Python 3.12 specifically.
  ; --only-binary=:all: refuses source builds — we want wheels only.
  ; ----------------------------------------------------------------
  DetailPrint "Preparing Python 3.12 virtual environment..."
  nsExec::ExecToLog 'cmd /c "py -3.12 -m venv \"$APPDATA\Accotech\venv\""'
  nsExec::ExecToLog 'cmd /c "\"$APPDATA\Accotech\venv\Scripts\python.exe\" -m pip install --upgrade pip wheel setuptools"'
  nsExec::ExecToLog 'cmd /c "\"$APPDATA\Accotech\venv\Scripts\python.exe\" -m pip install --only-binary=:all: -r \"$INSTDIR\resources\backend\requirements.txt\""'
!macroend

!macro customUnInstall
  DetailPrint "Removing Accotech user data..."
  RMDir /r "$APPDATA\Accotech"
!macroend

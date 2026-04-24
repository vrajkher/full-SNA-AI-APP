; Custom NSIS hooks for Accotech AI
; electron-builder exposes these well-known macros; they run after the
; default install / uninstall stages.

!macro customInstall
  ; ----------------------------------------------------------------
  ; Ensure Python is present. If not, silently install Python 3.12
  ; via winget (available on Windows 10 1809+ and Windows 11).
  ; ----------------------------------------------------------------
  nsExec::ExecToStack 'cmd /c "python --version"'
  Pop $0
  ${If} $0 != "0"
    DetailPrint "Python not detected – installing Python 3.12..."
    nsExec::ExecToLog 'cmd /c "winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements"'
  ${EndIf}

  ; ----------------------------------------------------------------
  ; Install backend dependencies into a per-user venv so nothing
  ; pollutes the system-wide Python.
  ; ----------------------------------------------------------------
  DetailPrint "Preparing Python virtual environment..."
  nsExec::ExecToLog 'cmd /c "python -m venv \"$APPDATA\Accotech\venv\""'
  nsExec::ExecToLog 'cmd /c "\"$APPDATA\Accotech\venv\Scripts\python.exe\" -m pip install --upgrade pip"'
  nsExec::ExecToLog 'cmd /c "\"$APPDATA\Accotech\venv\Scripts\python.exe\" -m pip install -r \"$INSTDIR\resources\backend\requirements.txt\""'
!macroend

!macro customUnInstall
  DetailPrint "Removing Accotech user data..."
  RMDir /r "$APPDATA\Accotech"
!macroend

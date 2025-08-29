@echo off
setlocal enabledelayedexpansion

REM Locate Anaconda/Miniconda installation
set "CANDIDATES=%USERPROFILE%\anaconda3;%USERPROFILE%\miniconda3;C:\ProgramData\anaconda3"
for %%D in (%CANDIDATES%) do (
  if exist "%%D\Scripts\activate.bat" (
    set "CONDA_ROOT=%%D"
    goto :found
  )
)

echo [ERROR] Could not find Anaconda/Miniconda on this system.
echo Open "Anaconda Prompt" and run the following manually:
echo   cd "%cd%"
echo   conda env create -f environment.yml
echo   conda activate churn-ml
exit /b 1

:found
echo Using Conda at "%CONDA_ROOT%"
call "%CONDA_ROOT%\Scripts\activate.bat" "%CONDA_ROOT%"

REM Verify conda is initialized
conda --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Failed to initialize conda shell. Try running from Anaconda Prompt.
  exit /b 1
)

REM Create or update the environment
conda env list | findstr /I "^churn-ml" >nul
if %errorlevel%==0 (
  echo Updating environment 'churn-ml' ...
  conda env update -n churn-ml -f environment.yml
) else (
  echo Creating environment 'churn-ml' ...
  conda env create -f environment.yml
)

REM Activate the environment
call conda activate churn-ml

REM Ensure pip requirements (harmless if already satisfied)
python -m pip install -r requirements.txt

REM Launch FastAPI server
python -m uvicorn api.app:app --reload --port 8000

pause

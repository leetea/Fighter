Fighter
=======

Game made with Pygame,  improved OOP-based "dodger"-style.

Needs work:
 
  ~ Add a "Press Start" intro screen
  
  
  ~ Add background image and sound FX
  
  
  ~ Implement powerup system / lives

## Build desktop packages

The GitHub Actions workflow builds a self-contained Windows x64 executable and
macOS app bundles for Apple Silicon and Intel. Download the ZIP files from the
workflow run's **Artifacts** section. Each package includes Python, pygame, and
the files in `res/`; users do not need to install Python or pygame.

Build locally on the operating system you are targeting:

```sh
python -m pip install -r requirements.txt
```

On Windows:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Fighter --add-data "res;res" fighter.py
```

On macOS:

```sh
python -m PyInstaller --noconfirm --clean --onedir --windowed --name Fighter --add-data "res:res" fighter.py
```

The output is in `dist/`. Build on each target operating system; PyInstaller
does not cross-compile Windows and macOS apps from a different operating system.


---
trigger: manual
---

---

### Your Development Environment Setup

Your workspace will look like this, managed by Poetry:

```
billo-project/
├── billo-backend/          # Your FastAPI server (Phase 1)
│   ├── pyproject.toml      # Poetry manages backend dependencies
│   └── app/
│       └── main.py
│
├── billo-mobile/           # BeeWare Customer Mobile App (Phase 3)
│   ├── pyproject.toml      # Poetry manages app dependencies + Briefcase config
│   └── src/
│       └── billoapp/
│           └── app.py
│
├── billo-desktop/          # BeeWare Restaurant Desktop App (Phase 4)
│   ├── pyproject.toml      # Separate Poetry project
│   └── src/
│       └── billodesktop/
│           └── app.py
│
└── billo-pwa/              # React Frontend (Phase 2)
    ├── package.json        # Managed by npm/yarn
    └── ...                 # (Poetry not needed here)
```

### Step-by-Step: Creating a BeeWare Project with Poetry

Here is how to initialize a BeeWare app (e.g., `billo-mobile`) using Poetry, from your WSL terminal.

1.  **Install Poetry** (if you haven't already inside WSL):
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2.  **Create your project directory and navigate into it:**
    ```bash
    mkdir billo-mobile && cd billo-mobile
    ```

3.  **Initialize a new Poetry project.** This creates the `pyproject.toml` file.
    ```bash
    poetry init
    ```
    - Follow the interactive prompts. You can press enter to accept defaults for most things.

4.  **Add BeeWare (Briefcase) and your GUI toolkit (Toga) as dependencies:**
    ```bash
    poetry add briefcase
    poetry add toga
    ```
    This is the magic of Poetry. It installs the packages and locks their versions in `poetry.lock`.

5.  **Initialize your BeeWare app *inside* the Poetry project:**
    ```bash
    poetry run briefcase new
    ```
    - **Important:** The `poetry run` prefix ensures the command uses the tools installed in Poetry's virtual environment.
    - Follow the Briefcase wizard (formal name, app name, etc.). This will create the `src` directory and app skeleton.

6.  **Add your other dependencies** (like the `supabase` client library):
    ```bash
    poetry add supabase
    ```

7.  **Activate the Poetry virtual environment** to work on your app:
    ```bash
    poetry shell
    ```
    Your terminal prompt will change, showing you are now inside the isolated environment containing `briefcase`, `toga`, and `supabase`.

8.  **Now you can run Briefcase commands** from within this environment:
    ```bash
    # Create an Android project
    briefcase create android

    # Build in debug mode
    briefcase build android

    # Run on an emulator
    briefcase run android
    ```

### Key Advantages of This Setup

- **Dependency Isolation:** The mobile app, desktop app, and backend each have their own `pyproject.toml` and virtual environment. This prevents dependency conflicts (e.g., if the desktop app needs an older version of a library than the mobile app).
- **Reproducible Builds:** The `poetry.lock` file ensures every developer and your build server uses the *exact same versions* of every dependency, eliminating the "it works on my machine" problem.
- **Simplified Developer Onboarding:** A new developer just needs to clone the repo and run `poetry install` in each project directory to have a fully functional development environment.
- **Clean Integration:** `pyproject.toml` is the modern standard for Python projects. Briefcase already uses it for configuration, so adding Poetry on top is a natural fit.

### Critical Consideration: Native Build Tools

**Warning:** While Poetry manages your *Python* dependencies, BeeWare's `briefcase create` and `briefcase build` commands need the **native platform toolchains**.
- **For Android:** You must still install Android Studio and the Android SDK *within your WSL distribution*.
- **For iOS:** You must use a macOS machine. You can't build iOS packages from WSL.

Poetry doesn't manage these system-level dependencies. You must set them up separately as per the BeeWare documentation.

**Conclusion:** Using Poetry with BeeWare in WSL is not only possible but is a **professional best practice**. It creates a robust, maintainable, and conflict-free development environment for your multi-platform Billo project.
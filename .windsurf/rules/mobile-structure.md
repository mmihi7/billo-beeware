---
trigger: manual
description: Strictly use the structure to build the mobile apps
---

billo-mobile/                      # Root project directory
├── .github/                      # GitHub workflows
│   └── workflows/
│       └── tests.yml
├── android/                      # Android build files (auto-generated)
├── assets/                       # Static assets
│   ├── fonts/
│   ├── icons/
│   └── images/
├── docs/                         # Project documentation
├── resources/                    # App resources
│   ├── android/                  # Android-specific resources
│   ├── ios/                      # iOS-specific resources
│   ├── icon.png                  # App icon
│   └── splash.png                # Splash screen
├── src/                          # Source code
│   └── billo/                    # Main package
│       ├── __init__.py
│       ├── app.py                # Main application entry point
│       ├── config/               # Configuration
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── core/                 # Core functionality
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── database.py
│       ├── models/               # Data models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── restaurant.py
│       ├── screens/              # Screen components
│       │   ├── __init__.py
│       │   ├── auth/
│       │   ├── home/
│       │   └── onboarding/
│       └── utils/                # Utilities
│           ├── __init__.py
│           └── helpers.py
├── tests/                        # Test files
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── .env.example                  # Environment variables example
├── .gitignore
├── pyproject.toml                # Project configuration
└── README.md
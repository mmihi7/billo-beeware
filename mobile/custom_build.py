import os
import shutil
import subprocess

def main():
    # Clean previous builds
    for dirname in ['build', 'dist']:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
    
    # Create a clean requirements file without pydantic
    with open('requirements.txt', 'w') as f:
        f.write("""toga-android>=0.5.2
python-dotenv>=1.0.0
segno>=1.5.0
aiohttp>=3.9.0
""")
    
    # Build with explicit requirements
    subprocess.run(['briefcase', 'build', 'android', '--no-docker'], check=True)

if __name__ == '__main__':
    main()

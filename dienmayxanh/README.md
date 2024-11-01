# DIEN MAY XANH SCRAPER 
## Repository Structure

- **diemayxanh.ipynb**: Jupyter notebook for scraping data from `diemayxanh.com`.
- **test_selenium.ipynb**: Jupyter notebook for testing Selenium functionality. This notebook may include examples or testing code to ensure Selenium is correctly configured and functioning as expected.
- **requirements.txt**: Contains a list of Python packages needed to run the notebooks and scripts in this repository. Use this file to set up your environment.
- **.env**: Environment file (typically contains sensitive information like API keys, database credentials, etc.). Ensure this file remains private and is not shared publicly.
- **.gitignore**: Specifies files and directories to be ignored by Git. Usually includes sensitive information files, like `.env`, and large or unnecessary files for version control.

## Getting Started

### Prerequisites

- Python 3.x >= 3.9
- Recommended to use a virtual environment to manage dependencies (conda or pip venv)

1. **Conda**:
   ```
   conda create -n [your env name] python=3.10
   conda activate [your env name]
   ```
2. **Py-env**:
   ```
   python -m venv [your env name]
   ```
   **follow command below to active environment**
   | Platform | Shell       | Command to activate virtual environment      |
   |----------|-------------|-------------------------------------------------|
   | POSIX    | bash/zsh    | `$ source <venv>/bin/activate`                  |
   |          | fish        | `$ source <venv>/bin/activate.fish`             |
   |          | csh/tcsh    | `$ source <venv>/bin/activate.csh`              |
   |          | pwsh        | `$ <venv>/bin/Activate.ps1`                     |
   | Windows  | cmd.exe     | `C:\> <venv>\Scripts\activate.bat`              |
   |          | PowerShell  | `PS C:\> <venv>\Scripts\Activate.ps1`           |
### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ManTD2003/Data-Science-Project.git
   cd dienmayxanh
   pip install -r requirements.txt
   ```
2. **Change urls from Dien may xanh**:
    replace dienmayxanh categories link with urls variables then run
    ```
      python run.py
    ```

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)

## Installation
1. Clone the Repository
```
git clone https://github.com/SanAfaGal/pdf-bank-statement-processor.git
cd pdf-bank-statement-processor
```

2. Creates a virtual environment named `venv` in the current directory
```
python -m venv venv
```

3. Activates the virtual environment (Windows)
```
.\env\Scripts\activate
```

4. Upgrades the core Python packaging tools
```
pip install --upgrade pip setuptools wheel
```

5. Installs all the dependencies specified in the `requirements.txt` file
```
pip install -r requirements.txt
```

## Configuration
```
# .env file
PDF_FOLDER=path/to/pdf/folder
PDF_PASSWORD=your_pdf_password
```
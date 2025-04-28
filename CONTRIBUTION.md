# CONTRIBUTION


```bash
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Install in system
```
pip install markdown html2text reportlab
sudo apt-get install fonts-dejavu  # For Debian/Ubuntu
```

## As a CLI

```
Usage: md2pdf [OPTIONS] MD PDF

  md2pdf command line tool.

Options:
  --css PATH
  -e, --extras TEXT
  --version          Show the version and exit.
  --help             Show this message and exit.
```

For example, try to generate the project documentation with:
[Taciturnitas.pdf](Taciturnitas.pdf)
```bash
md2pdf README.md Taciturnitas.pdf
```

## konwersja pdf na audiobook

+ [eBook to Audiobook Converter with Piper-tts](https://huggingface.co/spaces/drewThomasson/ebook2audiobookpiper-tts-GPU/blob/81daf8c663616945516abb0efd3738bc9932c183/README.md)

![img.png](img/text2audio.png)


## upgrade

To upgrade all Python packages in your virtual environment, you can use one of these methods:

1. Using pip:
```bash
pip list --outdated  # First, check which packages can be upgraded
pip list -o | cut -d ' ' -f1 | xargs -n1 pip install -U
```

2. Alternative method:
```bash
pip install --upgrade pip
pip list --outdated | tail -n +3 | awk '{ print $1 }' | xargs -n1 pip install -U
```

3. If you're using a requirements file:
```bash
pip freeze > requirements.txt
pip install -r requirements.txt --upgrade
```

4. For a more interactive approach:
```bash
pip list --outdated
# Then manually upgrade specific packages or all of them
pip install --upgrade <package_name>
```

Best practices:
- Always activate your virtual environment before upgrading
- Consider creating a backup of your current environment
- Test your project after upgrading to ensure compatibility
- For production environments, upgrade packages carefully and test thoroughly


pyinstaller -y -F --add-data "rozhlasdl";"." --hidden-import progressbar --hidden-import html5lib "rozhlasdl/rozhlasdl.py"

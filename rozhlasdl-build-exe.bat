pyinstaller -y -F --add-data "rozhlasdl";"." --hidden-import progressbar --hidden-import html5lib --hidden-import retry "rozhlasdl/rozhlasdl.py"

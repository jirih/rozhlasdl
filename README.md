# rozhlasdl
###### Downloader for rozhlas.cz

## Installation
The software is developed in Python 3.8, so you should use it.

Clone the repo and go to its root directory.

install wheel: `pip install wheel`
run: `python setup.py sdist bdist_wheel`
install the wheel: `pip install dist/rozhlasdl-{{version}}-py3-none-any.whl`

(Note: Input a correct {{version}}.)

There will be a script in your 
`Python/Scripts` directory. On Windows, you can find it as `C:\Program Files\Python38\Scripts\rozhlasdl.exe`.

Note, that you can find a Windows binary at https://github.com/jirih/rozhlasdl-exe.

## Usage
Running
`python rozhlasdl/rozhlasdl.py -h`
or on Windows:
`rozhlasdl.exe -h`
you will get:

```
usage: rozhlasdl.py [-h] [-d DIR] [-n] [-f] [-s] url [url ...]

Download mp3 from rozhlas.cz urls

positional arguments:
  url                   <Required> URLs

optional arguments:
  -h, --help            Show this help message and exit
  -d DIR, --dir DIR     Directory for saving downloaded files
  -n, --no-duplicate-skipping
                        Duplicates are not skipped
  -f, --follow-next-pages
                        Follow next pages
  -m MAX_NEXT_PAGES, --max-next-pages MAX_NEXT_PAGES
                        Maximal number of next pages to follow
  -s, --simulate-audio-download
                        Downloads of audio files will be faked
  -u, --utf-8           Explicitly set UTF-8 for stdin, stdout, stderr - against problems when piping
  -p, --progress-bar-disabled
                        Disable progress-bar
  -l LOG_FILE, --log-file LOG_FILE
                        Log file
  -v, --verbose         Verbose
```
Given urls must be valid rozhlas.cz pages.

Directory for saving downloaded files can be an absolute or relative path.
If the relative path is given, then the download will go to a subdirectory of a default download directory `~/Downloads`.

Normally, the downloader first checks if the file has been already downloaded and skips the download, if the file (same
name and same size) is already present. You can choose by the flag `-n` to download the file again and store it under
a name with an index number.

### Example

The command

`python rozhlasdl/rozhlasdl.py https://dvojka.rozhlas.cz/`

will download all audios which pages are accessible by a "play" button from this page.

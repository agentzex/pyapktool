# pyapktool

pyapktool is a command line utility that can help speed up common actions usually performed when reverse engineering 
Android apps.

* It can unpack Android app's apk file and extract all of its content (Smali code, libs, layouts XMLs etc.)
* It can pack an unpacked Android app's directory, back to an apk file (which usually happens after you create
any modification/patching to the app)
* It can sign a packed apk(by default-with debug keys. This is a required step in order to install your modified 
apk to any Android device)
* **No other libraries installation/tools are needed to use this tool.** 
It will download/update any required tool (apktool, apk-signer) automatically if needed.


### pyapktool is available on PyPI:

```
$ python -m pip install pyapktool
```

### How to use

Unpacking an apk file (output will be located in a directory named 'myapp') :
```
$ pyapktool myapp.apk
```

Packing an unpacked Android app's directory, back to an apk file, and signing it with debug keys:
```
$ pyapktool myapp
```



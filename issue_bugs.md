# Bugs

## 报错1：pdf2image.exceptions.PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?

Windows 平台会遇到这个错，pdfinfo.exe 是一个用于提取 PDF 文件信息的命令行工具，通常是由 Poppler 软件包提供的。所以需要先下载并安装 Poppler 软件包。

Windows users will have to build or download poppler for Windows. I recommend [@oschwartz10612 version](https://github.com/oschwartz10612/poppler-windows/releases/) which is the most up-to-date. You will then have to add the `bin/` folder to PATH.

即解压`Release-xxx.zip`包中的`bin`文件夹放到指定目录，比如`C:\ProgramFiles\poppler_bin`，并加入系统环境变量，再重启就可以了。

参考链接：[https://github.com/Belval/pdf2image](https://github.com/Belval/pdf2image)


## 报错1-2: pdf2image.exceptions.PDFPageCountError: Unable to get page count.

系统报错弹窗：由于找不到 libdeflate.dll，无法继续执行代码。xxx

解决方案：去[该网站](https://www.dllme.com/dll/files/libdeflate)下载对应dll，然后放到 `C:\ProgramFiles\poppler_bin` 目录下即可。


## 报错2：ImportError: DLL load failed while importing _imaging: 找不到指定的模块。

```text
Traceback (most recent call last):
  File "D:\Projects\arxiv_paper_downloader\arxiv_spider.py", line 10, in <module>
    from pdf2image import convert_from_bytes
  File "D:\ProgramFiles\miniforge3\lib\site-packages\pdf2image\__init__.py", line 5, in <module>
    from .pdf2image import convert_from_bytes as convert_from_bytes
  File "D:\ProgramFiles\miniforge3\lib\site-packages\pdf2image\pdf2image.py", line 15, in <module>
    from PIL import Image
  File "D:\ProgramFiles\miniforge3\lib\site-packages\PIL\Image.py", line 88, in <module>
    from . import _imaging as core
ImportError: DLL load failed while importing _imaging: 找不到指定的模块。
```

解决方法：
python 3.10
我看了一下我的pillow版本为：
pillow==10.3.0
pdf2image==1.17.0
pypdf2==2.10.5

先卸载 pillow 再安装即可：

```bash
pip uninstall pillow
pip install pillow
```

## 报错3：pdfinfo.exe-系统错误

> 由于找不到 libdeflate.dll，无法继续执行代码。重新安装程序可能会解决此问题。
暂未解决

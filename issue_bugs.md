# Bugs

## 报错1：pdf2image.exceptions.PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?

Windows 平台会遇到这个错，pdfinfo.exe 是一个用于提取 PDF 文件信息的命令行工具，通常是由 Poppler 软件包提供的。所以需要先下载并安装 Poppler 软件包。

Windows users will have to build or download poppler for Windows. I recommend [@oschwartz10612 version](https://github.com/oschwartz10612/poppler-windows/releases/) which is the most up-to-date. You will then have to add the `bin/` folder to PATH.

即解压`Release-xxx.zip`包中的`bin`文件夹放到指定目录，比如`C:\ProgramFiles\poppler_bin`，并加入系统环境变量，再重启就可以了。

参考链接：[https://github.com/Belval/pdf2image](https://github.com/Belval/pdf2image)

pipe_name := "\\.\pipe\umiocr" ; 命名管道名称
run_name := "Umi-OCR 文字识别.exe" ; 启动程序名称

; 将启动参数数组 转为字符串，每组参数用双引号括起来。
args := ""
for index, value in A_Args
{
    args .= """" . value . """ "
}

; 检查命名管道，若存在则通过管道传指令
if FileExist(pipe_name)
{
    Sleep, 30 ; 等待一段时间让服务端重启管道
    FileEncoding UTF-8 ; 设置文件写入的编码类型为UTF8
    pipe := FileOpen(pipe_name, "w")
    if (ErrorLevel) {
        MsgBox, 16, Error, 打开命名管道%pipe_name%失败。
        return
    }
    pipe.Write(args) ; 向管道写入指令
}
; 若不存在则启动Umi-OCR软件，通过启动参数传指令
else
{
    if !FileExist(run_name)
    {
        MsgBox 程序%run_name%不存在。请将该命令行入口放在Umi-OCR文件夹下。
        return
    }
    Run, %run_name% %args%
}
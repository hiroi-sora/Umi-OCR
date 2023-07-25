# 根据当前环境，提供不同平台对象
import sys

# 根据当前操作系统选择要导入的模块
plat = sys.platform
print(f"当前平台为：{plat}")
if plat.startswith('win'):
    from .platform_windows import PlatformWindows as Platform_
elif plat.startswith('linux'):
    raise ImportError("尚未支持linux系统！")
elif plat.startswith('darwin'):
    raise ImportError("尚未支持macos系统！")
else:
    raise ImportError(f"未知系统：{plat}")

# 构造单例：平台对象
Platform = Platform_()
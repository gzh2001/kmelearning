import PyInstaller.__main__
import os
import shutil

def build():
    # 清理旧的构建文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    print("开始打包...")

    # PyInstaller 参数
    params = [
        'src/main.py',              # 主程序入口
        '--name=课程自动学习工具',    # 生成的exe名称
        '--onefile',                # 单文件模式
        '--clean',                  # 清理临时文件
        '--distpath=dist',          # 输出目录
        '--workpath=build',         # 临时目录
        '--specpath=.',             # spec文件路径
        # '--noconsole',            # 不显示控制台 (由于程序中有 input()，所以需要保留控制台)
    ]

    PyInstaller.__main__.run(params)

    print("打包完成！")
    print(f"可执行文件位置: {os.path.abspath('dist/课程自动学习工具.exe')}")
    print("请确保 chromedriver.exe 与生成的 exe 文件在同一目录下。")

if __name__ == '__main__':
    build()


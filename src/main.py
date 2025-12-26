import os
import sys
from math import floor
from pathlib import Path
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import undetected_chromedriver as uc
import logging

# 日志配置
logger = logging.getLogger("kmelearning")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(filename)s:%(lineno)d: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 常量区
VIDEO_SPEED = 1.0  # 视频播放速度


def resource_path(relative_path):
    """ 获取资源的绝对路径，无论是开发环境还是打包环境 """
    try:
        # PyInstaller 创建一个临时文件夹，并把路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_chrome_version():
    """获取本机 Chrome 版本"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        major_version = version.split('.')[0]
        logger.info(f"检测到 Chrome 版本: {version} (主版本: {major_version})")
        return int(major_version)
    except Exception as e:
        logger.warning(f"无法检测 Chrome 版本: {e}")
        return None


def get_driver_path():
    """获取 ChromeDriver 路径（兼容开发和打包环境）"""
    # 判断是否为打包后的环境
    if getattr(sys, 'frozen', False):
        # 打包后：exe 所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境：脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    driver_path = os.path.join(base_path, 'chromedriver.exe')

    if os.path.exists(driver_path):
        logger.info(f"✓ 找到本地 ChromeDriver: {driver_path}")
        return driver_path
    else:
        logger.warning(f"✗ 未找到本地 ChromeDriver: {driver_path}")
        logger.info("将尝试自动下载...")
        return None


def init_driver(options=None):
    """初始化 undetected_chromedriver"""
    try:
        if options is None:
            options = uc.ChromeOptions()

        # 反检测配置
        options.add_argument('--disable-blink-features=AutomationControlled')

        # 获取驱动路径
        driver_path = get_driver_path()

        # 创建驱动
        if driver_path:
            # 使用本地驱动
            driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_path,
                use_subprocess=False
            )
            logger.info("✓ 使用本地 ChromeDriver")
        else:
            # 自动下载驱动（首次运行会较慢）
            driver = uc.Chrome(
                options=options,
                version_main=None,  # 自动检测版本
                use_subprocess=False
            )
            logger.info("✓ 自动下载 ChromeDriver")

        return driver

    except Exception as e:
        logger.error(f"✗ 初始化驱动失败: {e}")
        logger.error("请检查：")
        logger.error("1. Chrome 浏览器是否已安装")
        logger.error("2. chromedriver.exe 是否在程序同目录下")
        logger.error("3. chromedriver.exe 版本是否与 Chrome 匹配")
        raise

def manul_login(driver):
    """手动登录流程"""
    try:
        # undetected_chromedriver 已经自动处理了 webdriver 检测
        # 所以不需要再执行 execute_cdp_cmd

        driver.get("https://pc.kmelearning.com/jsncxyslhs/home/login")
        logger.info("已打开登录页面，请手动完成登录（包括滑块验证）")

        input("登录后在此回车\n")

        try:
            # 等待个人中心元素出现
            dashboard = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="homeIndex"]/div/div[2]/div/div/div/div/div/div[7]/div/div/div/div'))
            )

            if dashboard and dashboard.text == '个人中心':
                dashboard.click()
                logger.info("登录成功！")
                return True
            else:
                logger.error(f"元素文本不符，实际为: '{dashboard.text}'")
                raise Exception("登录页面不正确")
        except Exception as e:
            logger.error(f"查找个人中心元素失败: {e}")
            return False

    except Exception as e:
        logger.error(f"登录流程异常: {e}")
        return False


# ... 其余函数保持不变 ...

def to_my_task(driver):
    try:
        # dashborad = driver.find_element(By.XPATH,
        #                                 '//*[@id="homeIndex"]/div/div[2]/div/div/div/div/div/div[7]/div/div/div/div')
        # dashborad.click()
        # logger.info('打开个人中心')
        # sleep(5)
        # myTaskPage = driver.find_element(By.XPATH,
        #                                  '//*[@id="root"]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div/div[3]/div[2]')
        myTaskPage = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div/div[3]/div[2]'))
        )
        myTaskPage.click()
        logger.info('打开我的任务页面')
        sleep(5)
    except Exception as e:
        logger.error(f"跳转到我的任务页面失败: {e}")


def get_task_list(driver):
    try:
        taskListElements = driver.find_elements(By.CLASS_NAME, 'recommendDetail')
        if not taskListElements:
            logger.info('没有任务列表')
        taskDict = {e.find_element(By.XPATH, ".//div[contains(@class,'recomendName')]/span").text: e for e in
                    taskListElements}
        logger.info(f"任务列表: {list(taskDict.keys())}")
        return taskDict
    except Exception as e:
        logger.error('获取任务列表失败: {}'.format(e))


def to_study(driver, taskElement):
    try:
        lessonName = taskElement.text
        taskElement.click()
        logger.info(f"开始处理任务: {lessonName}")
        sleep(5)
        driver.find_element(By.CLASS_NAME, 'studyButton').click()
        sleep(5)
    except Exception as e:
        logger.error(f"进入学习页面失败: {e}")


def get_lesson_list(driver):
    try:
        lessonList = driver.find_elements(By.CLASS_NAME, 'panelContent')
        if not lessonList:
            logger.info('没有课程列表')
        return lessonList
    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        return []


def get_video_list(driver):
    try:
        videoList = driver.find_elements(By.CLASS_NAME, 'course-chapters-section')
        for v in videoList:
            if '测试题' in v.find_element(By.CLASS_NAME, 'course-chapters-section-name').text:
                videoList.remove(v)
                logger.info(f'存在测试题')
        if not videoList:
            logger.info('没有课程列表')
        return videoList
    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        return []


def handle_task(driver, l_index):
    try:
        lessonList = driver.find_elements(By.CLASS_NAME, 'panelContent')
        current_lesson = lessonList[l_index]
        try:
            current_lesson.find_element(By.TAG_NAME, 'i')
        except Exception:
            handle_lesson(driver, current_lesson)
    except Exception as e:
        logger.error(f"处理任务失败: {e}")


def handle_lesson(driver, lesson):
    try:
        lesson_name = lesson.text
        lesson.click()
        sleep(5)
        logger.info(f"开始学习课程: {lesson_name}")

        videoList = get_video_list(driver)
        logger.info(f"课程包含视频数量: {len(videoList)}")
        for video in videoList:
            try:
                handle_video(driver, video)
            except Exception as e:
                logger.error(
                    f'处理视频{video.find_element(By.CLASS_NAME, "course-chapters-section-name").text}失败: {e}')
        logger.info("课程结束，返回任务列表")
        driver.execute_script("window.scrollTo(0, 0);")
        driver.find_element(By.XPATH, '//*[@id="root"]/div[3]/div/div/div[1]').click()
        sleep(5)
        logger.info(f"完成课程: {lesson_name}")
    except Exception as e:
        logger.error(f"处理课程失败: {e}")
        driver.find_element(By.XPATH, '//*[@id="root"]/div[3]/div/div/div[2]/div/div[1]').click()
        sleep(5)
        logger.info(f"退出课程")


def handle_video(driver, video):
    try:
        video.find_element(By.TAG_NAME, 'g')
        logger.info('跳过已学习的视频')
        pass
    except NoSuchElementException as nsee:
        try:
            video.click()
            play_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'prism-big-play-btn'))
            )
            setSpeed(driver, VIDEO_SPEED)
            control_bar_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "prism-controlbar"))
            )
            new_style = "position: absolute; left: 0px; bottom: 0px; display: blocked;"
            driver.execute_script("arguments[0].style.cssText = arguments[1];",
                                  control_bar_element,
                                  new_style)
            current_time = driver.find_element(By.CLASS_NAME, 'current-time').text
            duration = driver.find_element(By.CLASS_NAME, 'duration').text
            left_time = time_str_to_seconds(duration) - time_str_to_seconds(current_time)
            left_time = round(left_time / VIDEO_SPEED, 0)
            logger.info("课程时间: {}s".format(left_time))
            sleep(left_time + 5)
        except Exception as e:
            logger.error(f"处理视频失败: {e}")
            return


def time_str_to_seconds(time_str):
    parts = list(map(int, time_str.split(":")))
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    else:
        return int(parts[0])


def setSpeed(driver, speed):
    try:
        videoPlayer = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "video[src*='kmelearning.com']"))
        )
        driver.execute_script("arguments[0].play();", videoPlayer)
        driver.execute_script(f"arguments[0].playbackRate = {speed};", videoPlayer)
        logger.info(f"设置视频播放速度为: {speed}x")
    except Exception as e:
        logger.error(f"设置视频播放速度失败: {e}")


def main():
    global VIDEO_SPEED

    try:
        # 初始化驱动（不传入任何options）
        driver = init_driver()
        driver.maximize_window()

        if not manul_login(driver):
            logger.info('发生错误，程序退出')
            return

        to_my_task(driver)
        tasksDict = get_task_list(driver)

        if len(tasksDict) <= 0:
            logger.info('没有任务可执行，程序退出')
            return

        tasksInput = input(f'请选择要执行的任务（输入任务名称，多个任务用逗号分隔）:\n{list(tasksDict.keys())}\n')
        speed = input('请输入视频播放速度（默认1.0）: ')
        VIDEO_SPEED = float(speed) if speed.strip() else 1.0

        tasks = [task.strip() for task in tasksInput.split(',')]
        for task in tasks:
            tasksDict = get_task_list(driver)
            to_study(driver, tasksDict.get(task))
            lessons = get_lesson_list(driver)
            logger.info(driver.find_element(By.CLASS_NAME, 'prograssSpan').text)
            logger.debug(f"课程列表: {[l.find_element(By.CLASS_NAME, 'activityTitle').text for l in lessons]}")
            for i in range(len(lessons)):
                handle_task(driver, i)

        logger.info("所有任务完成！")
        input("按回车键关闭浏览器...")
        driver.quit()

    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        input("按回车键退出...")


if __name__ == '__main__':
    main()
from math import floor
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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


def init_driver(options: Options = None):
    options = Options() if options is None else options
    service = Service(executable_path=r"../driver/chromedriver.exe")
# options = Options()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def manul_login(driver):
    try:
        driver.get("https://pc.kmelearning.com/jsncxyslhs/home/login")
        input("登录后在此回车\n")
        try:
            dashborad = driver.find_element(By.XPATH, '//*[@id="homeIndex"]/div/div[2]/div/div/div/div/div/div[7]/div/div/div/div/div[2]')
        except Exception as e:
            logger.error(f"查找个人中心元素失败: {e}")
            return False
        if dashborad and dashborad.text == '个人中心':
            return True
        else:
            logger.error(f"元素文本不符，实际为: '{dashborad.text}'")
            raise Exception("登录页面不正确")
    except Exception as e:
        logger.error(f"登录流程异常: {e}")
        return False

def to_my_task(driver):
    try:
        dashborad = driver.find_element(By.XPATH,
                                        '//*[@id="homeIndex"]/div/div[2]/div/div/div/div/div/div[7]/div/div/div/div/div[2]')
        dashborad.click()
        logger.info('打开个人中心')
        sleep(5)
        myTaskPage = driver.find_element(By.XPATH,
                                         '//*[@id="root"]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div/div[3]/div[2]')
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
        taskDict = {e.find_element(By.XPATH, ".//div[contains(@class,'recomendName')]/span").text: e for e in taskListElements}
        logger.info(f"任务列表: {list(taskDict.keys())}")
        return taskDict
    except Exception as e:
        logger.error('获取任务列表失败: {}'.format(e))

def to_study(driver,taskElement):
    try:
        lessonName = taskElement.text
        taskElement.click()
        logger.info(f"开始处理任务: {lessonName}")
        # 这里可以添加处理任务的具体逻辑
        sleep(5)  # 模拟处理时间
        driver.find_element(By.CLASS_NAME,
                            'studyButton').click()  # 点击进入学习按钮
        sleep(5)
    except Exception as e:
        logger.error(f"进入学习页面失败: {e}")

def get_lesson_list(driver):
    try:
        lessonList = driver.find_elements(By.CLASS_NAME, 'panelContent')
        # lesson2learn = []
        # for l in lessonList:
        #     if l.find_element(By.CLASS_NAME, 'anticon'):
        #         continue
        #     else:
        #         lesson2learn.append(l.text)
        if not lessonList:
            logger.info('没有课程列表')
        return lessonList
    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        return []

def get_video_list(driver):
    try:
        videoList = driver.find_elements(By.CLASS_NAME, 'course-chapters-section')
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
            # 查找当前课程下的 <i> 标签
            current_lesson.find_element(By.TAG_NAME, 'i')
            # 找到 <i> 标签，跳过
            pass
        except Exception:
            # 没找到 <i> 标签，执行课程处理
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
            handle_video(driver, video)
        logger.info("课程结束，返回任务列表")
        driver.find_element(By.XPATH, '//*[@id="root"]/div[3]/div/div/div[2]/div/div[1]').click()  # 点击返回按钮
        sleep(5)
        logger.info(f"完成课程: {lesson_name}")
    except Exception as e:
        logger.error(f"处理课程失败: {e}")

def handle_video(driver, video):
    """
    处理课程中的多视频
    :param driver: 驱动
    :param video: 视频
    :return:
    """
    try:
        video.find_element(By.TAG_NAME, 'g')
        logger.info('跳过已学习的视频')
        pass

    except NoSuchElementException as nsee:
        try:
            video.click()
            sleep(5)
            play_button = driver.find_element(By.CLASS_NAME, 'prism-big-play-btn')
            play_button.click()
            sleep(2)
            current_time = driver.find_element(By.CLASS_NAME, 'current-time').text
            duration = driver.find_element(By.CLASS_NAME, 'duration').text
            left_time = time_str_to_seconds(duration) - time_str_to_seconds(current_time)
            left_time = round(left_time / VIDEO_SPEED, 0)  # 计算剩余时间，向上取整
            logger.info("课程时间: {}s".format(left_time))
            sleep(left_time + 5)  # 模拟学习时间
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

def main():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = init_driver(options)
    if not manul_login(driver):
        logger.info('发生错误，程序退出')
        return
    to_my_task(driver)
    tasksDict = get_task_list(driver)
    if len(tasksDict) <= 0:
        logger.info('没有任务可执行，程序退出')
        return
    tasksInput = input(f'请选择要执行的任务（输入任务名称，多个任务用逗号分隔）:\n{list(tasksDict.keys())}\n')
    tasks = [task.strip() for task in tasksInput.split(',')]
    for task in tasks:
        tasksDict = get_task_list(driver)
        to_study(driver,tasksDict.get(task))
        lessons = get_lesson_list(driver)
        logger.info(driver.find_element(By.CLASS_NAME, 'prograssSpan').text)
        logger.debug(f"课程列表: {[l.find_element(By.CLASS_NAME, "activityTitle").text for l in lessons]}")
        for i in range(len(lessons)):
            handle_task(driver, i)

if __name__ == '__main__':
    main()

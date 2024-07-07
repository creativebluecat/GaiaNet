from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
import random
from multiprocessing import Process, freeze_support
from nltk.corpus import wordnet
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 加载所有的同义词集
synsets = list(wordnet.all_synsets())

# 函数：生成具有具体含义的随机字符串
def generate_meaningful_string():
    num_words = random.randint(1, 6)  # 随机选择1到6个单词
    random_synsets = random.sample(synsets, num_words)  # 随机选择若干个同义词集

    words = []
    for synset in random_synsets:
        words.extend(synset.lemma_names())  # 获取同义词集中的单词列表

    random_words = random.sample(words, num_words)  # 从单词列表中随机选择若干个单词
    random_string = ' '.join(random_words)  # 将选中的单词连接成一个字符串
    return random_string

# 函数：执行操作的函数
def perform_operations(url):
    retry_attempts = 30  # 设置重试次数
    driver = None  # 初始化浏览器对象

    while retry_attempts > 0:
        try:
            if driver is None:
                # 创建 Chrome 浏览器对象
                driver = webdriver.Chrome()

                # 打开页面
                driver.get(url)

                # 等待页面加载完成
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea.m-0')))

            start_time = time.time()  # 记录开始时间

            while True:
                try:
                    # 处理可能出现的弹框
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()  # 点击弹框上的确定按钮
                    except:
                        pass  # 如果没有弹框，继续执行后续操作

                    # 定位输入框和按钮元素
                    input_box = driver.find_element(By.CSS_SELECTOR, 'textarea.m-0')
                    send_button = driver.find_element(By.CSS_SELECTOR, 'button.inline-flex')

                    # 检查按钮状态
                    button_text = send_button.text
                    is_click = False
                    if button_text == "SEND":
                        print("Button text is 'Send'.")
                        is_click = True
                    elif button_text == "":
                        is_click = False
                        print("Button text is empty.")
                    else:
                        is_click = False
                        print(f"Button text is '{button_text}'.")

                    if  is_click:
                        # 生成具有具体含义的随机字符串
                        random_string = generate_meaningful_string()

                        # 输入生成的随机字符串
                        input_box.clear()
                        input_box.send_keys(random_string)

                        # 点击按钮
                        send_button.click()

                        # 输出日志
                        print(f"在 {url} 上发送消息: {random_string}")

                        # 重置开始时间
                        start_time = time.time()
                    else:
                        # 检查按钮是否超过60秒在旋转
                        if time.time() - start_time > 300:
                            raise WebDriverException(f"{url} 上的按钮一直在旋转超过60秒，视为异常")
                        else:
                            print(f"{url} 上的按钮正在旋转，暂时无法处理")
                            time.sleep(5)  # 等待一段时间后重新检查按钮状态

                except WebDriverException as e:
                    print(f"在 {url} 上执行操作时发生异常: {str(e)}")
                    retry_attempts -= 1  # 减少重试次数
                    time.sleep(5)  # 等待一段时间后重新尝试

                    # 关闭当前的浏览器对象
                    if driver:
                        driver.quit()
                        driver = None
                    break  # 跳出内循环，重新创建浏览器对象

        except TimeoutException:
            print(f"在 {url} 上等待页面加载超时")
            retry_attempts -= 1  # 减少重试次数

            # 关闭当前的浏览器对象
            if driver:
                driver.quit()
                driver = None

        finally:
            # 关闭浏览器
            if driver:
                driver.quit()

# 要操作的多个URL列表
urls = [
    # 添加更多的URL
]

if __name__ == '__main__':
    freeze_support()  # 在Windows下确保子进程能够正确启动

    # 使用多进程执行每个URL上的操作
    processes = []
    for url in urls:
        p = Process(target=perform_operations, args=(url,))
        processes.append(p)
        p.start()

    # 等待所有进程完成
    for p in processes:
        p.join()

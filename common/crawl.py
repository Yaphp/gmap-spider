import os
import time
from selenium import webdriver
from common.bucket import upload
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.util import get_location_by_coordinates
from config.config import R2_BUCKET, R2_PUBLIC_URL, API_URL


def get_driver():
    # 配置参数
    option = webdriver.EdgeOptions()

    # 开启无头模式（可选）
    # option.add_argument('--headless')

    # 设置全屏
    option.add_argument("--start-maximized")

    # 设置分辨率
    option.add_argument('--window-size=2560,1440')

    # 设置设备缩放比例
    option.add_argument("--force-device-scale-factor=1.25")

    # 禁用一些不必要的功能以提高性能
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-plugins")
    option.add_argument("--disable-images")  # 可选：如果不需要加载图片

    driver = webdriver.Edge(options=option)
    return driver


def get_element_screenshot(driver, element_selector, filename):
    """截取特定元素的截图，进一步减少白边"""
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, element_selector))
        )
        element.screenshot(filename)
        return filename
    except:
        print(f"无法找到元素 {element_selector}，使用全屏截图")
        return save_full_screenshot(driver, filename)


def save_full_screenshot(driver, filename):
    """保存全屏截图"""
    driver.save_screenshot(filename)
    return filename


def get_map_detail(session, items):
    """
    获取地图详情
    :param session:
    :param items:
    :return:
    """
    driver = get_driver()

    try:
        for item in items:
            driver.get(item["sourceUrl"])
            print(f"正在加载页面: {item['sourceUrl']}")

            # 等待页面主要元素加载完成
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "scene"))
                )
            except:
                print("页面加载超时，继续执行...")

            # 额外等待确保所有元素渲染完成
            time.sleep(3)

            print("页面加载完成，开始隐藏UI元素")

            # 更全面的隐藏脚本
            hide_script = '''
                // 隐藏搜索框
                var omnibox = document.querySelector("#omnibox");
                if (omnibox) omnibox.style.display = "none";

                // 隐藏标题卡片
                var titlecard = document.querySelector("#titlecard");
                if (titlecard) titlecard.style.display = "none";

                // 隐藏图片头部
                var imageHeader = document.querySelector("#image-header");
                if (imageHeader) imageHeader.style.display = "none";

                // 隐藏底部内容
                var bottomContent = document.querySelector("#content-container > div.app-viewcard-strip");
                if (bottomContent) bottomContent.style.display = "none";

                // 隐藏页脚
                var footer = document.querySelector("#content-container > div.scene-footer-container");
                if (footer) footer.style.display = "none";

                // 隐藏小地图
                var minimap = document.querySelector("#minimap");
                if (minimap) minimap.style.display = "none";

                // 隐藏所有可能的控制面板
                var controls = document.querySelectorAll('.app-viewcard-strip, .scene-footer-container, .titlecard, .omnibox-container');
                controls.forEach(function(el) {
                    if (el) el.style.display = "none";
                });

                // 隐藏导航控件
                var navControls = document.querySelector('.widget-scene-canvas-controls');
                if (navControls) navControls.style.display = "none";

                // 隐藏左上角的返回按钮等
                var backButton = document.querySelector('.widget-pane-toggle-button');
                if (backButton) backButton.style.display = "none";

                // 隐藏右下角的版权信息
                var copyright = document.querySelector('.app-copyright-control');
                if (copyright) copyright.style.display = "none";

                // 隐藏其他可能的UI元素
                var uiElements = document.querySelectorAll('.widget-scene-canvas-controls, .widget-compass, .widget-zoom, .gm-bundled-control');
                uiElements.forEach(function(el) {
                    if (el) el.style.display = "none";
                });

                console.log("UI元素隐藏完成");
            '''

            driver.execute_script(hide_script)

            # 再等待一下确保脚本执行完成
            time.sleep(2)

            print("脚本执行完成")

            # 提取坐标信息
            try:
                coords = item["sourceUrl"].split("@")[1].split(",")[0:2]
                item["lat"] = float(coords[0])
                item["lng"] = float(coords[1])
                # name = "_".join(coords)
                name = str(int(time.time()))

                address_dict = get_location_by_coordinates(coords[0], coords[1])
                item["country"] = address_dict["country"]
                item["city"] = address_dict["city"]

            except IndexError:
                # 如果无法提取坐标，使用时间戳作为文件名
                print("无法提取坐标信息")
                name = str(int(time.time()))
                item["lat"] = 0
                item["lng"] = 0
                item["country"] = ""
                item["city"] = ""

            print(f"基础信息采集:{item}")

            # 确保images文件夹存在
            if not os.path.exists("./images"):
                os.makedirs("./images")

            print("开始截图")

            # 截图前可以尝试调整窗口大小以减少白边
            driver.set_window_size(1920, 1080)  # 设置标准分辨率
            time.sleep(1)

            save_name = save_full_screenshot(driver, f"./images/{name}.png")
            print(f"截图成功: {save_name}")

            # 公共访问链接
            object_key = f"images/streetview/{name}.png"

            res, url = upload(R2_PUBLIC_URL, save_name, object_key, R2_BUCKET)

            if not res:
                print(f"图片上传失败: {save_name}")
                continue

            item["url"] = url

            # 提交数据
            resp = session.put(API_URL + "/api/panorama", json=item).json()

            if not resp.get("success"):
                print(f"数据提交失败: {item['id']}")
                print(resp)
                continue

            print(f"数据提交成功: {item['id']}")

    finally:
        driver.quit()


# 使用示例
if __name__ == "__main__":
    test_items = [
        {
            "sourceUrl": "https://www.google.com/maps/@40.6888885,-74.0441666,3a,75y,90t/data=!3m8!1e1!3m6!1sAF1QipPZ8GX5sKvPr4RIgbGm4t8_q8hJ8r8vJ5G6I6fJ!2e10!3e11!6shttps:%2F%2Flh5.googleusercontent.com%2Fp%2FAF1QipPZ8GX5sKvPr4RIgbGm4t8_q8hJ8r8vJ5G6I6fJ%3Dw203-h100-k-no-pi-0-ya56.389084-ro-0-fo100!7i11264!8i5632"
        }
    ]

    get_map_detail(test_items)

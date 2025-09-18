#!/usr/bin/env python3
"""
测试钓鱼网站检测系统的模态框功能
"""
import asyncio
from playwright.async_api import async_playwright

async def test_modal():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 访问网站
        print("正在访问网站...")
        await page.goto("http://localhost:5000")

        # 等待页面加载
        await page.wait_for_selector('input[name="url"]')

        # 输入测试URL
        print("输入测试URL...")
        await page.fill('input[name="url"]', 'http://example.com')

        # 点击分析按钮
        print("点击分析按钮...")
        await page.click('button[type="submit"]')

        # 等待结果显示
        print("等待分析结果...")
        await page.wait_for_selector('#resultSection', state='visible', timeout=30000)

        # 等待几秒钟确保数据加载完成
        await page.wait_for_timeout(2000)

        # 检查结果区域是否可见
        result_visible = await page.is_visible('#resultSection')
        print(f"结果区域是否可见: {result_visible}")

        # 尝试点击详细分析按钮
        print("尝试点击详细分析按钮...")
        detail_button = await page.query_selector('button[onclick="showDetailedModal()"]')

        if detail_button:
            print("找到详细分析按钮，尝试点击...")
            await detail_button.click()

            # 等待模态框显示
            print("等待模态框显示...")
            await page.wait_for_timeout(2000)

            # 检查模态框是否可见
            modal_visible = await page.is_visible('#detailedAnalysisModal')
            print(f"模态框是否可见: {modal_visible}")

            # 检查模态框是否具有show类
            modal_has_show = await page.evaluate('''
                () => {
                    const modal = document.getElementById('detailedAnalysisModal');
                    return modal && modal.classList.contains('show');
                }
            ''')
            print(f"模态框是否具有show类: {modal_has_show}")

            # 检查是否有modal-backdrop
            backdrop_visible = await page.is_visible('.modal-backdrop')
            print(f"背景遮罩是否可见: {backdrop_visible}")

            # 检查body是否有modal-open类
            body_has_modal_open = await page.evaluate('''
                () => {
                    return document.body.classList.contains('modal-open');
                }
            ''')
            print(f"body是否有modal-open类: {body_has_modal_open}")

            # 检查页面是否可滚动
            body_overflow = await page.evaluate('''
                () => {
                    return window.getComputedStyle(document.body).overflow;
                }
            ''')
            print(f"body的overflow属性: {body_overflow}")

            # 尝试关闭模态框
            print("尝试关闭模态框...")
            # 使用JavaScript点击关闭按钮
            close_result = await page.evaluate('''
                () => {
                    const closeBtn = document.querySelector('#detailedAnalysisModal .btn-close');
                    if (closeBtn) {
                        closeBtn.click();
                        return true;
                    }
                    return false;
                }
            ''')
            await page.wait_for_timeout(1000)
            print(f"模态框关闭结果: {close_result}")

            # 检查关闭后的状态
            modal_visible_after_close = await page.is_visible('#detailedAnalysisModal')
            print(f"关闭后模态框是否可见: {modal_visible_after_close}")

            # 再次检查body的modal-open类
            body_has_modal_open_after = await page.evaluate('''
                () => {
                    return document.body.classList.contains('modal-open');
                }
            ''')
            print(f"关闭后body是否有modal-open类: {body_has_modal_open_after}")

        else:
            print("未找到详细分析按钮")

        # 截图保存
        await page.screenshot(path='test_result.png')
        print("截图已保存为 test_result.png")

        # 等待一下保存结果
        await page.wait_for_timeout(2000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_modal())
#!/usr/bin/env python3
"""
专门测试导出功能
"""
import asyncio
from playwright.async_api import async_playwright

async def test_export_function():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("http://localhost:5000")
        await page.wait_for_selector('input[name="url"]')

        # 输入URL并提交
        await page.fill('input[name="url"]', 'http://example.com')
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#resultSection', state='visible', timeout=30000)
        await page.wait_for_timeout(2000)

        print("=== 导出功能测试 ===")

        # 打开模态框
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        # 测试导出功能
        print("1. 测试导出按钮...")
        try:
            # 监听下载事件
            async with page.expect_download() as download_info:
                # 使用JavaScript点击导出按钮
                export_result = await page.evaluate('''
                    () => {
                        const exportBtn = document.querySelector('button[onclick="exportReport()"]');
                        if (exportBtn) {
                            exportBtn.click();
                            return true;
                        }
                        return false;
                    }
                ''')

            download = await download_info.value
            print(f"✅ 导出按钮点击成功: {export_result}")
            print(f"✅ 文件名: {download.suggested_filename}")
            print(f"✅ 文件URL: {download.url}")

        except Exception as e:
            print(f"❌ 导出测试失败: {e}")

        # 测试关闭按钮
        print("\n2. 测试关闭按钮...")
        try:
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
            modal_visible = await page.is_visible('#detailedAnalysisModal')
            print(f"✅ 关闭按钮点击结果: {close_result}")
            print(f"✅ 关闭后模态框可见: {modal_visible}")
        except Exception as e:
            print(f"❌ 关闭按钮测试失败: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_export_function())
#!/usr/bin/env python3
"""
专门测试关闭按钮功能
"""
import asyncio
from playwright.async_api import async_playwright

async def close_button_test():
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

        print("=== 关闭按钮专项测试 ===")

        # 打开模态框
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        modal_visible = await page.is_visible('#detailedAnalysisModal')
        print(f"模态框已打开: {modal_visible}")

        # 使用JavaScript来点击关闭按钮（绕过指针事件问题）
        print("尝试使用JavaScript点击关闭按钮...")
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

            modal_visible_after = await page.is_visible('#detailedAnalysisModal')
            print(f"JavaScript点击后模态框可见: {modal_visible_after}")
            print(f"JavaScript点击结果: {close_result}")

            if not modal_visible_after:
                print("✅ 关闭按钮JavaScript点击成功！")
            else:
                print("❌ 关闭按钮JavaScript点击失败")

        except Exception as e:
            print(f"❌ JavaScript点击测试失败: {e}")

        # 重新打开模态框
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        # 测试Bootstrap API关闭
        print("\n测试Bootstrap API关闭...")
        try:
            bootstrap_result = await page.evaluate('''
                () => {
                    const modalElement = document.getElementById('detailedAnalysisModal');
                    if (modalElement) {
                        const modal = bootstrap.Modal.getInstance(modalElement);
                        if (modal) {
                            modal.hide();
                            return true;
                        }
                    }
                    return false;
                }
            ''')

            await page.wait_for_timeout(1000)

            modal_visible_bootstrap = await page.is_visible('#detailedAnalysisModal')
            print(f"Bootstrap API关闭后模态框可见: {modal_visible_bootstrap}")
            print(f"Bootstrap API关闭结果: {bootstrap_result}")

            if not modal_visible_bootstrap:
                print("✅ Bootstrap API关闭成功！")
            else:
                print("❌ Bootstrap API关闭失败")

        except Exception as e:
            print(f"❌ Bootstrap API关闭测试失败: {e}")

        # 最终状态检查
        await page.wait_for_timeout(500)
        final_modal_state = await page.is_visible('#detailedAnalysisModal')
        print(f"\n最终模态框状态: {'已关闭' if not final_modal_state else '仍显示'}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(close_button_test())
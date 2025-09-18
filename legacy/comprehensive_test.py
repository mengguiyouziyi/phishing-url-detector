#!/usr/bin/env python3
"""
全面测试模态框功能
"""
import asyncio
from playwright.async_api import async_playwright

async def comprehensive_test():
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

        print("=== 测试1: 模态框显示 ===")
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        modal_visible = await page.is_visible('#detailedAnalysisModal')
        modal_has_show = await page.evaluate('document.getElementById("detailedAnalysisModal").classList.contains("show")')
        backdrop_visible = await page.is_visible('.modal-backdrop')

        print(f"✓ 模态框可见: {modal_visible}")
        print(f"✓ 模态框有show类: {modal_has_show}")
        print(f"✓ 背景遮罩可见: {backdrop_visible}")

        print("\n=== 测试2: ESC键关闭 ===")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(1000)

        modal_visible_after = await page.is_visible('#detailedAnalysisModal')
        modal_has_show_after = await page.evaluate('document.getElementById("detailedAnalysisModal").classList.contains("show")')
        backdrop_visible_after = await page.is_visible('.modal-backdrop')

        print(f"✓ ESC后模态框可见: {modal_visible_after}")
        print(f"✓ ESC后模态框有show类: {modal_has_show_after}")
        print(f"✓ ESC后背景遮罩可见: {backdrop_visible_after}")

        print("\n=== 测试3: 重新打开模态框 ===")
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        modal_visible_reopen = await page.is_visible('#detailedAnalysisModal')
        print(f"✓ 重新打开模态框可见: {modal_visible_reopen}")

        print("\n=== 测试4: 关闭按钮 ===")
        try:
            # 等待关闭按钮可点击
            close_button = await page.wait_for_selector('#detailedAnalysisModal .btn-close', timeout=5000)
            await close_button.click()
            await page.wait_for_timeout(1000)

            modal_visible_close = await page.is_visible('#detailedAnalysisModal')
            print(f"✓ 关闭按钮点击后模态框可见: {modal_visible_close}")

            if modal_visible_close == False:
                print("✓ 关闭按钮工作正常")
            else:
                print("✗ 关闭按钮不工作")

        except Exception as e:
            print(f"✗ 关闭按钮测试失败: {e}")

        print("\n=== 测试5: 再次打开模态框 ===")
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        print("\n=== 测试6: 数据内容 ===")
        # 检查模态框是否有数据
        risk_score = await page.evaluate('document.getElementById("modalRiskScore").textContent')
        safety_score = await page.evaluate('document.getElementById("modalSafetyScore").textContent')

        print(f"✓ 风险分数显示: {risk_score}")
        print(f"✓ 安全分数显示: {safety_score}")

        # 检查特征表格
        feature_rows = await page.evaluate('document.querySelectorAll("#modalFeatureTable tr").length')
        print(f"✓ 特征表格行数: {feature_rows}")

        # 检查导出按钮是否存在
        export_button = await page.is_visible('button[onclick="exportReport()"]')
        print(f"✓ 导出按钮可见: {export_button}")

        print("\n=== 测试7: 最终关闭 ===")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(1000)

        final_modal_visible = await page.is_visible('#detailedAnalysisModal')
        print(f"✓ 最终模态框状态: {'关闭' if not final_modal_visible else '未关闭'}")

        # 截图
        await page.screenshot(path='comprehensive_test.png')
        print("\n截图已保存为 comprehensive_test.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(comprehensive_test())
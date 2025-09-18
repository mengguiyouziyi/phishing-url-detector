#!/usr/bin/env python3
"""
专门测试弹窗问题：关闭按钮、导出按钮、特征列表滚动
"""
import asyncio
from playwright.async_api import async_playwright

async def test_modal_issues():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # 使用无界面模式
        page = await browser.new_page()

        await page.goto("http://localhost:5000")
        await page.wait_for_selector('input[name="url"]')

        # 输入URL并提交
        await page.fill('input[name="url"]', 'http://example.com')
        await page.click('button[type="submit"]')
        await page.wait_for_selector('#resultSection', state='visible', timeout=30000)
        await page.wait_for_timeout(2000)

        print("=== 弹窗问题测试 ===")

        # 打开模态框
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        # 1. 测试关闭按钮可见性
        print("1. 检查关闭按钮可见性...")
        close_button = await page.query_selector('#detailedAnalysisModal .btn-close')
        if close_button:
            is_visible = await close_button.is_visible()
            print(f"✅ 关闭按钮可见: {is_visible}")

            # 获取关闭按钮的位置和大小
            bbox = await close_button.bounding_box()
            if bbox:
                print(f"✅ 关闭按钮位置: x={bbox['x']}, y={bbox['y']}, 宽={bbox['width']}, 高={bbox['height']}")
            else:
                print("❌ 无法获取关闭按钮位置")
        else:
            print("❌ 未找到关闭按钮")

        # 2. 测试导出按钮
        print("\n2. 检查导出按钮...")
        export_buttons = await page.query_selector_all('#detailedAnalysisModal button[onclick*="exportReport"]')
        print(f"✅ 找到 {len(export_buttons)} 个导出按钮")

        for i, btn in enumerate(export_buttons):
            is_visible = await btn.is_visible()
            bbox = await btn.bounding_box()
            print(f"   导出按钮{i+1}: 可见={is_visible}, 位置={bbox if bbox else '无法获取'}")

        # 3. 测试特征表格滚动
        print("\n3. 检查特征表格滚动...")
        feature_table = await page.query_selector('#modalFeatureTable')
        if feature_table:
            # 检查表格是否需要滚动
            table_height = await page.evaluate('element => element.scrollHeight', feature_table)
            table_visible_height = await page.evaluate('element => element.clientHeight', feature_table)
            print(f"✅ 特征表格总高度: {table_height}")
            print(f"✅ 特征表格可见高度: {table_visible_height}")
            print(f"✅ 是否需要滚动: {table_height > table_visible_height}")

            if table_height > table_visible_height:
                # 尝试滚动
                try:
                    await feature_table.evaluate('element => element.scrollTop = element.scrollHeight / 2')
                    await page.wait_for_timeout(1000)
                    scroll_top = await page.evaluate('element => element.scrollTop', feature_table)
                    print(f"✅ 滚动测试成功，scrollTop: {scroll_top}")
                except Exception as e:
                    print(f"❌ 滚动测试失败: {e}")
        else:
            print("❌ 未找到特征表格")

        # 4. 尝试点击关闭按钮（使用JavaScript）
        print("\n4. 测试关闭按钮点击...")
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
            print(f"✅ JavaScript点击结果: {close_result}")
            print(f"✅ 点击后模态框是否可见: {modal_visible}")
        except Exception as e:
            print(f"❌ 关闭按钮点击测试失败: {e}")

        # 5. 截图保存
        await page.screenshot(path='modal_issues_test.png')
        print(f"\n✅ 截图已保存: modal_issues_test.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_modal_issues())
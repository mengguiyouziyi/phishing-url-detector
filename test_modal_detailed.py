#!/usr/bin/env python3
"""
详细测试模态框显示问题
"""
import asyncio
from playwright.async_api import async_playwright

async def test_modal_detailed():
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

        print("=== 详细模态框测试 ===")

        # 打开模态框
        await page.click('button[onclick="showDetailedModal()"]')
        await page.wait_for_timeout(2000)

        # 检查模态框和按钮的位置信息
        print("1. 模态框位置信息:")
        modal = await page.query_selector('#detailedAnalysisModal')
        if modal:
            modal_bbox = await modal.bounding_box()
            print(f"   模态框: x={modal_bbox['x']}, y={modal_bbox['y']}, 宽={modal_bbox['width']}, 高={modal_bbox['height']}")

        print("\n2. 关闭按钮位置信息:")
        close_btn = await page.query_selector('#detailedAnalysisModal .btn-close')
        if close_btn:
            close_bbox = await close_btn.bounding_box()
            print(f"   关闭按钮: x={close_bbox['x']}, y={close_bbox['y']}, 宽={close_bbox['width']}, 高={close_bbox['height']}")

        print("\n3. 模态框内容区域信息:")
        modal_content = await page.query_selector('#detailedAnalysisModal .modal-content')
        if modal_content:
            content_bbox = await modal_content.bounding_box()
            print(f"   内容区域: x={content_bbox['x']}, y={content_bbox['y']}, 宽={content_bbox['width']}, 高={content_bbox['height']}")

        print("\n4. 模态框头部信息:")
        modal_header = await page.query_selector('#detailedAnalysisModal .modal-header')
        if modal_header:
            header_bbox = await modal_header.bounding_box()
            print(f"   头部区域: x={header_bbox['x']}, y={header_bbox['y']}, 宽={header_bbox['width']}, 高={header_bbox['height']}")

        print("\n5. 视口信息:")
        viewport = await page.viewport_size()
        print(f"   视口大小: {viewport}")

        print("\n6. 检查滚动情况:")
        # 检查模态框body的滚动
        modal_body = await page.query_selector('#detailedAnalysisModal .modal-body')
        if modal_body:
            body_scroll_height = await page.evaluate('element => element.scrollHeight', modal_body)
            body_client_height = await page.evaluate('element => element.clientHeight', modal_body)
            body_scroll_top = await page.evaluate('element => element.scrollTop', modal_body)
            print(f"   模态框body: scrollHeight={body_scroll_height}, clientHeight={body_client_height}, scrollTop={body_scroll_top}")

        print("\n7. 测试导出按钮点击:")
        try:
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
            print(f"   导出按钮点击结果: {export_result}")
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"   导出按钮点击失败: {e}")

        print("\n8. 测试ESC键关闭:")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(1000)
        modal_visible = await page.is_visible('#detailedAnalysisModal')
        print(f"   ESC键关闭后模态框可见: {modal_visible}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_modal_detailed())
#!/usr/bin/env python3
"""
真实用户体验测试 - 模拟真实用户操作流程
"""
import asyncio
from playwright.async_api import async_playwright

async def user_experience_test():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)  # 使用无界面模式
        page = await browser.new_page()

        print("=== 钓鱼网站检测系统用户体验测试 ===")
        print("浏览器已启动，开始测试...")

        try:
            # 访问网站
            print("1. 访问网站...")
            await page.goto("http://localhost:5000")
            await page.wait_for_selector('input[name="url"]', timeout=10000)
            print("✅ 网站加载成功")

            # 等待一下让用户看到页面
            await page.wait_for_timeout(2000)

            # 输入测试URL
            print("2. 输入测试URL...")
            await page.fill('input[name="url"]', 'http://example.com')
            print("✅ URL输入完成")

            await page.wait_for_timeout(1000)

            # 点击分析按钮
            print("3. 点击分析按钮...")
            await page.click('button[type="submit"]')
            print("✅ 分析按钮已点击")

            # 等待分析结果
            print("4. 等待分析结果...")
            await page.wait_for_selector('#resultSection', state='visible', timeout=30000)
            print("✅ 分析结果显示")

            await page.wait_for_timeout(2000)

            # 检查结果内容
            result_title = await page.evaluate('document.getElementById("resultTitle").textContent')
            print(f"✅ 分析结果: {result_title}")

            confidence_text = await page.evaluate('document.getElementById("confidenceText").textContent')
            print(f"✅ 置信度: {confidence_text}")

            await page.wait_for_timeout(2000)

            # 尝试点击详细分析按钮
            print("5. 点击详细分析按钮...")
            detail_button = await page.query_selector('button[onclick="showDetailedModal()"]')

            if detail_button:
                await detail_button.click()
                print("✅ 详细分析按钮已点击")

                # 等待模态框显示
                await page.wait_for_timeout(3000)

                # 检查模态框状态
                modal_visible = await page.is_visible('#detailedAnalysisModal')
                modal_has_show = await page.evaluate('document.getElementById("detailedAnalysisModal").classList.contains("show")')

                print(f"✅ 模态框可见: {modal_visible}")
                print(f"✅ 模态框激活: {modal_has_show}")

                if modal_visible and modal_has_show:
                    print("✅ 模态框正常打开！")

                    # 检查模态框内容
                    risk_score = await page.evaluate('document.getElementById("modalRiskScore").textContent')
                    safety_score = await page.evaluate('document.getElementById("modalSafetyScore").textContent')
                    print(f"✅ 风险分数: {risk_score}")
                    print(f"✅ 安全分数: {safety_score}")

                    # 检查特征表格
                    feature_rows = await page.evaluate('document.querySelectorAll("#modalFeatureTable tr").length')
                    print(f"✅ 特征分析: {feature_rows}行数据")

                    await page.wait_for_timeout(3000)

                    # 测试关闭按钮
                    print("6. 测试关闭按钮...")
                    close_button = await page.query_selector('#detailedAnalysisModal .btn-close')

                    if close_button:
                        print("找到关闭按钮，尝试点击...")
                        try:
                            await close_button.click(timeout=5000)
                            await page.wait_for_timeout(2000)

                            modal_visible_after = await page.is_visible('#detailedAnalysisModal')
                            if not modal_visible_after:
                                print("✅ 关闭按钮点击成功！模态框已关闭")
                            else:
                                print("❌ 关闭按钮点击失败，模态框仍显示")
                        except Exception as e:
                            print(f"❌ 关闭按钮点击异常: {e}")
                    else:
                        print("❌ 未找到关闭按钮")

                else:
                    print("❌ 模态框未正常打开")

            else:
                print("❌ 未找到详细分析按钮")

            # 截图保存结果
            await page.screenshot(path='user_experience_test.png')
            print("\n✅ 测试完成！截图已保存: user_experience_test.png")

        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()
            print("浏览器已关闭")

if __name__ == "__main__":
    asyncio.run(user_experience_test())
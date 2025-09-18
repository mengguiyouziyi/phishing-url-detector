import { test, expect } from '@playwright/test';

test.describe('Phishing Detection UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://192.168.1.246:5000');
  });

  test('should load Chinese interface correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/高级钓鱼网站检测系统/);

    // Check for Chinese elements
    await expect(page.locator('.hero-title')).toContainText('高级钓鱼网站检测系统');
    await expect(page.locator('text=机器学习')).toBeVisible();
    await expect(page.locator('text=实时分析')).toBeVisible();
    await expect(page.locator('text=置信度评分')).toBeVisible();
  });

  test('should show loading state during analysis', async ({ page }) => {
    await page.fill('#url', 'https://test-url.com');
    await page.click('#urlForm button[type="submit"]');

    // Check loading indicator appears
    await expect(page.locator('#loading')).toBeVisible();
    await expect(page.locator('#loading')).toContainText('正在分析URL');
  });

  test('should display results after analysis', async ({ page }) => {
    await page.fill('#url', 'https://google.com');
    await page.click('#urlForm button[type="submit"]');

    // Wait for results to appear
    await expect(page.locator('#resultSection')).toBeVisible({ timeout: 20000 });
    await expect(page.locator('#analyzedUrl')).toContainText('google.com');

    // Check confidence display
    await expect(page.locator('#confidenceText')).toBeVisible();
  });

  test('should handle URL validation', async ({ page }) => {
    // Test with invalid URL
    await page.fill('#url', 'not-a-valid-url');
    await page.click('#urlForm button[type="submit"]');

    // Should not submit or show validation error
    const urlInput = page.locator('#url');
    await expect(urlInput).toHaveAttribute('required');
  });

  test('should show statistics', async ({ page }) => {
    // Check initial statistics
    await expect(page.locator('#safeCount')).toHaveText('0');
    await expect(page.locator('#dangerCount')).toHaveText('0');
    await expect(page.locator('#avgTime')).toHaveText('0秒');
  });

  test('should update statistics after analysis', async ({ page }) => {
    await page.fill('#url', 'https://github.com');
    await page.click('#urlForm button[type="submit"]');

    // Wait for analysis to complete
    await expect(page.locator('#resultSection')).toBeVisible({ timeout: 20000 });

    // Statistics should be updated
    await expect(page.locator('#safeCount')).not.toHaveText('0');
    await expect(page.locator('#avgTime')).not.toHaveText('0秒');
  });

  test('should have functional reset button', async ({ page }) => {
    await page.fill('#url', 'https://test-url.com');
    await page.click('#urlForm button[type="submit"]');

    // Wait for results
    await expect(page.locator('#resultSection')).toBeVisible({ timeout: 20000 });

    // Click reset button
    await page.click('text=分析其他URL');

    // Results should be hidden
    await expect(page.locator('#resultSection')).toBeHidden();
    await expect(page.locator('#loading')).toBeHidden();
    await expect(page.locator('#url')).toHaveValue('');
  });

  test('should show proceed link with analyzed URL', async ({ page }) => {
    const testUrl = 'https://example.com';
    await page.fill('#url', testUrl);
    await page.click('#urlForm button[type="submit"]');

    await expect(page.locator('#resultSection')).toBeVisible({ timeout: 20000 });

    // Check proceed link
    const proceedLink = page.locator('#proceedBtn');
    await expect(proceedLink).toBeVisible();
    await expect(proceedLink).toHaveAttribute('href', testUrl);
  });

  test('should display feature cards correctly', async ({ page }) => {
    // Check all feature cards are visible
    await expect(page.locator('text=机器学习')).toBeVisible();
    await expect(page.locator('text=实时分析')).toBeVisible();
    await expect(page.locator('text=置信度评分')).toBeVisible();

    // Check for icons
    await expect(page.locator('.feature-icon')).toHaveCount(3);
  });

  test('should handle multiple consecutive analyses', async ({ page }) => {
    const urls = ['https://google.com', 'https://github.com'];

    for (const url of urls) {
      await page.fill('#url', url);
      await page.click('#urlForm button[type="submit"]');

      await expect(page.locator('#resultSection')).toBeVisible({ timeout: 20000 });
      await expect(page.locator('#analyzedUrl')).toContainText(url);

      // Reset for next test
      await page.click('text=分析其他URL');
      await expect(page.locator('#resultSection')).toBeHidden();
    }
  });
});
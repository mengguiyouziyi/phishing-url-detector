import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('should handle multiple concurrent requests', async ({ request }) => {
    const urls = [
      'https://google.com',
      'https://github.com',
      'https://stackoverflow.com'
    ];

    const requests = urls.map(url =>
      request.post('http://192.168.1.246:5000/analyze', {
        form: { url }
      })
    );

    const responses = await Promise.all(requests);

    for (const response of responses) {
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data).toHaveProperty('xx');
      expect(data).toHaveProperty('url');
    }
  });

  test('should complete analysis within reasonable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('http://192.168.1.246:5000');
    await page.fill('#url', 'https://google.com');
    await page.click('#urlForm button[type="submit"]');

    await expect(page.locator('#resultSection')).toBeVisible({ timeout: 30000 });

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Analysis should complete within 30 seconds
    expect(duration).toBeLessThan(30000);
    console.log(`Analysis completed in ${duration}ms`);
  });

  test('should handle timeout scenarios gracefully', async ({ request }) => {
    // Test with a URL that might timeout
    const response = await request.post('http://192.168.1.246:5000/analyze', {
      form: {
        url: 'http://this-domain-probably-does-not-exist-12345.com'
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();

    // Should return an error or confidence score
    expect(data).toHaveProperty('xx');
    expect(typeof data.xx).toBe('number');
  });
});
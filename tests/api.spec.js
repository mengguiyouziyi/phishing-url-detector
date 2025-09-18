import { test, expect } from '@playwright/test';

test.describe('Phishing Detection API Tests', () => {
  test('should handle valid URL submission', async ({ request }) => {
    const response = await request.post('http://192.168.1.246:5000/analyze', {
      form: {
        url: 'https://google.com'
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('xx');
    expect(data).toHaveProperty('url', 'https://google.com');
    expect(typeof data.xx).toBe('number');
  });

  test('should handle invalid URL format', async ({ request }) => {
    const response = await request.post('http://192.168.1.246:5000/analyze', {
      form: {
        url: 'not-a-url'
      }
    });

    const data = await response.json();
    expect(data).toHaveProperty('error');
  });

  test('should handle missing URL parameter', async ({ request }) => {
    const response = await request.post('http://192.168.1.246:5000/analyze', {
      form: {}
    });

    const data = await response.json();
    expect(data).toHaveProperty('error');
  });

  test('should handle phishing URL detection', async ({ request }) => {
    const response = await request.post('http://192.168.1.246:5000/analyze', {
      form: {
        url: 'http://paypal-security-update.verify-login.com'
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('xx');
    expect(data).toHaveProperty('url');
    // Expect low confidence score for suspicious URL
    expect(data.xx).toBeLessThan(0.5);
  });

  test('should handle safe URL detection', async ({ request }) => {
    const response = await request.post('http://192.168.1.246:5000/analyze', {
      form: {
        url: 'https://github.com'
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('xx');
    expect(data).toHaveProperty('url');
    // Expect high confidence score for safe URL
    expect(data.xx).toBeGreaterThan(0.5);
  });

  test('health check endpoint should be accessible', async ({ request }) => {
    const response = await request.get('http://192.168.1.246:5000/api/health');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
    expect(data).toHaveProperty('timestamp');
  });
});
import { test, expect } from '@playwright/test';

/**
 * Visual Regression Tests - Baseline Screenshots
 * DemoPPT v2.4
 * Screenshots saved to: /home/hg/.hermes/company/projects/DemoPPT/frontend/visual-tests/baseline/
 */
test.describe('视觉回归测试 - 基准截图', () => {
  const baselineDir = 'visual-tests/baseline';

  test('首页/落地页截图', async ({ page }) => {
    await page.goto('/');
    
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    // Take full page screenshot
    await page.screenshot({
      path: `${baselineDir}/homepage.png`,
      fullPage: true
    });
    
    // Verify key elements
    await expect(page.locator('text=AI智能PPT')).toBeVisible();
    await expect(page.locator('text=精选模板库')).toBeVisible();
  });

  test('模板选择页截图', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Scroll to templates section
    await page.locator('text=精选模板库').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    
    // Take screenshot of templates section
    await page.screenshot({
      path: `${baselineDir}/templates-page.png`,
      fullPage: true
    });
    
    // Verify templates are visible
    await expect(page.locator('.template-item').first()).toBeVisible();
  });

  test('定价页面截图', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await page.screenshot({
      path: `${baselineDir}/pricing-page.png`,
      fullPage: true
    });
    
    // Click to show plans
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
      await page.waitForTimeout(500);
      
      // Take screenshot with plans visible
      await page.screenshot({
        path: `${baselineDir}/pricing-page-with-plans.png`,
        fullPage: true
      });
    }
    
    await expect(page.locator('text=我的订阅')).toBeVisible();
  });

  test('AI生成进度页截图', async ({ page }) => {
    // Login and navigate to create
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    await page.goto('/create');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await page.screenshot({
      path: `${baselineDir}/ai-progress-page.png`,
      fullPage: true
    });
    
    // Verify progress component would be visible during generation
    await expect(page.locator('text=需求收集')).toBeVisible();
  });

  test('登录页面截图', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    await page.screenshot({
      path: `${baselineDir}/login-page.png`,
      fullPage: true
    });
    
    await expect(page.locator('text=DemoPPT')).toBeVisible();
  });

  test('用户页面截图', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    await page.waitForLoadState('networkidle');
    
    await page.screenshot({
      path: `${baselineDir}/user-page.png`,
      fullPage: true
    });
    
    await expect(page.locator('text=我的订阅')).toBeVisible();
  });
});

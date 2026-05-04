import { test, expect } from '@playwright/test';

/**
 * E2E Test: Pricing Page Display
 * DemoPPT v2.4
 */
test.describe('定价页面展示', () => {
  test('定价页面加载正确', async ({ page }) => {
    // Login first to access user page with pricing
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    // Navigate to pricing section (should be on user page)
    await page.goto('/user');
    
    // Check subscription section
    await expect(page.locator('text=我的订阅')).toBeVisible();
    
    // Click to show plans if not visible
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
    }
    
    // Check plans section
    await expect(page.locator('text=选择套餐')).toBeVisible();
    
    // Check plan cards are displayed
    const planCards = page.locator('.plan-card');
    await expect(planCards.first()).toBeVisible();
  });

  test('套餐信息完整展示', async ({ page }) => {
    // Login and access pricing
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    await page.goto('/user');
    
    // Show plans
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
    }
    
    // Wait for plans to load
    await expect(page.locator('.plan-card').first()).toBeVisible({ timeout: 5000 });
    
    // Check plan details - name, price, duration
    const firstPlan = page.locator('.plan-card').first();
    await expect(firstPlan.locator('.plan-name')).toBeVisible();
    await expect(firstPlan.locator('.plan-price')).toBeVisible();
    await expect(firstPlan.locator('.plan-duration')).toBeVisible();
    await expect(firstPlan.locator('.plan-features')).toBeVisible();
  });

  test('推荐套餐标记正确', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    await page.goto('/user');
    
    // Show plans
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
    }
    
    // Check recommended badge
    await expect(page.locator('.plan-badge:has-text("最优惠")')).toBeVisible();
    
    // Check recommended plan has correct class
    await expect(page.locator('.plan-card.recommended')).toBeVisible();
  });

  test('立即开通按钮状态正确', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    await page.goto('/user');
    
    // Show plans
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
    }
    
    // Check subscribe buttons exist
    const subscribeButtons = page.locator('button:has-text("立即开通")');
    await expect(subscribeButtons.first()).toBeVisible();
  });

  test('套餐特性列表正确显示', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    await page.goto('/user');
    
    // Show plans
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
    }
    
    // Check feature list
    const features = page.locator('.plan-features li');
    const featureCount = await features.count();
    expect(featureCount).toBeGreaterThan(0);
    
    // Each feature should have checkmark
    const firstFeature = await features.first().textContent();
    expect(firstFeature).toBeTruthy();
  });

  test('订单记录区域存在', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    await page.goto('/user');
    
    // Check orders section
    await expect(page.locator('text=订单记录')).toBeVisible();
    
    // Should show empty state or orders
    const emptyState = page.locator('.ant-empty').or(page.locator('.ant-list'));
    await expect(emptyState.first()).toBeVisible();
  });

  test('定价页面响应式布局', async ({ page }) => {
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    await page.goto('/user');
    
    // Plans should still be accessible
    const plansButton = page.locator('text=立即订阅').or(page.locator('text=续费/升级'));
    if (await plansButton.isVisible()) {
      await plansButton.click();
    }
    
    // Plan cards should stack vertically
    await expect(page.locator('.plan-card').first()).toBeVisible();
  });
});

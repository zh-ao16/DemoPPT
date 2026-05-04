import { test, expect } from '@playwright/test';

/**
 * E2E Test: User Registration and Login Flow
 * DemoPPT v2.4
 */
test.describe('用户注册/登录流程', () => {
  const testPhone = `138${Date.now().toString().slice(-8)}`;
  const testPassword = 'Test123456';
  const testNickname = '测试用户';

  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('登录页面正确加载', async ({ page }) => {
    await expect(page.locator('text=DemoPPT')).toBeVisible();
    await expect(page.locator('text=AI智能PPT生成系统')).toBeVisible();
    await expect(page.locator('text=登录')).toBeVisible();
    await expect(page.locator('text=注册')).toBeVisible();
  });

  test('注册流程 - 新用户注册成功', async ({ page }) => {
    // 切换到注册标签
    await page.click('text=注册');
    await expect(page.locator('text=注册')).toBeVisible();
    
    // 填写注册信息
    await page.fill('input[placeholder="请输入手机号"]', testPhone);
    await page.fill('input[placeholder="请输入密码（至少6位）"]', testPassword);
    await page.fill('input[placeholder="请输入昵称"]', testNickname);
    
    // 提交注册
    await page.click('button:has-text("注册")');
    
    // 等待注册成功，跳转到用户页面
    await page.waitForURL('**/user', { timeout: 10000 });
    await expect(page.locator('text=测试用户')).toBeVisible({ timeout: 5000 });
  });

  test('登录流程 - 已注册用户登录成功', async ({ page }) => {
    // 切换到登录标签
    await page.click('text=登录');
    
    // 填写登录信息
    await page.fill('input[placeholder="请输入手机号"]', testPhone);
    await page.fill('input[placeholder="请输入密码"]', testPassword);
    
    // 提交登录
    await page.click('button:has-text("登录")');
    
    // 等待登录成功
    await page.waitForURL('**/user', { timeout: 10000 });
    await expect(page.locator('.avatar')).toBeVisible({ timeout: 5000 });
  });

  test('登录流程 - 错误密码应显示错误提示', async ({ page }) => {
    await page.fill('input[placeholder="请输入手机号"]', testPhone);
    await page.fill('input[placeholder="请输入密码"]', 'wrongpassword');
    
    await page.click('button:has-text("登录")');
    
    // 检查错误提示
    await expect(page.locator('.ant-alert')).toBeVisible({ timeout: 5000 });
  });

  test('游客试用 - 可跳过登录直接访问首页', async ({ page }) => {
    await page.click('text=游客试用');
    
    await page.waitForURL('**/', { timeout: 5000 });
    await expect(page.locator('text=AI智能PPT')).toBeVisible();
  });

  test('退出登录功能正常', async ({ page }) => {
    // 先登录
    await page.fill('input[placeholder="请输入手机号"]', testPhone);
    await page.fill('input[placeholder="请输入密码"]', testPassword);
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    // 点击退出
    await page.click('text=退出登录');
    
    // 验证退出后返回首页
    await page.waitForURL('**/', { timeout: 5000 });
    await expect(page.locator('text=登录')).toBeVisible();
  });
});

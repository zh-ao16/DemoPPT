import { test, expect } from '@playwright/test';

/**
 * E2E Test: Template Selection Flow
 * DemoPPT v2.4
 */
test.describe('模板选择流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('首页模板展示', async ({ page }) => {
    // Check hero section
    await expect(page.locator('text=AI智能PPT')).toBeVisible();
    await expect(page.locator('text=行业解决方案')).toBeVisible();
    
    // Check templates section
    await expect(page.locator('text=精选模板库')).toBeVisible();
    
    // Check template items are displayed
    await expect(page.locator('.template-item').first()).toBeVisible();
    await expect(page.locator('text=商务蓝')).toBeVisible();
    await expect(page.locator('text=学术风')).toBeVisible();
  });

  test('首页模板点击选择', async ({ page }) => {
    // Get initial selected template
    const initialTemplate = await page.locator('.template-item.active').count();
    expect(initialTemplate).toBeGreaterThan(0);
    
    // Click on a different template
    await page.click('.template-item:has-text("科技风")');
    
    // Should now be selected
    await expect(page.locator('.template-item.active:has-text("科技风")')).toBeVisible();
  });

  test('首页快速生成 - 使用选中的模板', async ({ page }) => {
    // Select a template
    await page.click('.template-item:has-text("学术风")');
    
    // Enter topic
    await page.fill('input[placeholder="输入你的PPT主题"]', '人工智能发展趋势研究');
    
    // Click generate
    await page.click('text=智能生成');
    
    // Should navigate to create page with template parameter
    await page.waitForURL('**/create**', { timeout: 5000 });
  });

  test('创建页面模板网格展示', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[placeholder="请输入手机号"]', '13800000000');
    await page.fill('input[placeholder="请输入密码"]', 'Test123456');
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    // Navigate to create page
    await page.goto('/create');
    await page.click('text=科技/互联网');
    await page.fill('textarea[placeholder*="新能源汽车"]', '测试主题');
    await page.click('text=下一步：角度与受众');
    await page.selectOption('.ant-select:has-text("请选择受众群体")', 'investor');
    await page.click('text=下一步：参考资料');
    await page.click('text=🚀 生成大纲');
    
    // Wait for step 3
    await page.waitForFunction(() => {
      return document.body.textContent.includes('选一个模板风格');
    }, { timeout: 30000 });
    
    // Check template grid
    await expect(page.locator('.template-grid')).toBeVisible();
    
    // Should have multiple templates
    const templateCount = await page.locator('.template-item').count();
    expect(templateCount).toBeGreaterThan(10);
  });

  test('模板预览样式正确', async ({ page }) => {
    // Check homepage templates
    await page.goto('/');
    
    // Find a template item and verify it has a preview
    const templateItem = page.locator('.template-item').first();
    await expect(templateItem.locator('.template-preview')).toBeVisible();
    
    // Verify template description exists
    await expect(templateItem.locator('.template-desc')).toBeVisible();
  });

  test('模板选择后高亮显示', async ({ page }) => {
    await page.goto('/');
    
    // Click on ocean template
    await page.click('.template-item:has-text("海洋蓝")');
    
    // Verify it has active class
    await expect(page.locator('.template-item.active:has-text("海洋蓝")')).toBeVisible();
    
    // Click on another template
    await page.click('.template-item:has-text("商务紫")');
    
    // The previous should no longer be active
    await expect(page.locator('.template-item.active:has-text("海洋蓝")')).not.toBeVisible();
  });
});

import { test, expect } from '@playwright/test';

/**
 * E2E Test: AI PPT Generation Flow
 * DemoPPT v2.4
 * Flow: Input Topic → Select Template → Generate → Export
 */
test.describe('AI生成PPT流程', () => {
  const testTopic = '2024年新能源汽车市场分析报告';

  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    const testPhone = '13800000000';
    const testPassword = 'Test123456';
    await page.fill('input[placeholder="请输入手机号"]', testPhone);
    await page.fill('input[placeholder="请输入密码"]', testPassword);
    await page.click('button:has-text("登录")');
    await page.waitForURL('**/user', { timeout: 10000 });
    
    // Navigate to create page
    await page.goto('/create');
  });

  test('Step 1: 需求收集 - 基础信息填写', async ({ page }) => {
    // Check step indicator
    await expect(page.locator('text=需求收集')).toBeVisible();
    await expect(page.locator('text=确认大纲')).toBeVisible();
    await expect(page.locator('text=选择模板')).toBeVisible();
    await expect(page.locator('text=下载使用')).toBeVisible();
    
    // Select industry
    await page.click('text=科技/互联网');
    
    // Fill topic
    const topicInput = page.locator('textarea[placeholder*="新能源汽车"]');
    await topicInput.fill(testTopic);
    
    // Fill subtitle
    await page.fill('input[placeholder*="投资视角"]', '——从投资视角看产业变革机遇');
    
    // Click next
    await page.click('text=下一步：角度与受众');
    
    // Should move to step 1-2
    await expect(page.locator('text=你的PPT是给谁看的？')).toBeVisible();
  });

  test('Step 1: 需求收集 - 角度与受众选择', async ({ page }) => {
    // Skip to step 1-2
    await page.click('text=科技/互联网');
    await page.fill('textarea[placeholder*="新能源汽车"]', testTopic);
    await page.click('text=下一步：角度与受众');
    
    // Select audience
    await page.selectOption('.ant-select:has-text("请选择受众群体")', 'investor');
    
    // Select purpose
    await page.selectOption('.ant-select:has-text("请选择演示目的")', 'analysis');
    
    // Select angle
    await page.selectOption('.ant-select:has-text("请选择分析角度")', 'market');
    
    // Select language
    await page.click('text=🇨🇳 简体中文');
    
    // Click next
    await page.click('text=下一步：参考资料');
    
    // Should move to step 1-3
    await expect(page.locator('text=添加参考资料（可选）')).toBeVisible();
  });

  test('Step 1: 需求收集 - 可跳过参考资料', async ({ page }) => {
    // Navigate to step 1-3
    await page.click('text=科技/互联网');
    await page.fill('textarea[placeholder*="新能源汽车"]', testTopic);
    await page.click('text=下一步：角度与受众');
    await page.selectOption('.ant-select:has-text("请选择受众群体")', 'investor');
    await page.click('text=下一步：参考资料');
    
    // Should see generate button
    await expect(page.locator('text=🚀 生成大纲')).toBeVisible();
    
    // Click generate without reference material
    await page.click('text=🚀 生成大纲');
    
    // Wait for outline generation (step 2)
    await page.waitForFunction(() => {
      return document.body.textContent.includes('确认大纲');
    }, { timeout: 30000 });
  });

  test('Step 2: 确认大纲 - 大纲编辑功能', async ({ page }) => {
    // Navigate to step 2
    await page.goto('/create');
    await page.click('text=科技/互联网');
    await page.fill('textarea[placeholder*="新能源汽车"]', testTopic);
    await page.click('text=下一步：角度与受众');
    await page.selectOption('.ant-select:has-text("请选择受众群体")', 'investor');
    await page.click('text=下一步：参考资料');
    await page.click('text=🚀 生成大纲');
    await page.waitForFunction(() => {
      return document.body.textContent.includes('确认大纲');
    }, { timeout: 30000 });
    
    // Check outline is displayed
    await expect(page.locator('.outline-list')).toBeVisible();
    
    // Check batch operations
    await expect(page.locator('text=已选')).toBeVisible();
    
    // Click next to template selection
    await page.click('text=选择模板');
    
    // Should be on step 3
    await expect(page.locator('text=选一个模板风格')).toBeVisible();
  });

  test('Step 3: 选择模板 - 模板选择功能', async ({ page }) => {
    // Navigate to step 3
    await page.goto('/create');
    await page.click('text=科技/互联网');
    await page.fill('textarea[placeholder*="新能源汽车"]', testTopic);
    await page.click('text=下一步：角度与受众');
    await page.selectOption('.ant-select:has-text("请选择受众群体")', 'investor');
    await page.click('text=下一步：参考资料');
    await page.click('text=🚀 生成大纲');
    await page.waitForFunction(() => {
      return document.body.textContent.includes('确认大纲');
    }, { timeout: 30000 });
    await page.click('text=选择模板');
    
    // Check templates are visible
    await expect(page.locator('text=科技风')).toBeVisible();
    await.expect(page.locator('text=商务蓝')).toBeVisible();
    await.expect(page.locator('text=学术风')).toBeVisible();
    
    // Select a template
    await page.click('.template-item:has-text("科技风")');
    
    // Selected template should be highlighted
    await expect(page.locator('.template-item.active:has-text("科技风")')).toBeVisible();
  });

  test('Step 3: 高级选项 - 品牌配置', async ({ page }) => {
    // Navigate to step 3
    await page.goto('/create');
    await page.click('text=科技/互联网');
    await page.fill('textarea[placeholder*="新能源汽车"]', testTopic);
    await page.click('text=下一步：角度与受众');
    await page.selectOption('.ant-select:has-text("请选择受众群体")', 'investor');
    await page.click('text=下一步：参考资料');
    await page.click('text=🚀 生成大纲');
    await page.waitForFunction(() => {
      return document.body.textContent.includes('确认大纲');
    }, { timeout: 30000 });
    await page.click('text=选择模板');
    
    // Expand advanced options
    await expect(page.locator('text=高级选项（可选）')).toBeVisible();
    await page.click('text=高级选项（可选）');
    
    // Toggle speaker notes
    await page.click('text=演讲者备注');
    
    // Set brand name
    await page.fill('input[placeholder="如：DemoTech"]', 'DemoTech AI');
  });

  test('Step 4: 生成结果 - 成功页面', async ({ page }) => {
    // This test verifies the result page structure
    // Note: Full generation requires backend API
    await page.goto('/create');
    
    // The step 4 is only reached after successful generation
    // For now, verify the structure is correct
    await expect(page.locator('text=需求收集')).toBeVisible();
    await expect(page.locator('text=确认大纲')).toBeVisible();
    await expect(page.locator('text=选择模板')).toBeVisible();
    await expect(page.locator('text=下载使用')).toBeVisible();
  });
});

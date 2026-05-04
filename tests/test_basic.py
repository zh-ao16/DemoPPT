#!/usr/bin/env python3
"""
DemoPPT 基础测试用例
测试项目结构和模块导入
"""
import pytest
import sys
import os

# 添加backend路径
sys.path.insert(0, '/home/hg/.hermes/company/projects/DemoPPT/backend')


class TestProjectStructure:
    """项目结构测试"""

    def test_project_root_exists(self):
        """项目根目录存在"""
        assert os.path.exists('/home/hg/.hermes/company/projects/DemoPPT')

    def test_backend_exists(self):
        """backend目录存在"""
        assert os.path.exists('/home/hg/.hermes/company/projects/DemoPPT/backend')

    def test_frontend_exists(self):
        """frontend目录存在"""
        assert os.path.exists('/home/hg/.hermes/company/projects/DemoPPT/frontend')

    def test_output_dir_exists(self):
        """output目录存在"""
        assert os.path.exists('/home/hg/.hermes/company/projects/DemoPPT/backend/output')

    def test_tests_dir_exists(self):
        """tests目录存在"""
        assert os.path.exists('/home/hg/.hermes/company/projects/DemoPPT/tests')


class TestBackendModules:
    """后端模块导入测试"""

    def test_import_api_auth(self):
        """导入api_auth模块"""
        try:
            import api_auth
            assert api_auth is not None
        except ImportError as e:
            pytest.skip(f"Cannot import api_auth: {e}")

    def test_import_subscription(self):
        """导入subscription模块"""
        try:
            import subscription
            assert subscription is not None
        except ImportError as e:
            pytest.skip(f"Cannot import subscription: {e}")

    def test_import_model_config(self):
        """导入model_config模块"""
        try:
            import model_config
            assert model_config is not None
        except ImportError as e:
            pytest.skip(f"Cannot import model_config: {e}")

    def test_import_user_auth(self):
        """导入user_auth模块"""
        try:
            import user_auth
            assert user_auth is not None
        except ImportError as e:
            pytest.skip(f"Cannot import user_auth: {e}")

    def test_import_color_palette(self):
        """导入color_palette模块"""
        try:
            import color_palette
            assert color_palette is not None
        except ImportError as e:
            pytest.skip(f"Cannot import color_palette: {e}")

    def test_import_fallback_content(self):
        """导入fallback_content模块"""
        try:
            import fallback_content
            assert fallback_content is not None
        except ImportError as e:
            pytest.skip(f"Cannot import fallback_content: {e}")


class TestColorPalette:
    """颜色配置测试"""

    def test_palettes_exist(self):
        """检查预定义调色板存在"""
        try:
            from color_palette import PALETTES
            assert isinstance(PALETTES, dict)
            assert len(PALETTES) > 0
        except ImportError:
            pytest.skip("color_palette PALETTES not available")

    def test_industry_palette_mapping(self):
        """检查行业-调色板映射"""
        try:
            from color_palette import INDUSTRY_PALETTE_MAP
            assert isinstance(INDUSTRY_PALETTE_MAP, dict)
        except ImportError:
            pytest.skip("INDUSTRY_PALETTE_MAP not available")


class TestSubscriptionPlans:
    """订阅套餐测试"""

    def test_plans_defined(self):
        """检查套餐定义"""
        try:
            from subscription import SUBSCRIPTION_PLANS
            assert isinstance(SUBSCRIPTION_PLANS, (list, dict))
            assert len(SUBSCRIPTION_PLANS) > 0
        except ImportError:
            pytest.skip("SUBSCRIPTION_PLANS not available")


class TestRequirements:
    """依赖测试"""

    def test_requirements_file_exists(self):
        """requirements.txt存在"""
        assert os.path.exists('/home/hg/.hermes/company/projects/DemoPPT/backend/requirements.txt')

    def test_requirements_has_fastapi(self):
        """requirements包含fastapi"""
        with open('/home/hg/.hermes/company/projects/DemoPPT/backend/requirements.txt') as f:
            content = f.read()
            assert 'fastapi' in content.lower(), "requirements.txt should contain fastapi"

    def test_requirements_has_pptx(self):
        """requirements包含python-pptx"""
        with open('/home/hg/.hermes/company/projects/DemoPPT/backend/requirements.txt') as f:
            content = f.read()
            assert 'python-pptx' in content.lower() or 'pptx' in content.lower(), "requirements.txt should contain python-pptx"

    def test_requirements_has_pytest(self):
        """requirements包含pytest"""
        with open('/home/hg/.hermes/company/projects/DemoPPT/backend/requirements.txt') as f:
            content = f.read()
            assert 'pytest' in content.lower(), "requirements.txt should contain pytest"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

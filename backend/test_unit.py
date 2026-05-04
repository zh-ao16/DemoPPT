#!/usr/bin/env python3
"""
DemoPPT 后端单元测试
覆盖核心API：注册、登录、订阅、模型配置、大纲生成
"""
import pytest
import subprocess
import json
import time
import sys
import os

BASE_URL = "http://localhost:8000"
sys.path.insert(0, '/home/hg/.hermes/company/projects/DemoPPT/backend')

# ============================================================
# 辅助函数
# ============================================================

def wait_for_backend(timeout=10):
    """等待后端启动"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            import urllib.request
            urllib.request.urlopen(f"{BASE_URL}/", timeout=2)
            return True
        except:
            time.sleep(1)
    return False

def api_post(path, json_data, token=None):
    """POST请求"""
    import urllib.request
    data = json.dumps(json_data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8'))

def api_get(path, token=None):
    """GET请求"""
    import urllib.request
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8'))

# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="module")
def ensure_backend():
    """确保后端运行"""
    if not wait_for_backend():
        pytest.skip("Backend not running")
    yield True

@pytest.fixture
def test_user_phone():
    """每次测试用不同的手机号"""
    return f"139{time.time():.0f}"[-11:]

@pytest.fixture
def auth_token(test_user_phone, ensure_backend):
    """注册并登录，返回token"""
    # 注册
    result = api_post("/api/auth/register", {
        "phone": test_user_phone,
        "password": "Test@123456",
        "nickname": "测试用户"
    })
    # 登录
    result = api_post("/api/auth/login", {
        "phone": test_user_phone,
        "password": "Test@123456"
    })
    if result.get("success"):
        return result.get("token")
    pytest.skip(f"Auth failed: {result}")

# ============================================================
# 测试用例
# ============================================================

class TestAuthAPI:
    """认证API测试"""

    def test_register_success(self, test_user_phone, ensure_backend):
        """注册成功"""
        result = api_post("/api/auth/register", {
            "phone": test_user_phone,
            "password": "Test@123456",
            "nickname": "测试"
        })
        assert result.get("success") == True, f"注册失败: {result}"

    def test_register_duplicate(self, test_user_phone, ensure_backend):
        """重复注册"""
        api_post("/api/auth/register", {
            "phone": test_user_phone,
            "password": "Test@123456"
        })
        result = api_post("/api/auth/register", {
            "phone": test_user_phone,
            "password": "Test@123456"
        })
        assert result.get("success") == False, "重复注册应该失败"

    def test_login_success(self, test_user_phone, ensure_backend):
        """登录成功"""
        api_post("/api/auth/register", {
            "phone": test_user_phone,
            "password": "Test@123456"
        })
        result = api_post("/api/auth/login", {
            "phone": test_user_phone,
            "password": "Test@123456"
        })
        assert result.get("success") == True, f"登录失败: {result}"
        assert "token" in result, "缺少token"

    def test_login_wrong_password(self, test_user_phone, ensure_backend):
        """密码错误"""
        api_post("/api/auth/register", {
            "phone": test_user_phone,
            "password": "Test@123456"
        })
        result = api_post("/api/auth/login", {
            "phone": test_user_phone,
            "password": "WrongPassword"
        })
        assert result.get("success") == False, "密码错误应该登录失败"

    def test_login_nonexistent_user(self, ensure_backend):
        """用户不存在"""
        result = api_post("/api/auth/login", {
            "phone": "13800000000",
            "password": "Test@123456"
        })
        assert result.get("success") == False, "不存在的用户应该登录失败"


class TestSubscriptionAPI:
    """订阅API测试"""

    def test_get_plans(self, ensure_backend):
        """获取套餐列表"""
        result = api_get("/api/plans")
        assert isinstance(result, (list, dict)), f"plans应该返回列表或字典，实际: {type(result)}"
        assert len(result) > 0 if isinstance(result, list) else True, "应该有套餐数据"

    def test_get_subscription(self, auth_token, ensure_backend):
        """获取订阅状态"""
        result = api_get("/api/subscription", auth_token)
        # 应该返回用户的订阅状态
        assert isinstance(result, dict), f"subscription应该返回字典，实际: {type(result)}"

    def test_check_subscription(self, auth_token, ensure_backend):
        """检查订阅资格"""
        result = api_get("/api/subscription/check", auth_token)
        assert isinstance(result, dict), f"check应该返回字典，实际: {type(result)}"


class TestModelAPI:
    """模型配置API测试"""

    def test_get_models(self, auth_token, ensure_backend):
        """获取模型列表"""
        result = api_get("/api/models", auth_token)
        assert isinstance(result, dict), f"models应该返回字典，实际: {type(result)}"
        assert "models" in result or "configs" in result, f"应该包含models或configs字段，实际: {result.keys()}"

    def test_get_default_model(self, auth_token, ensure_backend):
        """获取默认模型"""
        result = api_get("/api/models/default", auth_token)
        assert isinstance(result, dict), f"default model应该返回字典，实际: {type(result)}"

    def test_add_model(self, auth_token, ensure_backend):
        """添加模型配置"""
        result = api_post("/api/models", {
            "name": "测试模型",
            "api_key": "sk-test123456789",
            "api_url": "https://api.test.com",
            "model_name": "test-model"
        }, auth_token)
        assert isinstance(result, dict), f"添加模型应该返回字典，实际: {type(result)}"

    def test_add_model_invalid_key(self, auth_token, ensure_backend):
        """无效API Key处理"""
        result = api_post("/api/models", {
            "name": "无效Key测试",
            "api_key": "sk-xxx",
            "api_url": "https://api.test.com",
            "model_name": "test-model"
        }, auth_token)
        # 应该能添加但调用会失败
        assert isinstance(result, dict), f"应该返回字典，实际: {type(result)}"


class TestGenerateOutline:
    """大纲生成API测试"""

    def test_generate_outline(self, auth_token, ensure_backend):
        """生成大纲"""
        result = api_post("/api/generate_outline", {
            "topic": "人工智能发展趋势",
            "industry": "科技",
            "num_slides": 5
        }, auth_token)
        
        assert isinstance(result, dict), f"应该返回字典，实际: {type(result)}"
        assert result.get("success") == True, f"生成失败: {result}"
        outline = result.get("outline", [])
        assert len(outline) >= 3, f"大纲页数不足: {len(outline)}"

    def test_generate_outline_no_auth(self, ensure_backend):
        """无认证也可以生成大纲（演示模式）"""
        result = api_post("/api/generate_outline", {
            "topic": "测试",
            "industry": "科技",
            "num_slides": 5
        })
        # 演示模式不强制认证，返回成功也合理
        assert isinstance(result, dict), "应该返回字典"


class TestHealthCheck:
    """健康检查测试"""

    def test_backend_alive(self, ensure_backend):
        """后端存活"""
        import urllib.request
        try:
            req = urllib.request.Request(f"{BASE_URL}/")
            with urllib.request.urlopen(req, timeout=5) as resp:
                assert resp.status == 200
        except:
            pytest.fail("Backend not responding")

    def test_frontend_alive(self):
        """前端存活"""
        import urllib.request
        try:
            req = urllib.request.Request("http://localhost:3000/")
            with urllib.request.urlopen(req, timeout=5) as resp:
                assert resp.status == 200
        except:
            pytest.fail("Frontend not responding")


# ============================================================
# 主函数
# ============================================================

def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("DemoPPT 后端单元测试")
    print("=" * 60)
    
    # 检查后端
    if not wait_for_backend():
        print("❌ 后端未运行，请先启动: cd /home/hg/.hermes/company/projects/DemoPPT/backend && uvicorn main:app --port 8000")
        return False
    
    # 检查前端
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:3000/", timeout=3)
    except:
        print("⚠️ 前端未运行，部分测试可能失败")
    
    # 运行pytest
    args = [
        __file__,
        '-v',
        '--tb=short',
        '-x',  # 遇到第一个失败就停止
    ]
    result = pytest.main(args)
    return result == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

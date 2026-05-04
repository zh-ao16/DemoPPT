<template>
  <div class="page-container">
    <!-- Steps Progress -->
    <a-card :bordered="false" class="steps-card">
      <a-steps :current="step - 1" size="small">
        <a-step title="需求收集" />
        <a-step title="确认大纲" />
        <a-step title="选择模板" />
        <a-step title="下载使用" />
      </a-steps>
    </a-card>

    <!-- ========== Step 1: 需求收集 ========== -->
    <a-card v-if="step === 1" :bordered="false" class="step-content-card">
      <!-- Sub Steps -->
      <a-steps :current="subStep - 1" size="small" class="sub-steps">
        <a-step title="基础信息" />
        <a-step title="角度与受众" />
        <a-step title="参考资料" />
      </a-steps>

      <!-- Step 1-1: 基础信息 -->
      <div v-if="subStep === 1" class="sub-content">
        <h2 class="step-title">告诉AI你要做什么PPT 🎯</h2>

        <a-form layout="vertical" class="step-form">
          <a-form-item label="所属行业">
            <a-radio-group 
              v-model:value="formData.industry" 
              class="industry-radio-group">
              <a-row :gutter="[12, 12]">
                <a-col :xs="12" :sm="8" :md="6" v-for="ind in industries" :key="ind.id">
                  <a-radio-button :value="ind.id" class="industry-btn">
                    <span class="ind-icon">{{ ind.icon }}</span>
                    <span>{{ ind.name }}</span>
                  </a-radio-button>
                </a-col>
              </a-row>
            </a-radio-group>
          </a-form-item>

          <a-form-item label="PPT主题" required>
            <a-input-group compact style="display: flex">
              <a-textarea
                v-model:value="formData.topic"
                placeholder="例如：2024年新能源汽车市场投资分析报告"
                :rows="4"
                showCount
                :maxlength="500"
                style="flex: 1"
              />
              <a-button @click="openTranslator(formData.topic, 'topic')" style="height: auto; margin-left: 8px">
                🌐 翻译
              </a-button>
            </a-input-group>
          </a-form-item>

          <a-form-item label="PPT副标题（可选）">
            <a-input
              v-model:value="formData.subtitle"
              placeholder="例如：——从投资视角看产业变革机遇"
            />
          </a-form-item>
        </a-form>

        <div class="form-actions">
          <a-button 
            type="primary" 
            size="large"
            :disabled="!formData.topic.trim()"
            @click="subStep = 2">
            下一步：角度与受众 →
          </a-button>
        </div>
      </div>

      <!-- Step 1-2: 角度与受众 -->
      <div v-if="subStep === 2" class="sub-content">
        <h2 class="step-title">你的PPT是给谁看的？📊</h2>

        <a-form layout="vertical" class="step-form">
          <a-form-item label="受众群体">
            <a-select v-model:value="formData.audience" placeholder="请选择受众群体">
              <a-select-option v-for="aud in audiences" :key="aud.id" :value="aud.id">
                {{ aud.icon }} {{ aud.name }}
              </a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="演示目的">
            <a-select v-model:value="formData.purpose" placeholder="请选择演示目的">
              <a-select-option v-for="pur in purposes" :key="pur.id" :value="pur.id">
                {{ pur.icon }} {{ pur.name }}
              </a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="分析角度">
            <a-select v-model:value="formData.angle" placeholder="请选择分析角度">
              <a-select-option v-for="ang in angles" :key="ang.id" :value="ang.id">
                {{ ang.icon }} {{ ang.name }}
              </a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="语言">
            <a-radio-group v-model:value="formData.language">
              <a-radio-button value="zh">🇨🇳 简体中文</a-radio-button>
              <a-radio-button value="en">🇺🇸 English</a-radio-button>
              <a-radio-button value="zh-TW">🇹🇼 繁體中文</a-radio-button>
            </a-radio-group>
          </a-form-item>
        </a-form>

        <div class="form-actions">
          <a-button @click="subStep = 1">← 上一步</a-button>
          <a-button type="primary" @click="subStep = 3">下一步：参考资料 →</a-button>
        </div>
      </div>

      <!-- Step 1-3: 参考资料 -->
      <div v-if="subStep === 3" class="sub-content">
        <h2 class="step-title">添加参考资料（可选）📚</h2>
        <p class="step-hint">上传文档或选择知识库内容，AI会自动融入PPT</p>

        <a-form layout="vertical" class="step-form">
          <!-- 知识库已有文档 -->
          <a-form-item v-if="kbDocs.length > 0" label="📂 知识库内容（自动融入PPT）">
            <a-list size="small" :data-source="kbDocs" class="kb-doc-list">
              <template #renderItem="{ item }">
                <a-list-item>
                  <template #actions>
                    <a-popconfirm
                      title="确定删除该文档？"
                      @confirm="deleteKbDoc(item.id)"
                    >
                      <a-button type="link" danger size="small">删除</a-button>
                    </a-popconfirm>
                  </template>
                  <a-list-item-meta>
                    <template #title>
                      <a-space>
                        <span>📄</span>
                        <span>{{ item.title || item.filename }}</span>
                      </a-space>
                    </template>
                    <template #description>
                      {{ formatSize(item.size) }} · {{ item.uploaded_at }}
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-form-item>

          <!-- 上传新文档 -->
          <a-form-item label="📤 上传文档到知识库">
            <a-upload
              drag
              :before-upload="handleFileUpload"
              :show-upload-list="false"
              accept=".txt,.md,.pdf,.docx"
            >
              <div class="upload-area">
                <p class="upload-icon">📎</p>
                <p class="upload-text">拖拽文件或点击上传</p>
                <p class="upload-formats">支持 TXT / MD / PDF / DOCX</p>
              </div>
            </a-upload>
          </a-form-item>

          <!-- 粘贴文本 -->
          <a-form-item label="📝 或粘贴文档内容">
            <a-textarea
              v-model:value="formData.refContent"
              placeholder="粘贴你要融入PPT的参考资料内容..."
              :rows="4"
            />
            <a-button 
              v-if="formData.refContent.trim()" 
              @click="addRefToKB" 
              :loading="refLoading"
              class="btn-add-ref">
              + 添加到知识库
            </a-button>
          </a-form-item>
        </a-form>

        <div class="form-actions">
          <a-button @click="subStep = 2">← 上一步</a-button>
          <a-button 
            type="primary" 
            size="large"
            :loading="loading"
            :disabled="!formData.topic.trim()"
            @click="generateOutlineWithContext">
            {{ loading ? '🤖 AI生成大纲中...' : '🚀 生成大纲' }}
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- ========== Step 2: 确认大纲 ========== -->
    <a-card v-if="step === 2" :bordered="false" class="step-content-card">
      <template #title>
        <a-space>
          <span>确认大纲</span>
          <a-tag v-if="hasKbContext" color="green">📚 知识库已融入</a-tag>
        </a-space>
      </template>

      <p class="step-hint">可以拖拽调整顺序，或直接修改标题</p>

      <!-- Batch Operations -->
      <div v-if="outline.length > 0" class="batch-bar">
        <a-checkbox v-model:checked="allSelected" @change="toggleSelectAll">全选</a-checkbox>
        <a-badge :count="selectedPages.length" :number-style="{ backgroundColor: '#1890ff' }" />
        <span class="selected-text">已选</span>
        <a-popconfirm
          v-if="selectedPages.length > 0"
          title="确定删除选中的页面？"
          @confirm="batchDelete"
        >
          <a-button size="small" danger>🗑️ 批量删除</a-button>
        </a-popconfirm>
      </div>

      <!-- Outline List -->
      <div class="outline-list">
        <div v-for="(page, index) in outline" :key="index" class="outline-item">
          <a-checkbox v-model:checked="page._selected" @change="updateSelected" />
          <a-badge :count="index + 1" :number-style="{ backgroundColor: '#1890ff' }" />
          <a-input 
            v-model:value="page.title" 
            class="page-title-input"
            :disabled="page.type === 'cover'" />
          <a-select v-model:value="page.type" class="page-type-select">
            <a-select-option value="cover">封面</a-select-option>
            <a-select-option value="toc">目录</a-select-option>
            <a-select-option value="content">内容页</a-select-option>
            <a-select-option value="summary">总结</a-select-option>
          </a-select>
          <a-button 
            v-if="page.type === 'content'" 
            type="link" 
            size="small"
            @click="toggleChart(page)">
            📊
          </a-button>
          <a-button 
            type="link" 
            danger 
            size="small"
            @click="removePage(index)">
            🗑️
          </a-button>
        </div>
        
        <a-button block @click="addPage" class="btn-add-page">+ 添加页面</a-button>
      </div>

      <div class="form-actions">
        <a-button @click="step = 1">← 修改需求</a-button>
        <a-button type="primary" @click="step = 3">选择模板 →</a-button>
      </div>
    </a-card>

    <!-- ========== Step 3: 选择模板 ========== -->
    <a-card v-if="step === 3" :bordered="false" class="step-content-card">
      <h2 class="step-title">选一个模板风格</h2>

      <a-row :gutter="[16, 16]" class="template-grid">
        <a-col :xs="12" :sm="8" :md="6" :lg="4" v-for="t in templates" :key="t.id">
          <div 
            class="template-item" 
            :class="{ active: selectedTemplate === t.id }"
            @click="selectedTemplate = t.id">
            <div class="template-preview" :style="getPreviewStyle(t)">
              <span>{{ t.name }}</span>
            </div>
            <p class="template-desc">{{ t.desc }}</p>
          </div>
        </a-col>
      </a-row>

      <!-- AI模型选择 -->
      <a-divider>选择AI模型</a-divider>
      <div class="model-selector">
        <a-empty v-if="modelConfigs.length === 0" description="暂无模型配置">
          <router-link to="/settings">
            <a-button type="primary">去添加 →</a-button>
          </router-link>
        </a-empty>
        <a-select
          v-else
          v-model:value="selectedModelId"
          placeholder="请选择AI模型"
          style="width: 300px"
        >
          <a-select-option v-for="m in modelConfigs" :key="m.id" :value="m.id">
            <a-space>
              <span>{{ m.name }}</span>
              <a-tag size="small">{{ m.provider }}</a-tag>
              <a-tag v-if="m.is_default" size="small" color="blue">默认</a-tag>
            </a-space>
          </a-select-option>
        </a-select>
      </div>

      <!-- 高级选项 -->
      <a-divider>高级选项（可选）</a-divider>
      <a-form layout="vertical" class="advanced-form">
      <a-form-item>
        <a-checkbox v-model:checked="speakerNotes">演讲者备注</a-checkbox>
        <span class="option-tip">自动生成每页演讲提示</span>
      </a-form-item>

      <a-form-item>
        <a-checkbox v-model:checked="faithfulMode">内容保真模式</a-checkbox>
        <span class="option-tip">保留原文格式，AI仅排版不扩写</span>
      </a-form-item>

      <a-form-item label="中文排版">
        <a-space direction="vertical" style="width: 100%">
          <a-space>
            <span style="width: 80px">字体：</span>
            <a-select v-model:value="chineseTypography.font_family" style="width: 160px">
              <a-select-option value="Microsoft YaHei">微软雅黑</a-select-option>
              <a-select-option value="PingFang SC">苹方</a-select-option>
              <a-select-option value="SimHei">黑体</a-select-option>
              <a-select-option value="SimSun">宋体</a-select-option>
            </a-select>
          </a-space>
          <a-space>
            <a-checkbox v-model:checked="chineseTypography.punctuation_compress">标点压缩</a-checkbox>
            <a-checkbox v-model:checked="chineseTypography.code_block_isolated">代码块隔离</a-checkbox>
          </a-space>
        </a-space>
      </a-form-item>
        
        <a-form-item label="语言">
          <a-select v-model:value="language" style="width: 200px">
            <a-select-option value="zh">简体中文</a-select-option>
            <a-select-option value="en">English</a-select-option>
            <a-select-option value="zh-TW">繁體中文</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="主题色">
          <a-space>
            <a-input type="color" v-model:value="brandColor" style="width: 60px" />
            <a-input v-model:value="brandColor" placeholder="#6366f1" style="width: 120px" />
            <span class="option-tip">选颜色自动生成全套配色</span>
          </a-space>
        </a-form-item>
        
        <a-form-item label="品牌名称">
          <a-input v-model:value="brandName" placeholder="如：DemoTech" style="width: 300px" />
        </a-form-item>
        
        <a-form-item label="品牌Logo">
          <a-input v-model:value="brandLogo" placeholder="Logo图片URL（可选）" style="width: 300px" />
        </a-form-item>
      </a-form>

      <!-- 生成进度 -->
      <a-modal
        v-model:open="showConfirm"
        title="📋 生成确认"
        @ok="doGenerate"
        ok-text="确认生成"
        cancel-text="返回修改"
        :confirmLoading="generating"
      >
        <a-descriptions bordered :column="1" size="small">
          <a-descriptions-item label="主题">{{ formData.topic }}</a-descriptions-item>
          <a-descriptions-item label="副标题">{{ formData.subtitle || '无' }}</a-descriptions-item>
          <a-descriptions-item label="行业">{{ formData.industry || '通用' }}</a-descriptions-item>
          <a-descriptions-item label="页数">{{ outline.length }} 页</a-descriptions-item>
          <a-descriptions-item label="模板">{{ getTemplateName(selectedTemplate) }}</a-descriptions-item>
          <a-descriptions-item label="演讲备注">{{ speakerNotes ? '✅ 开启' : '❌ 关闭' }}</a-descriptions-item>
          <a-descriptions-item label="内容保真">{{ faithfulMode ? '✅ 开启' : '❌ 关闭' }}</a-descriptions-item>
          <a-descriptions-item label="语言">{{ language === 'zh' ? '简体中文' : language === 'en' ? 'English' : '繁體中文' }}</a-descriptions-item>
          <a-descriptions-item v-if="brandName" label="品牌名称">{{ brandName }}</a-descriptions-item>
          <a-descriptions-item v-if="brandColor" label="主题色">{{ brandColor }}</a-descriptions-item>
        </a-descriptions>
      </a-modal>

      <!-- Error Message -->
      <a-alert
        v-if="errorMessage"
        type="error"
        :message="errorMessage"
        show-icon
        class="error-alert"
      >
        <template #action>
          <a-button size="small" @click="generatePPT">重试</a-button>
        </template>
      </a-alert>

      <div class="form-actions">
        <a-button @click="step = 2">← 上一步</a-button>
        <a-button 
          v-if="!generating" 
          type="primary" 
          size="large"
          @click="showConfirm = true">
          开始生成PPT →
        </a-button>
        <a-button v-else type="primary" size="large" loading>
          生成中...
        </a-button>
      </div>
    </a-card>

    <!-- ========== Step 4: 下载 ========== -->
    <a-card v-if="step === 4" :bordered="false" class="step-content-card result-card">
      <a-result
        status="success"
        title="PPT生成成功！"
        sub-title="下载文件开始使用"
      >
        <template #extra>
          <a-space size="large">
            <a :href="downloadUrl" download target="_blank">
              <a-button type="primary" size="large">下载PPTX</a-button>
            </a>
            <a-button size="large" @click="reset">再做一个</a-button>
          </a-space>
        </template>
      </a-result>
    </a-card>

    <!-- Translator Modal -->
    <Translator ref="translatorRef" :showInsertBtn="true" @insert="handleTranslateInsert" />
  </div>
</template>

<script>
import Translator from '../components/Translator.vue'
const API = 'http://localhost:8000/api'
export default {
  name: 'Create',
  components: { Translator },
  data() {
    return {
      step: 1,
      subStep: 1,
      showConfirm: false,
      loading: false,
      generating: false,
      refLoading: false,
      hasKbContext: false,
      outline: [],
      selectedTemplate: 'tech',
      modelConfigs: [],
      selectedModelId: null,
      speakerNotes: false,
      language: 'zh',
      brandColor: '',
      brandName: '',
      brandLogo: '',
      // 内容保真模式
      faithfulMode: true,
      // 中文排版选项
      chineseTypography: {
        font_family: 'Microsoft YaHei',
        punctuation_compress: true,
        paragraph_indent: 2,
        code_block_isolated: true
      },
      downloadUrl: '',
      allSelected: false,
      selectedPages: [],
      batchType: '',
      progressMessage: '准备开始...',
      progressPercent: 0,
      progressCurrent: 0,
      progressTotal: 0,
      errorMessage: '',
      progressEventSource: null,
      formData: {
        topic: '',
        subtitle: '',
        industry: 'technology',
        audience: 'investor',
        purpose: 'analysis',
        angle: 'market',
        language: 'zh',
        refContent: ''
      },
      kbDocs: [],
      industries: [
        { id: 'technology', icon: '💻', name: '科技/互联网' },
        { id: 'finance', icon: '💰', name: '金融/投资' },
        { id: 'education', icon: '🎓', name: '教育培训' },
        { id: 'healthcare', icon: '🏥', name: '医疗健康' },
        { id: 'retail', icon: '🛒', name: '零售/电商' },
        { id: 'manufacture', icon: '🏭', name: '制造业' },
        { id: 'energy', icon: '⚡', name: '新能源/双碳' },
        { id: 'media', icon: '📺', name: '传媒/娱乐' },
        { id: 'realestate', icon: '🏠', name: '房地产' },
        { id: 'general', icon: '📋', name: '通用/综合' },
      ],
      audiences: [
        { id: 'investor', icon: '👔', name: '投资人' },
        { id: 'executive', icon: '📊', name: '高管层' },
        { id: 'client', icon: '🤝', name: '客户' },
        { id: 'team', icon: '👥', name: '团队内部' },
        { id: 'public', icon: '🌐', name: '公开发布' },
        { id: 'academic', icon: '🔬', name: '学术研究' },
      ],
      purposes: [
        { id: 'analysis', icon: '🔍', name: '投资分析' },
        { id: 'report', icon: '📄', name: '汇报总结' },
        { id: 'proposal', icon: '💡', name: '商业提案' },
        { id: 'training', icon: '📚', name: '培训演示' },
        { id: 'marketing', icon: '📢', name: '市场推广' },
        { id: 'plan', icon: '🗺️', name: '规划方案' },
      ],
      angles: [
        { id: 'market', icon: '📈', name: '市场分析' },
        { id: 'competitor', icon: '⚔️', name: '竞争格局' },
        { id: 'technology', icon: '🔧', name: '技术路线' },
        { id: 'operation', icon: '⚙️', name: '运营管理' },
        { id: 'risk', icon: '⚠️', name: '风险评估' },
        { id: 'strategy', icon: '🎯', name: '战略规划' },
      ],
      templates: [
        { id: 'tech', name: '科技风', desc: '蓝紫渐变', color: 'linear-gradient(135deg, #1a1a4e, #00d4ff)' },
        { id: 'business', name: '商务蓝', desc: '藏蓝金色', color: 'linear-gradient(135deg, #2c5282, #ed8936)' },
        { id: 'enterprise', name: '企业蓝', desc: '稳重企业', color: 'linear-gradient(135deg, #1e3a5f, #3182ce)' },
        { id: 'navy_gold', name: '藏金商务', desc: '藏蓝金色', color: 'linear-gradient(135deg, #1a365d, #d69e2e)' },
        { id: 'simple', name: '简约风', desc: '纯白浅灰', color: 'linear-gradient(135deg, #f7fafc, #e2e8f0)' },
        { id: 'minimal', name: '极简白', desc: '纯白极简', color: 'linear-gradient(135deg, #ffffff, #edf2f7)' },
        { id: 'gray_elegant', name: '灰雅风', desc: '高级灰', color: 'linear-gradient(135deg, #2d3748, #718096)' },
        { id: 'academic', name: '学术风', desc: '深蓝白色', color: 'linear-gradient(135deg, #1a365d, #2c5282)' },
        { id: 'cyber', name: '赛博朋克', desc: '霓虹科技', color: 'linear-gradient(135deg, #0f0f23, #ff00ff)' },
        { id: 'future', name: '未来科技', desc: '深空蓝紫', color: 'linear-gradient(135deg, #1a0533, #7c3aed)' },
        { id: 'gradient', name: '渐变风', desc: '彩色活力', color: 'linear-gradient(135deg, #ff6b6b, #4ecdc4)' },
        { id: 'nature', name: '商务绿', desc: '绿色清新', color: 'linear-gradient(135deg, #276749, #68d391)' },
        { id: 'ocean', name: '海洋蓝', desc: '清爽海风', color: 'linear-gradient(135deg, #0077b6, #00b4d8)' },
        { id: 'elegant', name: '商务紫', desc: '紫色高贵', color: 'linear-gradient(135deg, #553c9a, #9f7aea)' },
        { id: 'royal', name: '皇家紫', desc: '皇室贵族', color: 'linear-gradient(135deg, #4c1d95, #8b5cf6)' },
        { id: 'festive', name: '商务红', desc: '红色喜庆', color: 'linear-gradient(135deg, #c53030, #fc8181)' },
        { id: 'classic_blue', name: '经典蓝', desc: '经典蓝色', color: 'linear-gradient(135deg, #2b6cb0, #63b3ed)' },
        { id: 'chinese', name: '中国风', desc: '水墨文化', color: 'linear-gradient(135deg, #1a202c, #718096)' },
        { id: 'ink_wash', name: '水墨风', desc: '山水意境', color: 'linear-gradient(135deg, #2d3748, #a0aec0)' },
        { id: 'red_gold', name: '中国红金', desc: '红金传统', color: 'linear-gradient(135deg, #742a2a, #d69e2e)' },
      ],
    }
  },
  mounted() {
    this.loadKBDocs()
    this.loadModelConfigs()
    const t = this.$route.query.topic
    if (t) {
      this.formData.topic = t
    }
  },
  methods: {
    getPreviewStyle(t) {
      if (t.previewImg) {
        return { backgroundImage: `url(${t.previewImg})`, backgroundSize: 'cover', backgroundPosition: 'center' }
      }
      return { background: t.color }
    },
    getTemplateName(tid) {
      const t = this.templates.find(x => x.id === tid)
      return t ? t.name : tid
    },
    doGenerate() {
      this.showConfirm = false
      this.generatePPT()
    },
    async loadKBDocs() {
      try {
        const resp = await fetch(`${API}/kb/documents`)
        const data = await resp.json()
        if (data.success) this.kbDocs = data.documents || []
      } catch (e) {}
    },
    async loadModelConfigs() {
      const token = localStorage.getItem('demoppt_token')
      if (!token) return
      try {
        const resp = await fetch(`${API}/models`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await resp.json()
        if (data.success) {
          this.modelConfigs = data.configs || []
          const defaultModel = this.modelConfigs.find(m => m.is_default)
          if (defaultModel) this.selectedModelId = defaultModel.id
          else if (this.modelConfigs.length === 1) this.selectedModelId = this.modelConfigs[0].id
        }
      } catch (e) {}
    },
    async deleteKbDoc(id) {
      await fetch(`${API}/kb/documents/${id}`, { method: 'DELETE' })
      this.loadKBDocs()
    },
    handleFileUpload(file) {
      this.uploadFile(file)
      return false
    },
    async uploadFile(file) {
      this.refLoading = true
      const form = new FormData()
      form.append('file', file)
      try {
        const resp = await fetch(`${API}/kb/upload`, { method: 'POST', body: form })
        const data = await resp.json()
        if (data.success) {
          this.loadKBDocs()
          this.$message.success('上传成功！已添加到知识库')
        } else {
          this.$message.error(data.message || '上传失败')
        }
      } catch (e) {
        this.$message.error('上传失败')
      }
      this.refLoading = false
    },
    async addRefToKB() {
      if (!this.formData.refContent.trim()) return
      this.refLoading = true
      try {
        const resp = await fetch(`${API}/kb/documents`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: this.formData.refContent,
            filename: '粘贴内容_' + Date.now() + '.txt',
            file_type: 'txt',
            title: this.formData.topic.slice(0, 30)
          })
        })
        const data = await resp.json()
        if (data.success) {
          this.formData.refContent = ''
          this.loadKBDocs()
          this.$message.success('已添加到知识库 ✅')
        }
      } catch (e) {
        this.$message.error('添加失败')
      }
      this.refLoading = false
    },
    async generateOutlineWithContext() {
      if (!this.formData.topic.trim()) {
        this.$message.warning('请输入主题')
        return
      }
      this.loading = true
      try {
        const audienceMap = { investor: '给投资人', executive: '给高管', client: '给客户', team: '内部团队', public: '公开发布', academic: '学术研究' }
        const purposeMap = { analysis: '投资分析', report: '汇报总结', proposal: '商业提案', training: '培训演示', marketing: '市场推广', plan: '规划方案' }
        const angleMap = { market: '市场分析', competitor: '竞争格局', technology: '技术路线', operation: '运营管理', risk: '风险评估', strategy: '战略规划' }

        const contextTopic = this.formData.topic +
          (this.formData.subtitle ? ' - ' + this.formData.subtitle : '') +
          `[${audienceMap[this.formData.audience] || ''}][${purposeMap[this.formData.purpose] || ''}][${angleMap[this.formData.angle] || ''}]`

        const resp = await fetch(`${API}/generate_outline`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic: contextTopic,
            industry: this.formData.industry,
            model_config_id: this.selectedModelId || undefined
          })
        })
        const data = await resp.json()
        if (data.success) {
          this.outline = data.outline.map(p => ({ ...p, showChart: false, chartTitle: '', chartLabels: '', chartValues: '' }))
          this.hasKbContext = data.has_kb_context
          this.step = 2
        } else {
          this.$message.error('生成失败，请重试')
        }
      } catch (e) {
        this.$message.error('生成失败，请重试')
      }
      this.loading = false
    },
    addPage() {
      this.outline.push({ title: '新页面', type: 'content', showChart: false, showPreview: false, previewContent: null, previewLoading: false, chartTitle: '', chartLabels: '', chartValues: '' })
    },
    removePage(i) {
      this.outline.splice(i, 1)
    },
    toggleChart(page) {
      page.showChart = !page.showChart
    },
    toggleSelectAll() {
      this.outline.forEach(p => this.$set(p, '_selected', this.allSelected))
      this.updateSelected()
    },
    updateSelected() {
      this.selectedPages = this.outline.filter(p => p._selected)
    },
    batchDelete() {
      this.outline = this.outline.filter(p => !p._selected)
      this.selectedPages = []
      this.allSelected = false
    },
    buildOutlineWithCharts() {
      return this.outline.map(p => {
        if (p.showChart && p.chartLabels && p.chartValues) {
          return {
            ...p,
            chart: {
              type: 'bar',
              title: p.chartTitle || p.title,
              data: {
                labels: p.chartLabels.split(',').map(s => s.trim()),
                values: p.chartValues.split(',').map(s => parseFloat(s.trim()) || 0)
              }
            }
          }
        }
        return p
      })
    },
    async generatePPT() {
      this.generating = true
      this.errorMessage = ''
      this.progressMessage = '正在连接服务器...'
      this.progressPercent = 0
      this.progressCurrent = 0

      try {
        const outlineWithCharts = this.buildOutlineWithCharts()

        const resp = await fetch(`${API}/generate_content`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic: this.formData.topic,
            subtitle: this.formData.subtitle,
            industry: this.formData.industry,
            outline: outlineWithCharts,
            template: this.selectedTemplate,
            speaker_notes: this.speakerNotes,
            faithful_mode: this.faithfulMode,
            chinese_typography: this.chineseTypography,
            language: this.language,
            brand_name: this.brandName || undefined,
            brand_logo: this.brandLogo || undefined,
            brand_color: this.brandColor || undefined,
            model_config_id: this.selectedModelId || undefined
          })
        })

        const data = await resp.json()

        if (!data.success) {
          this.errorMessage = data.error || '生成失败，请重试'
          this.generating = false
          return
        }

        const sessionId = data.session_id
        this.progressTotal = outlineWithCharts.length

        if (sessionId) {
          this.progressEventSource = new EventSource(`${API}/progress/${sessionId}`)

          this.progressEventSource.onmessage = (event) => {
            try {
              const status = JSON.parse(event.data)

              if (status.type === 'end') {
                if (this.progressEventSource) {
                  this.progressEventSource.close()
                  this.progressEventSource = null
                }
                return
              }

              this.progressMessage = status.message || '生成中...'
              this.progressPercent = status.progress || 0
              this.progressCurrent = status.current_page || 0
              this.progressTotal = status.total_pages || this.progressTotal

              if (status.stage === 'done') {
                this.downloadUrl = `http://localhost:8000${data.download_url}`
                this.step = 4
                this.generating = false
                this.saveHistory()
                if (this.progressEventSource) {
                  this.progressEventSource.close()
                  this.progressEventSource = null
                }
              }

              if (status.stage === 'error') {
                this.errorMessage = status.message || '生成过程中出错'
                this.generating = false
                if (this.progressEventSource) {
                  this.progressEventSource.close()
                  this.progressEventSource = null
                }
              }
            } catch (e) {
              console.error('解析进度数据失败:', e)
            }
          }

          this.progressEventSource.onerror = () => {
            if (this.progressEventSource) {
              this.progressEventSource.close()
              this.progressEventSource = null
            }
            this.pollForResult(data.download_url)
          }
        }
      } catch (e) {
        this.errorMessage = '网络错误：' + (e.message || '请检查网络连接')
        this.generating = false
      }
    },
    async pollForResult(downloadUrl) {
      let attempts = 0
      const maxAttempts = 60

      const poll = async () => {
        if (!this.generating) return

        attempts++
        if (attempts > maxAttempts) {
          this.errorMessage = '生成超时，请重试'
          this.generating = false
          return
        }

        this.progressMessage = `等待生成完成... (${attempts}/${maxAttempts})`
        this.progressPercent = Math.min(95, 50 + attempts)

        try {
          const testResp = await fetch(`http://localhost:8000${downloadUrl}`, { method: 'HEAD' })
          if (testResp.ok) {
            this.downloadUrl = `http://localhost:8000${downloadUrl}`
            this.progressPercent = 100
            this.progressMessage = '生成完成！'
            this.step = 4
            this.generating = false
            this.saveHistory()
            return
          }
        } catch (e) {}

        setTimeout(poll, 2000)
      }

      setTimeout(poll, 3000)
    },
    formatSize(bytes) {
      if (!bytes) return '0 B'
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / 1024 / 1024).toFixed(1) + ' MB'
    },
    async saveHistory() {
      try {
        await fetch(`${API}/history`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic: this.formData.topic,
            subtitle: this.formData.subtitle,
            industry: this.formData.industry,
            template: this.selectedTemplate,
            outline_json: JSON.stringify(this.outline),
            filename: this.downloadUrl ? this.downloadUrl.split('/').pop() : 'ppt.pptx',
            file_size: 0,
            download_url: this.downloadUrl
          })
        })
      } catch (e) {}
    },
    openTranslator(text, field) {
      this.$refs.translatorRef.open(text)
      this._translateTargetField = field
    },
    handleTranslateInsert(translatedText) {
      // 将翻译结果插入到对应字段
      if (this._translateTargetField === 'topic') {
        this.formData.topic = translatedText
      } else if (this._translateTargetField === 'subtitle') {
        this.formData.subtitle = translatedText
      } else if (this._translateTargetField === 'refContent') {
        this.formData.refContent = translatedText
      }
    },
    reset() {
      this.step = 1
      this.subStep = 1
      this.showConfirm = false
      this.formData = { topic: '', subtitle: '', industry: 'technology', audience: 'investor', purpose: 'analysis', angle: 'market', language: 'zh', refContent: '' }
      this.outline = []
      this.hasKbContext = false
      this.speakerNotes = false
      this.language = 'zh'
      this.brandColor = ''
      this.brandName = ''
      this.brandLogo = ''
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100%;
}

.steps-card {
  margin-bottom: 24px;
  border-radius: 8px;
}

.step-content-card {
  border-radius: 8px;
}

.sub-steps {
  margin-bottom: 32px;
}

.step-title {
  font-size: 24px;
  margin-bottom: 24px;
  color: #262626;
}

.step-hint {
  color: #8c8c8c;
  margin-bottom: 24px;
  font-size: 14px;
}

.step-form {
  max-width: 800px;
}

.industry-radio-group {
  width: 100%;
}

.industry-btn {
  width: 100%;
  text-align: center;
  height: auto;
  padding: 12px 8px;
}

.industry-btn :deep(.anticon) {
  margin-right: 6px;
}

.ind-icon {
  margin-right: 4px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-add-ref {
  margin-top: 8px;
}

.kb-doc-list {
  background: #fafafa;
  border-radius: 8px;
}

.upload-area {
  padding: 40px;
  text-align: center;
  cursor: pointer;
}

.upload-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 15px;
  color: #595959;
  margin-bottom: 4px;
}

.upload-formats {
  font-size: 12px;
  color: #8c8c8c;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.selected-text {
  font-size: 13px;
  color: #1890ff;
  font-weight: 500;
}

.outline-list {
  margin-bottom: 24px;
}

.outline-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 8px;
}

.page-title-input {
  flex: 1;
  min-width: 200px;
}

.page-type-select {
  width: 120px;
}

.btn-add-page {
  margin-top: 12px;
  border-style: dashed;
}

.template-grid {
  margin-bottom: 24px;
}

.template-item {
  text-align: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.template-item:hover {
  background: #f5f5f5;
}

.template-item.active .template-preview {
  box-shadow: 0 0 0 3px #1890ff;
}

.template-preview {
  height: 80px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 13px;
  margin-bottom: 8px;
}

.template-desc {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0;
}

.model-selector {
  margin-bottom: 24px;
}

.option-tip {
  color: #8c8c8c;
  font-size: 13px;
  margin-left: 8px;
}

.advanced-form {
  max-width: 500px;
}

.error-alert {
  margin: 24px 0;
}

.result-card {
  text-align: center;
}
</style>

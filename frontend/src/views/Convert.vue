<template>
  <div class="convert">
    <div class="header">
      <h1>📄 文档一键转PPT</h1>
      <p class="subtitle">上传文档，选择行业，AI自动生成专业PPT</p>
    </div>

    <!-- 步骤导航 -->
    <div class="steps">
      <div class="step" :class="{active: step >= 1, completed: step > 1}">
        <span class="num">1</span><span class="label">上传文档</span>
      </div>
      <div class="line"></div>
      <div class="step" :class="{active: step >= 2, completed: step > 2}">
        <span class="num">2</span><span class="label">选择行业</span>
      </div>
      <div class="line"></div>
      <div class="step" :class="{active: step >= 3}">
        <span class="num">3</span><span class="label">生成PPT</span>
      </div>
    </div>

    <!-- Step 1: 上传文档 -->
    <div v-if="step === 1" class="step-content card">
      <h2>上传您的文档</h2>
      <div class="upload-area" :class="{dragover: isDragover}" 
           @drop.prevent="handleDrop" @dragover="isDragover=true" @dragleave="isDragover=false"
           @click="$refs.fileInput.click()">
        <input type="file" ref="fileInput" @change="handleFileSelect" accept=".txt,.doc,.docx,.pdf" style="display:none">
        <div class="upload-icon">📁</div>
        <p>点击或拖拽文件到这里</p>
        <p class="upload-hint">支持 TXT、Word、PDF 文件</p>
      </div>
      
      <div class="divider"><span>或</span></div>
      
      <h3>直接粘贴文本内容</h3>
      <textarea v-model="documentText" class="doc-textarea" placeholder="在这里粘贴您的文本内容..." rows="10"></textarea>
      
      <div class="actions">
        <button class="btn-secondary" @click="$router.push('/')">返回首页</button>
        <button class="btn-primary" @click="nextStep" :disabled="!documentText.trim()">下一步</button>
      </div>
    </div>

    <!-- Step 2: 选择行业 -->
    <div v-if="step === 2" class="step-content card">
      <h2>选择所属行业</h2>
      <p class="hint">行业模板会影响PPT风格和配色</p>
      
      <div class="industry-grid">
        <div v-for="ind in industries" :key="ind.id" 
             class="industry-card" :class="{active: selectedIndustry === ind.id}"
             @click="selectedIndustry = ind.id">
          <span class="industry-icon">{{ ind.icon }}</span>
          <span class="industry-name">{{ ind.name }}</span>
        </div>
      </div>

      <h3 style="margin-top:40px;">选择模板风格</h3>
      <div class="template-grid">
        <div v-for="t in availableTemplates" :key="t.id" 
             class="template-card" :class="{active: selectedTemplate === t.id}"
             @click="selectedTemplate = t.id">
          <div class="template-preview" :style="{background: t.color}"><span>{{ t.name }}</span></div>
          <p>{{ t.description }}</p>
        </div>
      </div>

      <div class="actions">
        <button class="btn-secondary" @click="step = 1">上一步</button>
        <button class="btn-primary btn-large" @click="generatePPT" :disabled="converting">
          {{ converting ? 'AI分析中...' : '开始转换' }}
        </button>
      </div>
    </div>

    <!-- Step 3: 结果 -->
    <div v-if="step === 3" class="step-content card result">
      <div class="success-icon">🎉</div>
      <h2>转换成功！</h2>
      <p>您的PPT已生成，包含 {{ outlineLength }} 页</p>
      <p class="result-info">行业：{{ resultIndustry }} | 模板：{{ resultTemplate }}</p>
      <div class="download-actions">
        <a :href="downloadUrl" class="btn-primary" download>下载PPTX</a>
        <button class="btn-secondary" @click="reset">再转换一个</button>
      </div>
    </div>
  </div>
</template>

<script>
const API = "http://localhost:8000/api";
export default {
  name: "Convert",
  data() {
    return {
      step: 1,
      documentText: "",
      isDragover: false,
      industries: [],
      selectedIndustry: "general",
      selectedTemplate: "business",
      converting: false,
      downloadUrl: "",
      resultIndustry: "",
      resultTemplate: "",
      outlineLength: 0,
      templates: [
        { id: "academic", name: "学术风", description: "深蓝白色", color: "linear-gradient(135deg, #1a365d, #2c5282)" },
        { id: "business", name: "商务蓝", description: "藏蓝金色", color: "linear-gradient(135deg, #2c5282, #ed8936)" },
        { id: "enterprise", name: "企业蓝", description: "稳重企业", color: "linear-gradient(135deg, #1e3a5f, #3182ce)" },
        { id: "nature", name: "商务绿", description: "绿色清新", color: "linear-gradient(135deg, #276749, #68d391)" },
        { id: "tech", name: "科技风", description: "蓝紫渐变", color: "linear-gradient(135deg, #1a1a4e, #00d4ff)" },
        { id: "gradient", name: "渐变风", description: "彩色活力", color: "linear-gradient(135deg, #ff6b6b, #4ecdc4)" },
        { id: "elegant", name: "商务紫", description: "紫色高贵", color: "linear-gradient(135deg, #553c9a, #9f7aea)" },
        { id: "festive", name: "商务红", description: "红色喜庆", color: "linear-gradient(135deg, #c53030, #fc8181)" },
      ]
    };
  },
  computed: {
    availableTemplates() {
      // 根据行业返回推荐模板
      const industryTemplates = {
        education: ["academic", "nature", "sky"],
        medical: ["simple", "nature", "ocean"],
        ecommerce: ["gradient", "festive", "cyber"],
        finance: ["business", "navy_gold", "classic_blue"],
        technology: ["tech", "cyber", "future"],
        government: ["enterprise", "royal", "academic"],
        realestate: ["business", "gray_elegant", "ink_wash"],
        media: ["gradient", "cyber", "royal"],
        manufacture: ["enterprise", "nature", "classic_blue"],
        general: ["business", "simple", "elegant"]
      };
      const recommended = industryTemplates[this.selectedIndustry] || industryTemplates.general;
      return this.templates.filter(t => recommended.includes(t.id));
    }
  },
  async mounted() {
    // 加载行业列表
    try {
      const resp = await fetch(`${API}/industries`);
      const data = await resp.json();
      if (data.success) this.industries = data.industries;
    } catch (e) {
      this.industries = [
        { id: "education", name: "教育培训", icon: "🎓" },
        { id: "medical", name: "医疗健康", icon: "🏥" },
        { id: "ecommerce", name: "电商零售", icon: "🛒" },
        { id: "finance", name: "金融投资", icon: "💰" },
        { id: "technology", name: "科技互联网", icon: "💻" },
        { id: "government", name: "政府企业", icon: "🏛️" },
        { id: "realestate", name: "房产建筑", icon: "🏗️" },
        { id: "media", name: "传媒广告", icon: "📺" },
        { id: "manufacture", name: "制造业", icon: "⚙️" },
        { id: "general", name: "通用场景", icon: "📋" },
      ];
    }
  },
  methods: {
    handleFileSelect(e) {
      const file = e.target.files[0];
      if (file) this.readFile(file);
    },
    handleDrop(e) {
      this.isDragover = false;
      const file = e.dataTransfer.files[0];
      if (file) this.readFile(file);
    },
    readFile(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.documentText = e.target.result;
      };
      reader.readAsText(file);
    },
    nextStep() {
      if (this.documentText.trim()) this.step = 2;
    },
    async generatePPT() {
      this.converting = true;
      try {
        const resp = await fetch(`${API}/convert_document`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: this.documentText,
            industry: this.selectedIndustry,
            template: this.selectedTemplate
          })
        });
        const data = await resp.json();
        if (data.success) {
          this.downloadUrl = `http://localhost:8000${data.download_url}`;
          this.resultIndustry = data.industry;
          this.resultTemplate = data.template;
          this.outlineLength = data.outline ? data.outline.length : 0;
          this.step = 3;
        } else {
          alert("转换失败，请重试");
        }
      } catch (e) {
        alert("转换失败: " + e.message);
      }
      this.converting = false;
    },
    reset() {
      this.step = 1;
      this.documentText = "";
      this.selectedIndustry = "general";
      this.selectedTemplate = "business";
    }
  }
};
</script>

<style scoped>
.convert { max-width: 1100px; margin: 0 auto; }
.header { text-align: center; margin-bottom: 40px; }
.header h1 { font-size: 32px; margin-bottom: 10px; }
.subtitle { color: #666; font-size: 16px; }
.steps { display: flex; align-items: center; justify-content: center; margin-bottom: 50px; }
.step { display: flex; align-items: center; gap: 10px; color: #999; }
.step.active { color: #667eea; }
.step.completed { color: #48bb78; }
.step .num { width: 36px; height: 36px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.step.active .num { background: #667eea; color: white; }
.step.completed .num { background: #48bb78; color: white; }
.line { width: 80px; height: 2px; background: #e2e8f0; margin: 0 20px; }
.step-content h2 { font-size: 24px; margin-bottom: 20px; }
.hint { color: #666; margin-bottom: 20px; }
.upload-area { border: 2px dashed #e2e8f0; border-radius: 16px; padding: 60px; text-align: center; cursor: pointer; transition: all 0.3s; }
.upload-area:hover, .upload-area.dragover { border-color: #667eea; background: rgba(102,126,234,0.05); }
.upload-icon { font-size: 60px; margin-bottom: 20px; }
.upload-hint { color: #999; font-size: 14px; }
.divider { display: flex; align-items: center; margin: 40px 0; color: #999; }
.divider::before, .divider::after { content: ""; flex: 1; height: 1px; background: #e2e8f0; }
.divider span { padding: 0 20px; }
.doc-textarea { width: 100%; padding: 20px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 14px; resize: vertical; outline: none; }
.doc-textarea:focus { border-color: #667eea; }
.actions { display: flex; gap: 15px; margin-top: 30px; justify-content: center; }
.btn-large { padding: 16px 50px; font-size: 18px; }
.industry-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }
.industry-card { padding: 20px; border: 2px solid #e2e8f0; border-radius: 12px; text-align: center; cursor: pointer; transition: all 0.3s; }
.industry-card:hover { border-color: #667eea; }
.industry-card.active { border-color: #667eea; background: rgba(102,126,234,0.1); }
.industry-icon { display: block; font-size: 36px; margin-bottom: 10px; }
.industry-name { font-size: 14px; }
.template-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.template-card { cursor: pointer; }
.template-preview { height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px; margin-bottom: 8px; }
.template-card.active .template-preview { box-shadow: 0 0 0 3px #667eea; }
.template-card p { font-size: 12px; color: #666; text-align: center; }
.result { text-align: center; padding: 60px 40px; }
.success-icon { font-size: 80px; margin-bottom: 20px; }
.result-info { color: #999; font-size: 14px; margin: 10px 0; }
.download-actions { display: flex; gap: 15px; justify-content: center; margin-top: 30px; }
.download-actions a { text-decoration: none; }
</style>

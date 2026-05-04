"""
DemoPPT 本地知识库系统
- 文档上传 → Chunk分割 → TF-IDF向量化 → SQLite存储
- 搜索时召回相关Chunk，注入PPT生成Prompt
- 零外部依赖，纯Python实现
"""

import os
import re
import sqlite3
import hashlib
import json
import uuid
import datetime
from typing import List, Dict, Tuple, Optional
from collections import Counter
import math

# ============================================================
# 配置
# ============================================================
KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
os.makedirs(KB_DIR, exist_ok=True)
DB_PATH = os.path.join(KB_DIR, "kb_store.db")
CHUNK_SIZE = 400  # 每个chunk的字符数
CHUNK_OVERLAP = 80  # overlap防止句子截断

# ============================================================
# 数据库初始化
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT,
            file_type TEXT,
            size INTEGER,
            uploaded_at TEXT,
            title TEXT,
            summary TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            doc_id TEXT,
            chunk_index INTEGER,
            content TEXT,
            chunk_hash TEXT,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        )
    """)
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
            content, content=chunks, content_rowid=rowid
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ============================================================
# 文本分块
# ============================================================
def chunk_text(text: str) -> List[str]:
    """将长文本分割成重叠的chunk"""
    import sys
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    if len(text) <= CHUNK_SIZE:
        return [text.strip()] if text.strip() else []
    
    chunks = []
    pos = 0
    while pos < len(text):
        chunk_end = min(pos + CHUNK_SIZE, len(text))
        
        # 尝试在句子边界截断
        if chunk_end < len(text):
            # 找最后一个句号
            last_period = text.rfind('。', pos + CHUNK_SIZE - 100, chunk_end)
            if last_period > pos:
                chunk_end = last_period + 1
            else:
                # 找最后一个逗号
                last_comma = text.rfind('，', pos + CHUNK_SIZE - 50, chunk_end)
                if last_comma > pos:
                    chunk_end = last_comma + 1
        
        chunk = text[pos:chunk_end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 移动位置（带重叠）
        pos = chunk_end - CHUNK_OVERLAP
        if pos <= 0 or not chunk:
            pos = chunk_end
    
    return [c for c in chunks if c]

# ============================================================
# TF-IDF 向量化（无需外部依赖）
# ============================================================
class TFIDFVectorizer:
    """简单的TF-IDF向量化，用于计算文本相似度"""
    
    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_count = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """中英文混合分词"""
        # 中文：按标点分词
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', text.lower())
        # 简单bigram扩展（对中文效果好）
        words = []
        for t in tokens:
            if re.search(r'[\u4e00-\u9fff]', t):
                words.append(t)
                # 相邻汉字组合
                for i in range(len(t) - 1):
                    words.append(t[i:i+2])
            else:
                words.append(t)
        return words
    
    def fit(self, texts: List[str]):
        """构建TF-IDF模型"""
        self.doc_count = len(texts)
        doc_freq = Counter()
        total_tokens = []
        
        for text in texts:
            tokens = self._tokenize(text)
            total_tokens.append(tokens)
            doc_freq.update(set(tokens))
        
        # 计算IDF
        self.vocab = {word: i for i, (word, _) in enumerate(doc_freq.most_common(5000))}
        self.idf = {}
        for word, df in doc_freq.items():
            self.idf[word] = math.log((self.doc_count + 1) / (df + 1)) + 1
    
        return self
    
    def transform(self, texts: List[str]) -> List[List[float]]:
        """将文本转为TF-IDF向量"""
        vectors = []
        for text in texts:
            tokens = self._tokenize(text)
            tf = Counter(tokens)
            vec = [0.0] * len(self.vocab)
            for word, count in tf.items():
                if word in self.vocab:
                    tf_val = count / len(tokens) if tokens else 0
                    vec[self.vocab[word]] = tf_val * self.idf.get(word, 1.0)
            # L2归一化
            norm = math.sqrt(sum(v*v for v in vec))
            if norm > 0:
                vec = [v/norm for v in vec]
            vectors.append(vec)
        return vectors
    
    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """余弦相似度"""
        dot = sum(a*b for a,b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(v*v for v in vec1))
        norm2 = math.sqrt(sum(v*v for v in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

# ============================================================
# 知识库核心类
# ============================================================
class KnowledgeBase:
    
    def __init__(self):
        self.vectorizer = TFIDFVectorizer()
        self._chunks: List[str] = []
        self._chunk_vectors: List[List[float]] = []
        self._chunk_doc_ids: List[str] = []
        self._chunk_ids: List[str] = []
        self._load_all_chunks()
    
    def _load_all_chunks(self):
        """从数据库加载所有chunks并构建索引"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, content FROM chunks")
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return
        
        self._chunk_ids = [r[0] for r in rows]
        self._chunks = [r[1] for r in rows]
        
        # 批量构建向量
        self.vectorizer.fit(self._chunks)
        self._chunk_vectors = self.vectorizer.transform(self._chunks)
    
    def add_document(self, content: str, filename: str, file_type: str, title: str = "") -> str:
        """添加文档到知识库"""
        doc_id = str(uuid.uuid4())[:8]
        
        # 分块
        chunks = chunk_text(content)
        
        # 生成summary（取前200字）
        summary = content[:200].strip() + "..." if len(content) > 200 else content
        
        # 存入数据库
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO documents (id, filename, file_type, size, uploaded_at, title, summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (doc_id, filename, file_type, len(content), datetime.datetime.now().isoformat(), title or filename, summary)
        )
        
        chunk_ids = []
        for i, chunk_content in enumerate(chunks):
            chunk_id = str(uuid.uuid4())[:12]
            chunk_hash = hashlib.md5(chunk_content.encode()).hexdigest()[:8]
            c.execute(
                "INSERT INTO chunks (id, doc_id, chunk_index, content, chunk_hash) VALUES (?, ?, ?, ?, ?)",
                (chunk_id, doc_id, i, chunk_content, chunk_hash)
            )
            chunk_ids.append(chunk_id)
        
        conn.commit()
        conn.close()
        
        # 重新加载索引
        self._load_all_chunks()
        
        return doc_id
    
    def search(self, query: str, top_k: int = 5, doc_id: Optional[str] = None) -> List[Dict]:
        """搜索知识库，返回最相关的chunks"""
        if not self._chunks:
            return []
        
        # 对查询文本向量化
        query_vec = self.vectorizer.transform([query])[0]
        
        # 计算与所有chunks的相似度
        similarities = []
        for i, chunk_vec in enumerate(self._chunk_vectors):
            sim = self.vectorizer.compute_similarity(query_vec, chunk_vec)
            similarities.append((i, sim))
        
        # 排序取top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 获取结果
        results = []
        for idx, sim in similarities[:top_k]:
            if sim < 0.05:  # 相似度阈值
                break
            results.append({
                "chunk_id": self._chunk_ids[idx],
                "content": self._chunks[idx],
                "score": round(sim, 4)
            })
        
        return results
    
    def get_context_for_prompt(self, topic: str, industry: str = "", top_k: int = 5) -> str:
        """为PPT生成构建上下文Prompt片段"""
        query = f"{industry} {topic}" if industry else topic
        results = self.search(query, top_k=top_k)
        
        if not results:
            return ""
        
        context_parts = ["【知识库参考内容】"]
        for r in results:
            context_parts.append(f"[相关度{r['score']}] {r['content']}")
        
        return "\n\n".join(context_parts)
    
    def list_documents(self) -> List[Dict]:
        """列出知识库中所有文档"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, filename, file_type, size, uploaded_at, title, summary FROM documents ORDER BY uploaded_at DESC")
        rows = c.fetchall()
        conn.close()
        
        return [
            {
                "id": r[0],
                "filename": r[1],
                "file_type": r[2],
                "size": r[3],
                "uploaded_at": r[4],
                "title": r[5],
                "summary": r[6]
            }
            for r in rows
        ]
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        affected = c.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            self._load_all_chunks()
        
        return affected > 0
    
    def get_stats(self) -> Dict:
        """获取知识库统计"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM documents")
        doc_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = c.fetchone()[0]
        c.execute("SELECT SUM(size) FROM documents")
        total_size = c.fetchone()[0] or 0
        conn.close()
        
        return {
            "document_count": doc_count,
            "chunk_count": chunk_count,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }


# 全局单例
kb = KnowledgeBase()

# ============================================================
# 文档解析（支持TXT/MD）
# ============================================================
def parse_txt(content: bytes) -> str:
    """解析纯文本"""
    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
        try:
            return content.decode(encoding)
        except:
            continue
    return content.decode('utf-8', errors='ignore')

def parse_document(file_path: str) -> str:
    """根据文件类型解析文档"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.txt', '.md', '.csv']:
        with open(file_path, 'rb') as f:
            return parse_txt(f.read())
    elif ext == '.pdf':
        # 尝试用PyPDF2
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
        except ImportError:
            return f"[PDF文件需要安装PyPDF2: pip install PyPDF2] 文件路径: {file_path}"
        except:
            return f"[PDF解析失败] 文件路径: {file_path}"
    elif ext in ['.docx', '.doc']:
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            return f"[Word文件需要安装python-docx: pip install python-docx] 文件路径: {file_path}"
        except:
            return f"[Word解析失败] 文件路径: {file_path}"
    else:
        return f"[不支持的文件格式: {ext}]"

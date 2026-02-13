# 电商智能客服Agent 🤖

基于RAG（检索增强生成）架构的电商智能客服系统，集成向量数据库和大语言模型，为企业提供7×24小时智能化客户服务。

## 🌟 核心特性

### 🔍 RAG架构
- **智能检索**：基于FAISS向量数据库的语义相似度搜索
- **知识增强**：结合业务知识库生成准确、专业的回复
- **多模型支持**：兼容通义千问和OpenAI双AI平台

### 🧠 核心功能
- ✅ 智能问答：基于业务知识的精准回答
- ✅ 会话管理：支持多轮对话和上下文理解
- ✅ 个性化推荐：根据用户偏好推荐相关商品
- ✅ 状态跟踪：实时监控系统运行状态
- ✅ **图片识别**：支持商品图片上传和智能识别 🆕

## 🛠️ 技术架构

```
用户输入 → 向量检索 → 知识匹配 → AI生成 → 专业回复
   ↓         ↓         ↓         ↓         ↓
"怎么退货" → 相似度搜索 → 退货流程知识 → 结构化回答

图片上传 → 阿里云API → 商品识别 → 智能客服
   ↓         ↓         ↓         ↓
"image:商品.jpg" → 图像分析 → 商品信息 → 相关服务
```

### 技术栈
- **核心框架**：Python 3.8+
- **AI平台**：通义千问 / OpenAI GPT
- **向量检索**：FAISS + OpenAI Embeddings
- **图像识别**：阿里云图片识别API 🆕
- **开发框架**：LangChain
- **环境管理**：python-dotenv

## 📁 项目结构

```
电商agent客服/
├── main.py                 # 主程序入口
├── config.py              # 配置管理
├── requirements.txt       # 依赖清单
├── .env                   # 环境变量配置
├── agents/                # Agent模块
│   └── qwen_agent.py     # 通义千问客服Agent
├── memory/                # 内存管理
│   └── enhanced_memory.py # 增强型会话内存
├── tools/                 # 工具模块 🆕
│   └── image_recognition.py # 图片识别工具
└── knowledge/             # 知识库模块
    └── ecommerce_kb.py   # 电商业务知识
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/cthsss/cth-agent.git
cd cth-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. API配置
在 `.env` 文件中配置API密钥：

```env
# 通义千问API Key（推荐）
DASHSCOPE_API_KEY=your_dashscope_api_key

# OpenAI API Key（备选）
OPENAI_API_KEY=your_openai_api_key

# 阿里云图片识别API配置 🆕
ALIYUN_IMAGE_API_KEY=your_api_key
ALIYUN_IMAGE_API_SECRET=your_api_secret
ALIYUN_IMAGE_APP_CODE=your_app_code
```

### 3. 运行系统
```bash
python main.py
```

## 💬 使用示例

### 文本对话
```
🚀 电商智能客服启动中...
✅ 使用 QWEN API 服务
📦 正在加载向量数据库...
✅ 向量数据库初始化完成！
📊 向量数据库状态: {'status': 'initialized', 'vector_count': 8}

✅ 客服系统启动成功！
💬 开始对话（输入 'quit' 退出）:
💡 支持文本对话和图片识别
💡 图片识别格式: image:图片路径
--------------------------------------------------

👤 用户: 怎么退货？
🔄 正在检索相关信息...
🤖 客服: 您好！退货流程如下：
1. 在订单详情页提交退货申请
2. 选择退货原因并上传商品照片
3. 等待客服审核（通常1-2个工作日）
4. 审核通过后按提示寄回商品
5. 收到退货后3个工作日内退款到账
```

### 图片识别 🆕
```
👤 用户: image:test_product.jpg
📸 正在识别图片: test_product.jpg
✅ 图片识别完成！
🔍 识别结果:
   product_name: 智能手机
   category: 电子产品
   confidence: 0.95
   price_range: 2000-3000元
   similar_products: 3

🔄 正在基于图片信息为您提供相关服务...
🤖 客服: 您上传的商品是智能手机，属于电子产品类别。
我可以为您提供以下服务：
1. 产品详细介绍和参数查询
2. 价格比较和优惠信息
3. 购买建议和使用指导
4. 售后服务和保修政策
请问您想了解哪方面的信息？
```

## 🎯 适用场景

- 🛒 电商平台客服自动化
- 📞 24小时在线咨询服务
- 📊 客户问题标准化处理
- 💰 降低人工客服成本
- 📈 提升客户服务效率
- 📸 商品图片智能识别 🆕

## 📊 项目优势

| 特性 | 传统客服 | 本系统 |
|------|----------|--------|
| 响应速度 | 人工响应 | 秒级回复 |
| 服务时间 | 工作时间 | 7×24小时 |
| 回答一致性 | 因人而异 | 标准化输出 |
| 成本控制 | 人力成本高 | 自动化低成本 |
| 知识更新 | 培训周期长 | 实时动态更新 |
| 图片识别 | 需要人工 | AI智能识别 🆕 |

## 📚 详细文档

- [USAGE.md](USAGE.md) - 详细使用指南
- [IMAGE_RECOGNITION_USAGE.md](IMAGE_RECOGNITION_USAGE.md) - 图片识别功能说明 🆕
- [API_CONFIG.md](API_CONFIG.md) - API配置详解

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题，请提交GitHub Issue或联系项目维护者。
"""
电商客服向量数据库模块
专门负责知识库的向量化存储和相似性检索
支持多种嵌入模型
"""

import os
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough

class EcommerceVectorDB:
    """电商客服专用向量数据库"""
    
    def __init__(self):
        self.db = None
        self.retriever = None
        self.embeddings = None
        self.is_initialized = False
        self.provider = None
        
    def build_knowledge_base(self) -> tuple[List[str], List[Dict[str, str]]]:
        """构建电商客服知识库"""
        print("📚 正在构建电商客服知识库...")
        
        knowledge_base = [
            {
                "question": "退货流程是什么？",
                "answer": "1. 在订单详情页提交退货申请\n2. 选择退货原因并上传商品照片\n3. 等待客服审核（通常1-2个工作日）\n4. 审核通过后按提示寄回商品\n5. 收到退货后3个工作日内退款到账"
            },
            {
                "question": "商品保修多久？",
                "answer": "本店所有商品均提供1年全国联保服务。购买后凭发票和保修卡可在任一授权维修点享受免费维修服务。"
            },
            {
                "question": "支持哪些支付方式？",
                "answer": "我们支持支付宝、微信支付、银行卡在线支付以及货到付款等多种支付方式，您可以根据需要自由选择。"
            },
            {
                "question": "配送时间需要多久？",
                "answer": "一般情况下，下单后1-3个工作日发货，根据收货地址不同，配送时间通常为2-7个工作日。偏远地区可能需要更长时间。"
            },
            {
                "question": "如何联系人工客服？",
                "answer": "您可以通过以下方式联系人工客服：\n- 在线客服：点击右下角'联系客服'按钮\n- 电话客服：拨打400-xxx-xxxx\n- 微信客服：添加微信号 xxx_service\n工作时间：每天9:00-21:00"
            },
            {
                "question": "商品质量问题怎么办？",
                "answer": "如果您收到的商品存在质量问题：\n1. 请在签收时当场验货\n2. 如发现问题立即拍照留存证据\n3. 联系客服申请换货或退款\n4. 我们承担往返运费并优先处理"
            },
            {
                "question": "优惠券怎么使用？",
                "answer": "优惠券使用方法：\n1. 在购物车页面选择可用优惠券\n2. 确认订单金额满足使用条件\n3. 系统自动抵扣相应金额\n4. 注意查看有效期和使用范围"
            },
            {
                "question": "发票怎么开？",
                "answer": "开票流程：\n1. 下单时选择'需要发票'\n2. 填写发票抬头和税号\n3. 选择电子发票或纸质发票\n4. 发货后3个工作日内开具并发送"
            }
        ]
        
        # 分离问题和答案
        texts = [item["answer"] for item in knowledge_base]
        metadatas = [{"question": item["question"], "answer": item["answer"]} for item in knowledge_base]
        
        print(f"✅ 知识库构建完成，共 {len(knowledge_base)} 条知识")
        return texts, metadatas
    
    def initialize(self) -> bool:
        """初始化向量数据库"""
        try:
            print("📄 正在初始化向量数据库...")
            
            # 构建知识库
            texts, metadatas = self.build_knowledge_base()
            
            # 获取嵌入模型
            self.embeddings = self.get_embeddings_model()
            
            # 创建向量数据库
            self.db = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
            self.retriever = self.db.as_retriever(search_kwargs={"k": 1})
            
            self.is_initialized = True
            print(f"✅ 向量数据库初始化完成！(使用 {self.provider} 模型)")
            return True
            
        except Exception as e:
            print(f"❌ 向量数据库初始化失败: {e}")
            return False
    
    def search_similar(self, query: str, k: int = 1) -> List[Dict[str, Any]]:
        """搜索相似内容"""
        if not self.is_initialized:
            raise RuntimeError("向量数据库未初始化")
        
        try:
            # 执行相似性搜索
            results = self.db.similarity_search_with_score(query, k=k)
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "question": doc.metadata.get("question", ""),
                    "answer": doc.metadata.get("answer", doc.page_content),
                    "similarity_score": float(score),
                    "content": doc.page_content
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def get_retriever(self):
        """获取检索器"""
        if not self.is_initialized:
            raise RuntimeError("向量数据库未初始化")
        return self.retriever
    
    def add_knowledge(self, question: str, answer: str):
        """动态添加新知识"""
        if not self.is_initialized:
            raise RuntimeError("向量数据库未初始化")
        
        try:
            # 添加新文本到数据库
            self.db.add_texts(
                texts=[answer],
                metadatas=[{"question": question, "answer": answer}]
            )
            print(f"✅ 新知识已添加: {question}")
            
        except Exception as e:
            print(f"❌ 添加知识失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        if not self.is_initialized:
            return {"status": "not initialized"}
        
        try:
            # 获取向量数量（近似）
            vector_count = len(self.db.index_to_docstore_id) if hasattr(self.db, 'index_to_docstore_id') else 0
            
            return {
                "status": "initialized",
                "vector_count": vector_count,
                "model": self.provider,
                "search_top_k": 1
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


    def get_embeddings_model(self):
        """根据配置获取合适的嵌入模型"""
        dashscope_key = os.getenv('DASHSCOPE_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if dashscope_key:
            print("🔧 使用通义千问嵌入模型...")
            try:
                from langchain_community.embeddings import DashScopeEmbeddings
                self.provider = "dashscope"
                return DashScopeEmbeddings(
                    dashscope_api_key=dashscope_key,
                    model="text-embedding-v1"
                )
            except ImportError:
                print("⚠️  通义千问嵌入模型不可用，尝试备用方案...")
        
        if openai_key:
            print("🔧 使用OpenAI嵌入模型...")
            try:
                from langchain_openai import OpenAIEmbeddings
                self.provider = "openai"
                return OpenAIEmbeddings(
                    timeout=60,
                    max_retries=3
                )
            except ImportError:
                print("⚠️  OpenAI嵌入模型不可用...")
        
        # 备用方案：使用简单的文本哈希
        print("🔧 使用基础文本处理...")
        self.provider = "basic"
        return BasicTextEmbeddings()


class BasicTextEmbeddings:
    """基础文本嵌入模型（备用方案）"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """为文档列表生成嵌入向量"""
        return [self._simple_embed(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """为查询文本生成嵌入向量"""
        return self._simple_embed(text)
    
    def _simple_embed(self, text: str) -> List[float]:
        """简单的文本向量化方法"""
        # 使用字符频率作为简单向量
        char_freq = {}
        for char in text.lower():
            if char.isalnum():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # 创建固定长度向量
        vector = []
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        for char in chars:
            vector.append(char_freq.get(char, 0) / len(text) if text else 0)
        
        return vector
    
    def __call__(self, text: str) -> List[float]:
        """使对象可调用"""
        return self.embed_query(text)

# 全局向量数据库实例
vector_db = EcommerceVectorDB()

if __name__ == "__main__":
    # 测试向量数据库功能
    print("=== 电商客服向量数据库测试 ===\n")
    
    # 初始化数据库
    if vector_db.initialize():
        print("✅ 数据库初始化成功\n")
        
        # 测试搜索功能
        test_queries = [
            "怎么退货？",
            "支持支付宝吗？",
            "发货要几天？"
        ]
        
        for query in test_queries:
            print(f"🔍 搜索: '{query}'")
            results = vector_db.search_similar(query)
            
            if results:
                result = results[0]
                print(f"   相关问题: {result['question']}")
                print(f"   相似度: {result['similarity_score']:.3f}")
                print(f"   答案预览: {result['answer'][:50]}...")
            else:
                print("   未找到相关结果")
            print()
        
        # 显示统计信息
        stats = vector_db.get_stats()
        print("📊 数据库统计:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print("❌ 数据库初始化失败")
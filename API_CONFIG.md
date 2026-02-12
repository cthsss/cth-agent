# API配置说明

## 通义千问配置（推荐）

1. 访问 [阿里云百炼平台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 创建API Key
4. 将获得的API Key填入 `.env` 文件：
   ```
   DASHSCOPE_API_KEY=your_actual_api_key_here
   ```

## 备用方案

如果没有千问API Key，可以：
1. 继续使用现有的OpenAI API Key
2. 或者使用我提供的简化模拟版本进行测试

## 测试当前配置

运行以下命令检查配置状态：
```bash
python test_api_config.py
```
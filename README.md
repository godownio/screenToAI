# screenToAI 颗秒算法

一个用于个人学习/复盘的桌面小工具：按下全局快捷键后截屏并做 OCR，将识别到的文字直接发送给 DeepSeek 生成“解题提示”，悬浮窗只展示 DeepSeek 的回答。

不建议也不支持将该工具用于考试、竞赛、面试等有明确规则限制的场景；请遵守所在平台与活动规则。

但是下次谁再出出生算法题，直接上这个

效果：1分钟刷三道leetcode最难题，页面干净下只要页面能装下题目就是秒

!\[screenToAI]\(https\://typora-202017030217.oss-cn-beijing.aliyuncs.com/typora/screenToAI.gif null)

## 快速开始（Windows）

1. 安装 Python 3.10+
2. 安装依赖

```powershell
pip install -r requirements.txt
```

1. 配置 OCR key、配置deepseek key
   - 推荐：腾讯云在线 OCR（需要开通服务并配置 `TENCENT_SECRET_ID / TENCENT_SECRET_KEY`）
   - 可选：本地 Tesseract OCR（配置 `TESSERACT_CMD`，或默认安装到 `C:\Program Files\Tesseract-OCR\tesseract.exe`）（很垃圾，要自己训练一遍）
2. 复制并编辑环境变量，env才有效

```powershell
copy .env.example .env
```

1. 运行

```powershell
python -m screen_to_ai
```

## 使用方式

- 全局快捷键：`Ctrl + Shift + O`（可用 `SCREEN_TO_AI_HOTKEY` 修改）
- 翻页快捷键：
  - 下翻：`Ctrl + Shift + L`（`SCREEN_TO_AI_PAGE_DOWN_HOTKEY`）或者`Ctrl + Shift + ↑`
  - 上翻：`Ctrl + Shift + P`（`SCREEN_TO_AI_PAGE_UP_HOTKEY`）或者`Ctrl + Shift + ↓`
- 触发后：截取主屏幕并 OCR，然后调用 DeepSeek，悬浮窗显示 DeepSeek 回答
- 悬浮窗支持：
  - 关闭/隐藏
  - 复制 DeepSeek 回答
  - 打开输出目录（保存截图与 OCR 文本）

## 环境变量

- `SCREEN_TO_AI_HOTKEY`：快捷键（pynput 格式，默认 `<ctrl>+<shift>+o`）
- `SCREEN_TO_AI_PAGE_DOWN_HOTKEY`：下翻快捷键（默认 `<ctrl>+<shift>+l`）
- `SCREEN_TO_AI_PAGE_UP_HOTKEY`：上翻快捷键（默认 `<ctrl>+<shift>+p`）
- `SCREEN_TO_AI_OUT_DIR`：输出目录（默认 `.screen_to_ai`）
- `SCREEN_TO_AI_OCR_PROVIDER`：OCR 提供方（`tencent` 或 `tesseract`）
- `SCREEN_TO_AI_OCR_LANG`：tesseract 语言（默认 `eng`，中文可用 `chi_sim`，需安装对应语言包）
- `TENCENT_SECRET_ID` / `TENCENT_SECRET_KEY`：腾讯云在线 OCR 凭证
- `TENCENT_REGION`：腾讯云区域（默认 `ap-guangzhou`）
- `TENCENT_OCR_MODE`：识别模式（`accurate` 或 `basic`，默认 `accurate`）
- `TESSERACT_CMD`：tesseract 可执行文件路径（当 `SCREEN_TO_AI_OCR_PROVIDER=tesseract` 时使用）
- `DEEPSEEK_API_KEY`：启用 DeepSeek
- `DEEPSEEK_BASE_URL`/`DEEPSEEK_MODEL`：自定义接入地址与模型名


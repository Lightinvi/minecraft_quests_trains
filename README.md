# Minecraft Quests Translator

此工具可自動將 Minecraft FTB 任務模組的 `.snbt` 任務文字翻譯成繁體中文，並保留原始內容，便於玩家使用及開發者調整。

---

## 📁 結構

```
minecraft_quests_trans/
├── app.py                  # 主執行檔
├── contrast_table/         # 儲存自訂詞彙對照表的 JSON 檔
├── trans_target/           # 存放需翻譯的 .snbt 任務檔案
├── README.md               # 使用說明文件
└── .venv/                  # Python 虛擬環境 (建議使用)
```

## 📦 安裝相依套件

進入專案資料夾後，於終端機中執行：

```bash
pip install -r requirements.txt
```

### 主要使用到的套件

- `googletrans`：進行自動翻譯
- `ftb_snbt_lib`：解析與輸出 `.snbt` 檔案

---

## 📘 對照表格式

可於 `contrast_table/` 資料夾中放置多個 `.json` 檔案，用於關鍵詞優先翻譯對照。

範例：

```json
{
  "Oak Boat With Chest": "儲物箱橡木船",
  "Oak Boat": "橡木船"
}
```

🔁 對照表會依照 key 字串長度排序，保證最長匹配優先。

---

## 🚀 使用步驟

1. 將欲翻譯的 `.snbt` 任務檔案放入 `trans_target/` 資料夾中。
2. 執行翻譯：

```bash
python app.py
```

3. 程式會自動解析每個任務內容（title、subtitle、description、text）並附加翻譯。
4. 翻譯內容會儲存回原始檔案，格式為原文在後，翻譯在前。

---

## 🧠 注意事項

- 建議使用虛擬環境執行，以避免套件版本衝突。
- 若 `contrast_table/` 資料夾不存在，將不載入對照表功能。

---

🛠 Made with ❤️ by Lightinvi Peng

# GitHub 倉庫設定指南

## 建立新倉庫步驟

### 1. 在 GitHub 網站建立倉庫
1. 登入 GitHub
2. 點擊右上角的 "+" 號，選擇 "New repository"
3. 倉庫名稱：`CRS-compare-TWD67-vs-WGS84-coordinate-analysis`
4. 描述：Analysis of coordinate differences between TWD67 and WGS84 reference systems for Taiwan weather stations
5. 設定為 Public 或 Private
6. **不要**勾選 "Add a README file"（我們已經有了）
7. 點擊 "Create repository"

### 2. 初始化本地 Git 倉庫
```bash
# 確保在正確的目錄
cd "c:\軟體\遙測與空資\lesson 2 ex.2\class_1-main\class_1-main"

# 初始化 Git 倉庫
git init

# 設定遠端倉庫（替換 YOUR_USERNAME 為你的 GitHub 用戶名）
git remote add origin https://github.com/YOUR_USERNAME/CRS-compare-TWD67-vs-WGS84-coordinate-analysis.git

# 添加所有檔案
git add .

# 提交變更
git commit -m "Initial commit: Coordinate analysis between TWD67 and WGS84 systems

- Added coordinate_analysis.py for dual coordinate system analysis
- Added comprehensive visualization with Folium maps
- Added statistical analysis with matplotlib/seaborn
- Added detailed README documentation
- Generated analysis results showing ~850m average coordinate differences"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 3. 檔案結構說明
```
CRS-compare-TWD67-vs-WGS84-coordinate-analysis/
├── .env                    # API 金鑰（不會上傳到 GitHub）
├── .env.example           # API 金鑰範例
├── .gitignore             # Git 忽略檔案
├── README.md              # 原始專案說明
├── README_coordinate_analysis.md  # 坐標分析專門說明
├── requirements.txt       # Python 套件依賴
├── coordinate_analysis.py # 主要分析程式
├── sample_api_data.py     # API 樣本資料獲取
├── GITHUB_SETUP_GUIDE.md  # 本設定指南
└── outputs/               # 分析結果輸出（不會上傳）
    ├── coordinate_analysis_*.csv
    ├── coordinate_stats_*.json
    ├── coordinate_comparison_map_*.html
    └── coordinate_analysis_plot_*.png
```

### 4. 重要注意事項

#### 安全性
- `.env` 檔案包含 API 金鑰，已在 `.gitignore` 中設定為不上傳
- 確保不要意外上傳包含敏感資訊的檔案

#### 輸出檔案
- `outputs/` 目錄包含分析結果，已在 `.gitignore` 中設定為不上傳
- 這些檔案很大且會定期更新，不適合放在版本控制中

#### 程式說明
- 程式分析氣象站API中的兩種坐標系統（TWD67/TWD97 vs WGS84）
- 發現平均坐標差異約 850 公尺
- 提供互動式地圖和統計分析圖表

### 5. 後續維護
- 當需要更新程式時，使用標準的 Git 工作流程：
  ```bash
  git add .
  git commit -m "描述你的變更"
  git push
  ```

### 6. 分享倉庫
建立完成後，你可以：
- 分享倉庫連結給其他人
- 在 README 中添加更多詳細說明
- 考慮添加 Issues 來追蹤功能需求或 bug 報告

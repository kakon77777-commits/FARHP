# FARHP 系列 v0.7 完整包

本包包含第一至第七篇論文、三層規格、`FARHP-Core v0.3` 原始碼、二十一項測試、合成 WAV、相位變換比較圖與匿名盲聽包。

## 建議閱讀順序

1. 系列總篇；
2. 數學結構；
3. 聲學與知覺邊界；
4. 離散編碼；
5. 單框架系統；
6. 軌跡追蹤；
7. 相位控制與生成。

## 工程啟動

```bash
cd 工程/farhp_core_v0.3
python -m pip install -e .
python -m unittest discover -s tests -v
farhp --help
```

盲聽材料位於：

```text
工程/farhp_core_v0.3/artifacts/phase_transform_demo/blind_listening_pack/
```

這些結果屬於研究原型與合成回歸，不是自然語音或人類知覺的最終證明。

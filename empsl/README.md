# EMPSL 當前工作區

目前權威節點是 [`v0.4/`](v0.4/)：已包含 128 原子、256 受控種子變體、六槽字形、30 條合法性規則、4,096 筆符合性語料，以及 Node／Python 雙引擎驗證。

快速驗證：

```powershell
cd v0.4
node tests/test_core_v0.4.js
python tools/empsl_v04_batch_check.py
```

下一個主線版本是 v0.5：Versioned Lexicon、Typed AST、Type Inference、Compiler 與 Decompiler。Stable ID 不得被 PUA、字形或字型檔取代。

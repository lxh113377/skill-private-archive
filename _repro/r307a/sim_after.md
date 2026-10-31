---
name: SIM-BEFORE
version: 1.0.0
---

# 模拟改后件（人为多两条命令声明）

写产物：
python -c "open('a.json','w').write('{}')" 这条命令把结果写入 a.json
python -c "open('b.md','w').write('x')" 这条命令把摘要写入 b.md
python -c "open('c.txt','w').write('y')" 这条命令把日志输出到 c.txt

# r310 · Lead 独立 ground-truth（审计逐字吸收度尺用，先于 A1 交付落盘）

方法（与臂独立但我可复跑）：git show HEAD 取两件现值全文；从两份 edits.json 取 op=insert 的 new，
剔注释/空行后取**首个正文行**验在现值；另数钉定注释定位器（r306a 逐字钉定 / r307b 逐字钉定）出现次数。

| 件 | inserts | 定位器注释 | 首行命中 | HEAD 现值 |
|---|---|---|---|---|
| A-prompt-better | 5 | 4 | 5/5 | 35594B |
| frontend-skill | 5 | 5 | 5/5 | 15540B |

解释（预登记，防读错）：A 臂 4<5 是因为 E6=我 Lead 追加的版本历史行（自写、无上游块）⇒ 它不该带定位器；
F 臂 F2-F6 五条都带 ⇒ 5=5。⇒ 尺若报 A 臂 locators=5 或 F 臂 4 ⇒ 口径不同，先问它怎么数。
臂若报 blocks_present<total ⇒ 说明它读错对象或件被改写过（broken/partial），我拿本表对质。

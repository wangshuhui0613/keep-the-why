# PR 检查清单

提 PR 前先读 [CONTRIBUTING](../CONTRIBUTING.md)。最有价值的贡献是「你用的时候哪里卡住了」。

## 改了什么

<!-- 逐条列出改动 -->

## 为什么改

<!-- 问题是什么、不改会怎样；附 issue 链接（如有） -->

## 对已有用户有没有破坏性

- [ ] 无破坏性（纯新增 / 文案修正）
- [ ] 有破坏性（删文件、改结构、改规则）——已在 CHANGELOG「变更」节写清影响与迁移方式

## 自检

- [ ] 跑过 `python tools/vault_health_check.py --root .`，输出 `PASS`
- [ ] 跑过 `python -m unittest discover -s tests`，全部通过
- [ ] **没有个人信息**：真实姓名、公司名、项目名、令牌都没进 diff
- [ ] 新增或删除了 `.md` 文件、或改了体检输出数字：已按 CONTRIBUTING 把新数字同步进 `docs/_gif-scenes.html` 第 5 屏并重建 `demo.gif`
- [ ] 结构变更（新增或删除目录、模板、命令、检查项）已写进 CHANGELOG 的「变更」节

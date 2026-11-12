from pathlib import Path
p=Path("STATUS.md"); t=p.read_text(encoding="utf-8")
old="- 没到收敛：只是到点停下。还差的："
assert old in t
t=t.replace(old,"- `qu` 补测：和 `qo` 直接盲比 4/4 选 `qu`。开放评审集中在三件事：Op.60 第 7 段没铺垫、后半段绕圈、替人物概括心理（详见 `试验记录.md`），下一轮从这里开始。\n"+old)
p.write_text(t,encoding="utf-8")

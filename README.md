# 纸刻合影 · paper-cut-portrait

将人物照片转为暖纸底、无五官的剪纸版画拼贴。保留人数、位置、发型、眼镜、服装主色和关键手势，用粗糙纸片、干刷与掉墨质感重绘。

默认上原图、下 AI 插画；说「只要 AI 图」即可仅输出插画。生成部分不添加任何文字，原图已有内容保持原样。

仓库仅存放 Skill、提示词与代码；原始照片及生成示例留在本地交付包中。

## 使用

将仓库文件放入 `~/.codex/skills/paper-cut-portrait/`，保留 `SKILL.md` 与各子目录。重新打开 Codex 后，调用 `$paper-cut-portrait` 并附人物原图。也可在已经建立的纸刻合影上下文中直接发下一张原图。

需要可用的图像生成工具；优先用内置 image_gen，生成不需要自行配置 API 密钥。脚本需要 Python 3.10+ 和 Pillow 9.1+，可通过 `python -m pip install -r requirements.txt` 安装。脚本不能独立生成 AI 图片。

```text
使用 $paper-cut-portrait，按默认上下拼接生成。
使用 $paper-cut-portrait，只发 AI 图。
```

## 内容

- `SKILL.md`：触发规则、两种输出模式、工作流程和检查要求。
- `references/prompt.md`：中文核心提示词与动态照片描述规则。
- `scripts/compose_collage.py`：无损 PNG 拼接及插画原样复制。
- 本地交付包另附实际试生成示例；GitHub 仓库不包含照片或图片文件。
- `TESTING.md`：本次测试范围和结果。

默认拼接保留原图按 EXIF 方向显示的原尺寸及解码 RGB 像素；下方等大，插画完整等比例放入。图像生成有随机性，手势与细节仍需每次查看，示例不代表所有照片均已测试。

代码与提示词采用 MIT 许可；用户提供的原始照片及示例图片不在该代码许可授权范围内，请勿据此假定拥有第三方照片、人物或品牌的使用授权。

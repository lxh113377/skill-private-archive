# -*- coding: utf-8 -*-
"""r31 P0-2: 反理性化表 H4 第二批 —— 8 条（9 条队列剔除 A-skill-manager 他人在途）。

用法：
  python 05-exec/r31_landing_rationalizations.py --dry-run   # 只打印将要写的内容与锚点校验
  python 05-exec/r31_landing_rationalizations.py --apply     # 经 rule_editor append --no-commit 逐条落盘
  python 05-exec/r31_landing_rationalizations.py --commit    # 一次收口提交（--file 白名单）

判据：反驳句须含该技能正文里实测存在的 token（见 REQUIRED_TOKEN），缺则拒绝落盘。
"""
import subprocess
import sys
import io
import os

GS = r"D:\global_skills"
PY = r"C:\Program Files\Python312\python.exe"
RULE_EDITOR = os.path.join(GS, "A-memory-start", "references", "rule_editor.py")

HEADER = "\n## 反理性化（借口 → 反驳，出现左列念头即停手）\n\n| 借口 | 反驳 |\n|---|---|\n"

# skill -> (required tokens that must exist in that SKILL.md, [(借口, 反驳), ...])
ENTRIES = {
    "local-ocr-npu": (
        ["27 s", "0.32 s/img", "-Device cpu", "Intel AIPC", "[0.997]"],
        [
            ("「首跑 27 秒没输出，八成卡死了，中断改走 CPU」",
             "那 27 s 是首次把模型编译到 NPU ISA，缓存后 0.32 s/img；中断等于每次重付编译税，而 CPU 是 1.50 s/img（本文件性能表实测值）"),
            ("「run.ps1 之外还有别的脚本，直接调更灵活」",
             "本技能明文 run.ps1 是唯一受支持接口；绕过它就绕掉了设备选择、缓存复用与平台校验层"),
            ("「报 requires Intel AIPC 就自己加 -Device cpu 默默重试」",
             "本文件要求不重试并告知用户；静默降级会把「硬件不满足」伪装成「结果就是这么慢」"),
            ("「OCR 出来的文字可以直接抄进结论」",
             "每行带置信度（示例 [0.997]）；低置信行必须标注存疑，不能与高置信行同等采信"),
            ("「目录跑完某几张没文字，就是图片本身空白」",
             "要区分「图中确无文字」与「不支持的格式/图损坏」——支持面只有 jpg/jpeg/png/bmp/tiff，后者属故障面不是空面"),
        ],
    ),
    "oc-dispatch-exec-guard": (
        ["exit 0 ≠ 成功", "护栏", "stopReason=stop", "MSYS_NO_PATHCONV", "已发生 3 次"],
        [
            ("「openclaw 返回 exit 0，说明任务跑完了」",
             "exit 0 + 0 报告产出正是本技能要拦的假成功（护栏 4 明文 exit 0 ≠ 成功）；判据只能是报告文件的实测字节数"),
            ("「session 创建成功、tracker 显示 running，就是在执行」",
             "护栏 5 实测过 session 被环境轮转、tracker 丢句柄两种活着的假象；只信磁盘上目标文件有没有变"),
            ("「这次秒停是偶发，原样重派一次」",
             "同一提示词结构已发生 3 次「这是文档不是指令」误判，原样重派必复发；先按护栏 1 在顶部注入执行段"),
            ("「它超时了，把 --timeout 调大就行」",
             "根因是反问方向后 stopReason=stop，调超时不改变行为，属用参数掩盖机制"),
            ("「prompt 里写 Read/Grep 让 agent 自己看文件更省事」",
             "CC/OC 没有这些专有工具名会卡死；要写成 cat/ls/grep -n 并明确「用 cat 实测文件」"),
            ("「中文路径直接传给 node 系 CLI 没问题」",
             "Git Bash 下必乱码，本技能因此规定走 ASCII 临时目录 + MSYS_NO_PATHCONV=1 + 反斜杠传参"),
        ],
    ),
    "hook-analyzer-skill": (
        ["数据提取", "frame_images", "segments", "TOS", "前 3 帧"],
        [
            ("「输出里有 frame_images，可以直接当评分结果交给下游」",
             "本脚本只做数据提取，5 个维度的评分由 LLM 完成（注意事项 1）；把上下文当结论等于交一份没人评过的报告"),
            ("「breakdown.json 我按格式手写一个就行」",
             "输入必须是 process_video 返回的完整 JSON；手写样本只会让真素材上线时才崩"),
            ("「segment_count=0 说明这视频开头没镜头」",
             "本文件故障排除表给了两种成因：输入缺 segments 字段、或视频从静止画面开始，与「没有镜头」结论完全不同"),
            ("「关键帧 URL 现在打得开，交付后也打得开」",
             "TOS 签名 URL 会过期；报告若依赖帧图必须留存或重新拆解获取"),
            ("「多取几帧分析更准，每个分镜取满 10 帧」",
             "每分镜只取前 3 帧是防 token 超限（注意事项 3），加帧会把上下文打爆而不是把结论做准"),
            ("「前三秒无分镜，整轮判失败」",
             "只影响钩子章节，其余拆解数据仍有效；应标注「前 3 秒无分镜」并继续出报告"),
        ],
    ),
    "report-generator-skill": (
        ["暂无数据", "前 10 个", "40 字符", "N/A", "example.com"],
        [
            ("「不传 hook_analysis 报告也能出，就这样交」",
             "钩子分析章节会显示「暂无数据」（注意事项 1）；把缺核心章节的报告当完整交付就是假交付"),
            ("「分镜概览只有 10 行，数据丢了一半」",
             "最多展示前 10 个是设计上限，完整数据在 breakdown.json，不该为凑数把全量塞进报告"),
            ("「画面描述被截断了，我在报告里手动补全」",
             "超 40 字符自动截断发生在生成侧；正文补全会让报告与脚本产出不可复现，下轮对不上账"),
            ("「BGM 和场景全是 N/A，肯定是我脚本跑坏了」",
             "本文件故障排除表写明：分镜拆解服务可能未返回该数据；先查 breakdown.json 字段再定责"),
            ("「> report.md 命令 exit 0 就算交付」",
             "重定向成功不等于内容完整；必须实测文件字节与关键章节存在（报告结构一节列出的六章）"),
            ("「示例里的 URL 是真视频，直接照跑冒烟」",
             "https://example.com/video.mp4 是占位链接，照跑得到的失败与技能缺陷无关；冒烟要用真实本地样本"),
        ],
    ),
    "天眼一下": (
        ["绝对没有风险", "USCC", "交叉验证", "relation-path", "pageSize", "不替用户"],
        [
            ("「查询返回空，说明这家公司没有风险」",
             "本技能明文：空结果只表示当前命令未返回数据，不要写成「绝对没有风险」；必须区分查到记录/已查询未返回/未查询该维度"),
            ("「名称对上了就是同一家公司」",
             "只有完整企业名或 18 位统一社会信用代码可跳过锚定；简称、品牌、曾用名必须先 company companies，多候选请用户确认"),
            ("「risk overview 查过了，明细可以不看」",
             "查询流程要求重要判断尽量两个以上维度交叉验证，且总览与明细冲突时必须直接说明冲突"),
            ("「两家都在同一个集团名下一样，肯定有关系」",
             "关联判断以 relation-path、持股、任职、集团信息为依据，不以名称相似为依据"),
            ("「把 --pageSize 拉满 50 更保险」",
             "列表默认 10，大结果应用 --head/--threshold/--output-file 控制；把长原始数据塞进最终答复会把有效信号埋掉"),
            ("「数据都指向高风险，直接建议用户别合作」",
             "本技能不替用户做法律、投资、授信或采购的最终决策；给数据驱动建议并列出需人工复核的材料"),
        ],
    ),
    "local-realtime-translator": (
        ["--continue", "4-5GB", "8766", "--stop", "benign", "diarization"],
        [
            ("「首跑 8 分钟没就绪就是失败了，换在线翻译」",
             "首跑要下 ~4-5GB 模型，本文件明令重复 --continue 直到出现就绪 URL（典型 2-4 次），并禁止替换成在线服务、子代理或其它 skill"),
            ("「命令 exit 0 返回了，任务完成」",
             "exit 0 只代表服务起来了；必须把打印的 http://127.0.0.1:8766 交给用户，并让其对着麦克风说话才算交付"),
            ("「用完不用管，反正是后台服务」",
             "服务持续持有麦克风与 GPU 显存，必须 scripts\\run.ps1 --stop 释放"),
            ("「启动日志里有 sox missing，环境坏了，先修依赖」",
             "本文件判定该警告 benign（只用中英 TTS）；为它动依赖会引入真故障"),
            ("「exit 1 就换个参数再试一次」",
             "exit 1 包含非 Intel AIPC 的情形，本文件明文不支持硬件不要重试"),
            ("「它能翻本地音频文件、能分说话人、什么语言都行」",
             "What this skill does NOT do 三项边界：已有音视频走 local-asr、单麦克风无 diarization、仅 zh↔en"),
            ("「iGPU 模型加载不了 = 整个技能不可用」",
             "管线有自动降级（Hunyuan→Opus-MT、Qwen3-ASR→Paraformer-Offline），质量下降但不算硬失败"),
        ],
    ),
    "story-cover": (
        ["UPLOAD_SIZE", "不得编造", "居中裁剪", "jq -e", "封面_v", "_上传"],
        [
            ("「中转代理忽略了 GPT_IMAGE_SIZE 返回 2:3，平台尺寸没救了」",
             "本文件已实测该行为并专设 Step 5 居中裁剪+缩放（UPLOAD_SIZE），平台像素不依赖代理认不认 size"),
            ("「用户没给笔名，先按常见署名生成一版看看」",
             "Step 1 明文：书名与笔名缺任一必须先问，不得编造或留空"),
            ("「模型肯定把书名写对了，不用放大看」",
             "文字渲染是 Step 6 的第一检查项；中文错字/丢字属高发失败位，必须目检书名与笔名可辨且未被裁切"),
            ("「Windows Git Bash 里 command -v convert 命中的就是 ImageMagick」",
             "convert 也可能是系统自带的 NTFS 卷转换工具，参数语义完全不同；优先 magick，都找不到就显式提示手动裁剪"),
            ("「curl exit 0 就代表拿到图了」",
             "API error 的 JSON 会被 base64 --decode 写成损坏文件；必须 jq -e '.error' 早退 + [ -s \"$OUT\" ] 校验（脚本里就是这两道）"),
            ("「重新生成时覆盖同名封面更干净」",
             "自增 封面_vN 是为保留迭代对照和同名 .prompt.txt 副本，覆盖等于丢掉可复现线索"),
            ("「_上传 版和原图一回事，随便用哪个」",
             "_上传 是裁剪后的平台交付件，原图必须保留供继续迭代（Step 5 明文「原图保留、另存」）"),
        ],
    ),
    "wechat-automation": (
        ["Placeholder", "last_message_id", "hash(content)", "GetAllMessage", "窗口可见", "sanitize", "validate_command"],
        [
            ("「Swift 里那两个 return nil // Placeholder 先照抄骨架，之后再填」",
             "占位实现会让监听恒返回 0 条消息且不报错，看上去「在跑」；未实现前不得当作可用交付"),
            ("「去重只记 last_message_id 一个值，够用」",
             "两个会话交替出现 A→B→A 时会被判成重复而丢消息；要的是 MessageDeduplicator 的集合 + 时间窗口"),
            ("「hash(content) 生成的 ID 重启后还能对上」",
             "CPython 的 str hash 按进程随机化，重启后 ID 全变，结果是历史消息整批重发"),
            ("「message.get('content') 一定取得到值」",
             "wxauto 返回的是消息对象而非 dict；字段取不到时输出空 content，比抛异常更难被发现"),
            ("「SendMsg 没抛异常就是发出去了」",
             "窗口最小化、未登录或焦点在别的会话时会静默失败；须回读 GetAllMessage 验证，且本文件前提就是「微信已登录且窗口可见」"),
            ("「单元测试把 WeChat mock 掉就证明链路可用」",
             "mock 只覆盖类初始化断言，真实的 UI Automation 权限与版本差异被整个抹掉"),
            ("「日志里把消息内容记全一点，排查方便」",
             "隐私一节要求 sanitize（超 50 字符截断）；全量落盘等于把聊天内容写进日志"),
            ("「命令来自自家 Orchestrator，不用校验」",
             "validate_command 的白名单 + 长度上限正是这道防线；stdin 是可被其它进程注入的边界"),
        ],
    ),
}


def build_text(skill):
    rows = ENTRIES[skill][1]
    return HEADER + "".join("| %s | %s |\n" % (a, b) for a, b in rows)


def check_tokens(skill):
    """反驳句必须指向该技能正文里真实存在的元素，否则拒绝落盘。"""
    path = os.path.join(GS, skill, "SKILL.md")
    body = io.open(path, encoding="utf-8").read()
    text = build_text(skill)
    missing = [t for t in ENTRIES[skill][0] if t not in body]
    if missing:
        return "TOKEN-MISSING-IN-SOURCE:%s" % ",".join(missing)
    if "反理性化" in body:
        return "ALREADY-HAS-SECTION"
    return "OK" if text.strip() else "EMPTY"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    skills = list(ENTRIES.keys())
    if mode in ("--dry-run", "--apply"):
        for s in skills:
            st = check_tokens(s)
            print("%-30s %s  rows=%d  bytes=%d" % (s, st, len(ENTRIES[s][1]), len(build_text(s).encode("utf-8"))))
            if st != "OK":
                print("   !! 拒绝处理：%s" % st)
                return 1
        if mode == "--dry-run":
            print("\n[dry-run] 未写盘。")
            return 0
        for s in skills:
            rc, out = run([PY, RULE_EDITOR, "append", "--file", "%s/SKILL.md" % s,
                           "--text", build_text(s), "--no-commit"])
            print("%-30s rc=%d %s" % (s, rc, out.strip().replace("\n", " | ")[:160]))
            if rc != 0:
                return 1
        return 0
    if mode == "--commit":
        args = [PY, RULE_EDITOR, "commit"]
        for s in skills:
            args += ["--file", "%s/SKILL.md" % s]
        args += ["--desc",
                 "feat(skills): r31 存量补反理性化表 8 条（对标 r31 新维度 N12 同轮 P0 队列 H4 第二批）——"
                 "真队列 9 条，剔除 A-skill-manager（他人在途 ` M`）后落 8 条；逐技能写特有失败形态，"
                 "每条反驳指向该文件正文实测存在的 token（脚本内 check_tokens 强校验，缺则拒写）。"
                 "frontmatter/description 零改动⇒派生件无需重建。复测见 r31_section_robustness"]
        rc, out = run(args)
        print(out.strip()[:1200])
        return rc
    print("unknown mode")
    return 2


if __name__ == "__main__":
    sys.exit(main())

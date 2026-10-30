"""R301C 新鲜度面判定核心。
抽成独立模块的理由：正式读数(build_r301c.py)与负控(negctl_r301c.py)必须调用同一个 classify，
否则负控测的是另一支复制品，证明不了正式判据有牙。
本模块只用一条时间轴(local_last_updated vs upstream_pushed_at)，不碰版本号 —— 两把尺不许混。
"""
import re

RE_DAY = re.compile(r"(\d{4}-\d{2}-\d{2})")


def norm_day(v):
    """任意输入 -> YYYY-MM-DD；取不到即 None。缺数据绝不猜，也不拿别的字段补。"""
    if not v:
        return None
    m = RE_DAY.search(str(v))
    return m.group(1) if m else None


def classify(local_last_updated, upstream_pushed_at):
    """唯一判据：upstream 比 local 新 => BEHIND；相同 => CURRENT；upstream 更旧 => LOCAL_AHEAD；任一侧取不到 => UNKNOWN。"""
    l = norm_day(local_last_updated)
    u = norm_day(upstream_pushed_at)
    if l is None or u is None:
        return "UNKNOWN"
    if u > l:
        return "BEHIND"
    if u == l:
        return "CURRENT"
    return "LOCAL_AHEAD"
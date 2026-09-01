#!/usr/bin/env python3
"""MiniMax 媒体生成 CLI（零依赖，仅标准库）。

封装 MiniMax 图像生成（image-01）与视频生成（MiniMax-H3）两个接口，
让 Codex / 开发者可以用一条命令按 prompt 产出素材。

常用示例：
    python scripts/minimax_gen.py image --prompt "雨后的律所窗外" --out assets/art/scene.png
    python scripts/minimax_gen.py image --prompt "同一角色不同场景" --reference-image ref.png --out assets/art/
    python scripts/minimax_gen.py video --prompt "云朵缓缓飘过 15s, 16:9" --out assets/videos/sky.mp4
    python scripts/minimax_gen.py video --prompt "让这张图动起来" --image first.png --out assets/videos/court.mp4

配置读取优先级：环境变量 > .env（默认读取项目根目录 .env，可 --env 指定）> 内置默认值。
真实 API Key 放在被 gitignore 的 .env 中，绝不提交进 git。
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "https://api.minimax.io"
DEFAULT_IMAGE_MODEL = "image-01"
DEFAULT_VIDEO_MODEL = "MiniMax-H3"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".mov"}
AUDIO_EXTENSIONS = {".mp3", ".wav"}

# 手动兜底 mimetypes（Windows 上 mimetypes 未必认识 .mp4 等）
MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
}


def default_env_path() -> Path:
    """项目根目录的 .env（脚本位于 scripts/ 下，故取上一级）。"""
    return Path(__file__).resolve().parent.parent / ".env"


def load_env(path: Path) -> dict[str, str]:
    """极简 .env 解析，支持 export 前缀、引号、注释。"""
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def cfg(env: dict[str, str], key: str, default: str | None = None) -> str | None:
    """环境变量优先，其次 .env，最后默认值。"""
    return os.environ.get(key) or env.get(key) or default


def resolve_media(value: str) -> str:
    """把引用（URL 或本地路径）转成 API 可用的 url 字符串。

    http(s) 与 data: URI 原样返回；本地文件读字节并 base64 编码为 data URI
    （MiniMax 官方推荐 URL，本地文件用 data URI 是尽力而为，若端点拒绝会给出报错）。
    """
    lowered = value.lower()
    if lowered.startswith(("http://", "https://", "data:")):
        return value
    path = Path(value)
    if not path.exists():
        raise FileNotFoundError(f"引用文件不存在: {value}")
    ext = path.suffix.lower()
    mime = MIME_MAP.get(ext) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def http_json(method: str, url: str, headers: dict[str, str],
              body: dict | None = None, timeout: int = 120) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
            msg = (
                parsed.get("base_resp", {}).get("status_msg")
                or parsed.get("message")
                or raw
            )
        except Exception:
            msg = raw
        raise RuntimeError(f"HTTP {e.code}: {msg}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}") from e


def download(url: str, out: Path, timeout: int = 300) -> Path:
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        out_path.write_bytes(resp.read())
    return out_path


def build_auth(api_key: str | None, env: dict[str, str]) -> str:
    key = api_key or cfg(env, "MINIMAX_API_KEY")
    if not key:
        raise SystemExit(
            "错误：缺少 MINIMAX_API_KEY。请在项目根目录 .env 中配置，或用 --api-key / 环境变量传入。"
        )
    return f"Bearer {key}"


def check_prompt_len(prompt: str, limit: int, kind: str) -> None:
    if len(prompt) > limit:
        print(f"警告：{kind} prompt 长度 {len(prompt)} > {limit}，可能被拒绝。", file=sys.stderr)


def now_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------------- image ----
def cmd_image(args: argparse.Namespace) -> int:
    env = load_env(args.env_path if args.env else default_env_path())
    api_key = args.api_key or cfg(env, "MINIMAX_API_KEY")
    base = (args.base_url or cfg(env, "MINIMAX_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
    model = args.model or DEFAULT_IMAGE_MODEL
    prompt = args.prompt
    check_prompt_len(prompt, 1500, "图像")

    payload: dict = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": args.aspect_ratio or "16:9",
        "response_format": args.response_format,
        "n": args.n,
    }
    if args.reference_image:
        payload["subject_reference"] = [{
            "type": args.subject_type,
            "image_file": resolve_media(args.reference_image),
        }]

    if args.dry_run:
        print(json.dumps({"url": f"{base}/v1/image_generation", "payload": payload},
                         ensure_ascii=False, indent=2))
        return 0

    resp = http_json("POST", f"{base}/v1/image_generation",
                     {"Authorization": build_auth(api_key, env),
                      "Content-Type": "application/json"}, payload)
    if "data" not in resp:
        print(f"接口返回异常: {json.dumps(resp, ensure_ascii=False)}", file=sys.stderr)
        return 1
    data = resp["data"]
    base64s = data.get("image_base64") if isinstance(data.get("image_base64"), list) else None
    urls = data.get("image_urls") if isinstance(data.get("image_urls"), list) else None
    if not base64s and not urls:
        print(f"未取到图像: {json.dumps(resp, ensure_ascii=False)}", file=sys.stderr)
        return 1

    items: list[tuple[bytes, str]] = []
    if base64s:
        items = [(base64.b64decode(s), ".png") for s in base64s]
    else:
        items = [(s, ".png") for s in urls]

    return write_media(items, args.out, "assets/art", "image", "image")


# ---------------------------------------------------------------- video ----
def build_video_payload(args: argparse.Namespace) -> dict:
    content: list[dict] = [{"type": "text", "text": args.prompt}]
    if args.first_frame:
        content.append({"type": "image_url", "image_url": {"url": resolve_media(args.first_frame)},
                        "role": "first_frame"})
    if args.last_frame:
        content.append({"type": "image_url", "image_url": {"url": resolve_media(args.last_frame)},
                        "role": "last_frame"})
    for v in args.reference_image or []:
        content.append({"type": "image_url", "image_url": {"url": resolve_media(v)},
                        "role": "reference_image"})
    for v in args.reference_video or []:
        content.append({"type": "video_url", "video_url": {"url": resolve_media(v)},
                        "role": "reference_video"})
    for v in args.reference_audio or []:
        content.append({"type": "audio_url", "audio_url": {"url": resolve_media(v)},
                        "role": "reference_audio"})

    has_frame = bool(args.first_frame or args.last_frame)
    has_ref = bool(args.reference_image or args.reference_video or args.reference_audio)
    mode = "reference" if has_ref else ("image" if has_frame else "text")
    ratio = args.ratio or ("16:9" if mode == "text" else "adaptive")

    return {
        "model": args.model or DEFAULT_VIDEO_MODEL,
        "content": content,
        "duration": args.duration,
        "resolution": args.resolution or "2K",
        "ratio": ratio,
    }


def extract_task_id(resp: dict) -> str:
    if isinstance(resp.get("task_id"), str):
        return resp["task_id"]
    data = resp.get("data")
    if isinstance(data, dict):
        if isinstance(data.get("task_id"), str):
            return data["task_id"]
        task = data.get("task")
        if isinstance(task, dict) and isinstance(task.get("task_id"), str):
            return task["task_id"]
    task = resp.get("task")
    if isinstance(task, dict) and isinstance(task.get("task_id"), str):
        return task["task_id"]
    raise RuntimeError(f"未取到 task_id: {json.dumps(resp, ensure_ascii=False)}")


def cmd_video(args: argparse.Namespace) -> int:
    env = load_env(args.env_path if args.env else default_env_path())
    api_key = args.api_key or cfg(env, "MINIMAX_API_KEY")
    base = (args.base_url or cfg(env, "MINIMAX_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
    check_prompt_len(args.prompt, 7000, "视频")
    payload = build_video_payload(args)

    if args.dry_run:
        staged = json.loads(json.dumps(payload))
        # data URI 过长时在 dry-run 中省略正文，避免刷屏
        for item in staged.get("content", []):
            for key in ("image_url", "video_url", "audio_url"):
                url = item.get(key, {}).get("url", "")
                if url.startswith("data:"):
                    item[key]["url"] = f"<data-uri {len(url)} chars>"
        print(json.dumps({"url": f"{base}/v2/video_generation", "payload": staged},
                         ensure_ascii=False, indent=2))
        return 0

    resp = http_json("POST", f"{base}/v2/video_generation",
                     {"Authorization": build_auth(api_key, env),
                      "Content-Type": "application/json"}, payload)
    task_id = extract_task_id(resp)
    print(f"视频生成任务已提交，task_id={task_id}")

    query_url = f"{base}/v2/query/video_generation/{task_id}"
    interval = args.poll_interval
    deadline = time.time() + args.max_time
    while time.time() < deadline:
        time.sleep(interval)
        q = http_json("GET", query_url, {"Authorization": build_auth(api_key, env)})
        task = q.get("task", q)
        status = task.get("status", "unknown")
        print(f"当前任务状态: {status}")
        if status == "succeeded":
            url = (task.get("content") or {}).get("url")
            if not url:
                print(f"任务成功但无视频 URL: {json.dumps(q, ensure_ascii=False)}", file=sys.stderr)
                return 1
            out_path = Path(args.out) if args.out else Path(f"assets/videos/{now_stamp()}_video.mp4")
            saved = download(url, out_path)
            print(f"视频已保存: {saved}")
            print(f"下载 URL（若需要重新获取）: {url}")
            return 0
        if status in ("failed", "cancelled"):
            print(f"生成失败: status={status}, error={task.get('error')}", file=sys.stderr)
            return 1
    print(f"超过 {args.max_time}s 仍未完成，请稍后用 task_id={task_id} 查询。", file=sys.stderr)
    return 1


# ------------------------------------------------------------- helpers ----
def write_media(items: list[tuple[bytes, str]], out: str | None,
                default_dir: str, prefix: str, kind: str) -> int:
    """按输出目标写文件。out 若是带扩展名的单文件路径则覆盖；否则当作目录写多份。"""
    if out:
        out_path = Path(out)
    else:
        out_path = Path(default_dir)

    is_single_file = out and out_path.suffix.lower() in (IMAGE_EXTENSIONS | VIDEO_EXTENSIONS)
    if is_single_file and len(items) > 1:
        print("提示：--out 是单文件路径但生成了多份，已按目录处理。", file=sys.stderr)
        is_single_file = False

    saved: list[Path] = []
    for i, (blob, ext) in enumerate(items):
        if is_single_file:
            target = out_path
        else:
            target = out_path / f"{prefix}_{now_stamp()}_{i + 1}{ext or '.png'}"
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(blob)
        saved.append(target)

    for p in saved:
        print(f"{kind} 已保存: {p}")
    return 0


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--env", dest="env", default=None, help="指定 .env 文件路径（默认项目根目录 .env）")
    parser.add_argument("--api-key", dest="api_key", default=None, help="直接传 API Key（优先于 .env / 环境变量）")
    parser.add_argument("--base-url", dest="base_url", default=None, help=f"API 基址（默认 {DEFAULT_BASE_URL}）")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要发送的请求体，不真正调用")


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    add_common_args(common)

    parser = argparse.ArgumentParser(description="MiniMax 图像/视频生成 CLI（零依赖）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_img = sub.add_parser("image", parents=[common], help="image-01 文生图 / 参考图生图")
    p_img.add_argument("--prompt", required=True, help="图像 prompt")
    p_img.add_argument("--model", default=None, help=f"图像模型（默认 {DEFAULT_IMAGE_MODEL}）")
    p_img.add_argument("--out", default=None, help="输出文件或目录（默认 assets/art/image_<ts>_N.png）")
    p_img.add_argument("--aspect-ratio", default=None, help="宽高比，如 16:9 / 1:1（默认 16:9）")
    p_img.add_argument("--n", type=int, default=1, help="生成张数（1-9）")
    p_img.add_argument("--response-format", dest="response_format", choices=("base64", "url"), default="base64")
    p_img.add_argument("--reference-image", dest="reference_image", default=None, help="参考图 URL/本地路径（subject_reference）")
    p_img.add_argument("--subject-type", dest="subject_type", default="character", help="subject_reference 类型（默认 character）")
    p_img.set_defaults(func=cmd_image)

    p_vid = sub.add_parser("video", parents=[common], help="MiniMax-H3 文生视频 / 图生视频 / 参考生成")
    p_vid.add_argument("--prompt", required=True, help="视频描述")
    p_vid.add_argument("--model", default=None, help=f"视频模型（默认 {DEFAULT_VIDEO_MODEL}）")
    p_vid.add_argument("--out", default=None, help="输出文件（默认 assets/videos/<ts>_video.mp4）")
    p_vid.add_argument("--resolution", default=None, help="2K / 768P（默认 2K）")
    p_vid.add_argument("--duration", type=int, default=5, help="时长（4-15 的整数，默认 5）")
    p_vid.add_argument("--ratio", default=None, help="宽高比，t2v 必填且非 adaptive；i2v 默认 adaptive")
    p_vid.add_argument("--image", dest="first_frame", default=None, help="首帧图 URL/本地路径")
    p_vid.add_argument("--last-frame", dest="last_frame", default=None, help="尾帧图 URL/本地路径")
    p_vid.add_argument("--reference-image", dest="reference_image", action="append", default=None, help="参考图（可多次）")
    p_vid.add_argument("--reference-video", dest="reference_video", action="append", default=None, help="参考视频（可多次）")
    p_vid.add_argument("--reference-audio", dest="reference_audio", action="append", default=None, help="参考音频（可多次）")
    p_vid.add_argument("--poll-interval", dest="poll_interval", type=int, default=10, help="轮询间隔秒数（默认 10）")
    p_vid.add_argument("--max-time", dest="max_time", type=int, default=600, help="最长等待秒数（默认 600）")
    p_vid.set_defaults(func=cmd_video)

    return parser


def main() -> int:
    # 固定 UTF-8 输出，避免中文在 Windows 控制台/管道里乱码
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (SystemExit, KeyboardInterrupt):
        raise
    except (FileNotFoundError, RuntimeError) as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
exp_monitor_debug.py -- OCR 診斷錄影機（新版：使用 template OCR）
================================================================
用「新的模板辨識器 + ExpTracker」逐幀錄影並記錄失敗原因，
方便在真實遊戲上確認辨識器準不準、或找出線上失敗的原因。

用法：
    python exp_monitor_debug.py            # 連續錄到 Ctrl+C
    python exp_monitor_debug.py -n 8       # 錄 8 幀就停
    python exp_monitor_debug.py -i 0.5     # 每 0.5 秒一幀

輸出：debug_YYYYMMDD_HHMMSS/
    NNNNN_raw.png        原始底部條
    NNNNN_mask.png       新辨識器實際看到的遮罩（白字黑底）
    session.csv          每幀：raw_exp / pct / conf / reason / n_runs / widths / 追蹤輸出
"""
import os, sys, csv, time, json, argparse, importlib.util
from datetime import datetime
from pathlib import Path
import cv2, numpy as np

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("expmon", HERE / "exp_monitor.py")
M = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(M)
from exp_template_ocr import TemplateOCR, ExpTracker, build_mask

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--interval", type=float, default=1.0)
ap.add_argument("-n", "--frames",   type=int,   default=0, help="0=無限，直到 Ctrl+C")
args = ap.parse_args()

session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = HERE / f"debug_{session_id}"
out_dir.mkdir(parents=True, exist_ok=True)

CSV_FIELDS = ["frame","timestamp","status","cap_method","win_w","win_h",
              "raw_exp","pct","conf","reason","n_runs","widths",
              "track_exp","track_pct","track_reason"]

M.set_dpi_awareness()
ocr = TemplateOCR()
if not ocr.is_ready():
    print("[ERROR] 模板未就緒（templates/ 不完整）"); sys.exit(1)
tracker = ExpTracker()

print("="*70)
print(f"  EXP Debug (template OCR)  --  {session_id}")
print(f"  templates ready: {ocr.is_ready()}   interval={args.interval}s")
print(f"  output: {out_dir}")
print("="*70)
print(f"  {'#':>4} {'time':12} {'raw_exp':16} {'pct':8} {'conf':5} {'reason':14} {'tracked'}")
print("-"*70)

frame = 0
with open(out_dir / "session.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=CSV_FIELDS); w.writeheader()
    try:
        while True:
            frame += 1
            now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            rec = {k: "" for k in CSV_FIELDS}; rec["frame"]=frame; rec["timestamp"]=now

            hwnd, reg = M.find_window()
            if hwnd is None:
                rec["status"]="no_window"; w.writerow(rec); f.flush()
                print(f"  {frame:>4} {now}  NO WINDOW")
                if args.frames and frame>=args.frames: break
                time.sleep(args.interval); continue

            rec["win_w"]=reg["width"]; rec["win_h"]=reg["height"]
            img, cap = M.capture_strip(hwnd, reg)
            rec["cap_method"]=cap or ""
            if img is None:
                rec["status"]="cap_fail"; w.writerow(rec); f.flush()
                print(f"  {frame:>4} {now}  CAP FAIL ({cap})")
                if args.frames and frame>=args.frames: break
                time.sleep(args.interval); continue

            cv2.imwrite(str(out_dir/f"{frame:05d}_raw.png"), img)
            y0,y1 = M.find_exp_bar_rows(img); band = img[y0:y1,:]
            x0,x1 = M.find_exp_text_cols(band, img.shape[1]); row = band[:,x0:x1]
            mask = build_mask(band)   # 用整條 band，由 recognize 內部切文字區塊（抗金色UI雜訊）
            cv2.imwrite(str(out_dir/f"{frame:05d}_mask.png"), mask)
            try:
                cv2.imwrite(str(out_dir/f"{frame:05d}_block.png"), ocr._isolate_text(mask))
            except Exception:
                pass

            r = ocr.recognize(mask, debug=True)
            t = tracker.update(r["exp"], r["pct"])

            rec["status"]   = "ok" if r["ok"] else "fail"
            rec["raw_exp"]  = r["exp"] or ""
            rec["pct"]      = r["pct"] or ""
            rec["conf"]     = f"{r['conf']:.3f}"
            rec["reason"]   = r["reason"]
            rec["n_runs"]   = r["n_runs"]
            rec["widths"]   = json.dumps(r["widths"])
            rec["track_exp"]= t["exp"] if t["exp"] is not None else ""
            rec["track_pct"]= f"{t['pct']:.3f}" if t["pct"] is not None else ""
            rec["track_reason"]= t["reason"]
            w.writerow(rec); f.flush()

            tracked = f"{t['exp']:,}" if t["exp"] is not None else "-"
            ndig = len(r['exp']) if r['exp'] else 0
            print(f"  {frame:>4} {now} {str(r['exp'] or '-'):16} ({ndig}d) {str(r['pct'] or '-'):8} "
                  f"{r['conf']:.2f}  {r['reason']:14} {tracked}")

            if args.frames and frame>=args.frames: break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n停止。")

print(f"\n完成。請把整個資料夾 {out_dir.name} 給我看（特別是 *_raw.png 與 *_mask.png）。")

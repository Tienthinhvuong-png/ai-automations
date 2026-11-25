"""Chạy từ dòng lệnh:  python -m app.cli data/products.csv"""

import argparse
import logging
from pathlib import Path

from app.pipeline import run_batch


def main() -> None:
    parser = argparse.ArgumentParser(description="Tạo nội dung marketing hàng loạt từ file CSV sản phẩm")
    parser.add_argument("csv", type=Path, help="File CSV có cột name, description, price, promotion, target_customer, link")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    results = run_batch(args.csv)

    ok = [r for r in results if r.ok]
    print(f"\nXong {len(ok)}/{len(results)} sản phẩm.")
    for r in results:
        print(f"  {'OK ' if r.ok else 'LỖI'} {r.product}: {r.file or r.error}")


if __name__ == "__main__":
    main()

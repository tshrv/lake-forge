import argparse

from loguru import logger

from db import load_into_db
from generator import generate_parquet_data


def main():
    logger.info("Data generation started")
    args = parse_arguments()
    data_dir_path = generate_parquet_data(scale_factor=args.scale_factor)
    table_map = load_into_db(data_dir_path=data_dir_path)
    logger.info("Data generation completed")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate TPCH data in Parquet format."
    )
    parser.add_argument(
        "--scale-factor",
        type=int,
        default=1,
        help="Scale factor for data generation (e.g., 1, 10, 100). Default is 1.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()

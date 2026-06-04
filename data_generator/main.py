import argparse

from loguru import logger

from db import load_into_db, profile_data, validate_data
from generator import generate_parquet_data


def main():
    logger.info("Data generation started")
    args = parse_arguments()
    data_dir_path = generate_parquet_data(scale_factor=args.scale_factor)
    logger.info("Data generation completed")

    if args.create_db:
        logger.info("Database creation started")
        db_name = f"lake_forge_db_sf{args.scale_factor}.duckdb"
        table_map = load_into_db(data_dir_path=data_dir_path, db_name=db_name)
        logger.info("Database creation completed")

        logger.info("Data validation started")
        validate_data(table_map=table_map, db_name=db_name)
        # Run profiling
        profile_data(table_map=table_map, db_name=db_name)
        logger.info("Data validation completed")


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
    parser.add_argument(
        "--create-db",
        type=bool,
        default=False,
        help="Whether to create the database or not. Default is False.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()

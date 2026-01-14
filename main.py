from src.crawler.pipeline import Pipeline

def main():
    pipeline = Pipeline("https://www.lasmarias.com.ar")
    pipeline.run()


if __name__ == "__main__":
    main()

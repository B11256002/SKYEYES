def main():
    try:
        import torch
    except ImportError:
        print("PyTorch is not installed in this Python environment.")
        return

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")

    if torch.cuda.is_available():
        print(f"GPU name: {torch.cuda.get_device_name(0)}")


if __name__ == "__main__":
    main()

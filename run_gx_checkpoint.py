import great_expectations as gx
import sys
import os

def main():
    print("Loading Great Expectations Context...")
    try:
        context = gx.get_context(mode="file")
    except Exception as e:
        print(f"Error loading context: {e}")
        sys.exit(1)

    print("Fetching checkpoint...")
    checkpoint = context.checkpoints.get("ecommerce_daily_checkpoint")
    
    print("Running checkpoint...")
    result = checkpoint.run()
    
    if not result.success:
        print("Data quality validation failed!")
        sys.exit(1)
        
    print("Data quality validation passed!")

if __name__ == "__main__":
    main()

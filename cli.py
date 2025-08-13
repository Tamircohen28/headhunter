"""
Command Line Interface for the job4u application.
Provides a simple interface to run the interview preparation pipeline.
"""

import sys
from main import InterviewPreparationPipeline


def main():
    """Main CLI entry point."""
    try:
        # Create and run pipeline
        pipeline = InterviewPreparationPipeline()
        result = pipeline.run()
        
        if result['success']:
            print("✅ Pipeline completed successfully!")
            print(f"📁 Results saved to: {pipeline.config.output_dir}")
            print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
            print(f"📊 Files generated: {len(result['results'].get('files_generated', []))}")
        else:
            print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
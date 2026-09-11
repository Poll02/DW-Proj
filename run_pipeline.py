import subprocess
import sys
import time

def run_step(step_name, command):
    print(f"\n{'='*60}")
    print(f"STARTING STEP: {step_name}")
    print(f"{'='*60}")
    start_time = time.time()
    
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\nERROR: Step '{step_name}' failed. Pipeline aborted.")
        sys.exit(1)
        
    elapsed = time.time() - start_time
    print(f"COMPLETED: {step_name} in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    print("Starting Movie Analytics Data Warehouse Pipeline...")
    
    # 1. Reconciled Layer
    run_step("Build Reconciled Layer", f'"{sys.executable}" etl_pipeline/02_reconcile.py')
    
    # 2. Data Warehouse Build
    run_step("Build Data Warehouse Schema and Populate", f'"{sys.executable}" etl_pipeline/03_build_dw.py')
    
    # 3. Export Charts
    run_step("Export Analytics Charts", f'"{sys.executable}" etl_pipeline/04_export_charts.py')
    
    # 4. Quality Checks
    run_step("Run Quality Checks", f'"{sys.executable}" etl_pipeline/05_run_quality_checks.py')
    
    print("\n" + "="*60)
    print("END-TO-END PIPELINE EXECUTED SUCCESSFULLY")
    print("="*60)
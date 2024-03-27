# Step 1: Create a new Conda environment
conda create --name mamonandia_env python=3.11

# Step 2: Activate the Conda environment
conda activate mamonandia_env

# Step 3: Install required packages from requirements.txt
pip install -r requirements.txt

# Step 4: Deactivate the Conda environment (optional)
conda deactivate
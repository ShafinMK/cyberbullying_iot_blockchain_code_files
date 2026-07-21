# 1. Clone or create the project structure
mkdir cyberbullying-forensic-framework
cd cyberbullying-forensic-framework

# 2. Create all directories
mkdir -p chaincode iot-simulator caliper-benchmarks deployment analysis figures

# 3. Copy all files to their respective directories

# 4. Install dependencies
# For chaincode
cd chaincode
go mod tidy

# For IoT simulator
cd ../iot-simulator
pip install -r requirements.txt

# For Caliper benchmarks
cd ../caliper-benchmarks
npm install

# 5. Deploy the blockchain network
cd ../deployment
chmod +x network.sh
./network.sh up

# 6. Run IoT device simulation
cd ../iot-simulator
python device_simulator.py --config config.yaml

# 7. Run performance benchmarks
cd ../caliper-benchmarks
npm run benchmark

# 8. Analyze results
cd ../analysis
python performance_analysis.py --results-dir ../caliper-benchmarks/results --visualize
python visualize_results.py
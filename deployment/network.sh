#!/bin/bash
#
# Network Deployment Script for Hyperledger Fabric
# Deploys the forensic evidence blockchain network
#
# Based on Section 3.6 of the paper

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FABRIC_VERSION="2.5.0"
CHANNEL_NAME="evidencechannel"
CHAINCODE_NAME="evidencechaincode"
CHAINCODE_VERSION="1.0"
CHAINCODE_PATH="../chaincode"
ORDERER_ORG="example.com"
ORG1_NAME="org1"
ORG2_NAME="org2"
ORG3_NAME="org3"

# Print with color
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Go
    if ! command -v go &> /dev/null; then
        print_error "Go is not installed"
        exit 1
    fi
    
    print_info "All prerequisites satisfied"
}

# Generate crypto materials
generate_crypto() {
    print_info "Generating crypto materials..."
    
    # Use cryptogen to generate certificates
    if [ -f "crypto-config.yaml" ]; then
        cryptogen generate --config=crypto-config.yaml --output=crypto-config
        print_info "Crypto materials generated"
    else
        print_warning "crypto-config.yaml not found, skipping"
    fi
}

# Generate channel artifacts
generate_channel_artifacts() {
    print_info "Generating channel artifacts..."
    
    if [ -f "configtx.yaml" ]; then
        configtxgen -profile TwoOrgsChannel -outputCreateChannelTx ${CHANNEL_NAME}.tx -channelID ${CHANNEL_NAME}
        configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ${ORG1_NAME}MSPanchors.tx -channelID ${CHANNEL_NAME} -asOrg ${ORG1_NAME}MSP
        configtxgen -profile TwoOrgsChannel -outputAnchorPeersUpdate ${ORG2_NAME}MSPanchors.tx -channelID ${CHANNEL_NAME} -asOrg ${ORG2_NAME}MSP
        print_info "Channel artifacts generated"
    else
        print_warning "configtx.yaml not found, skipping"
    fi
}

# Start the network
start_network() {
    print_info "Starting blockchain network..."
    
    # Start Docker containers
    docker-compose -f docker-compose.yaml up -d
    
    # Wait for containers to be ready
    print_info "Waiting for containers to initialize..."
    sleep 10
    
    print_info "Network started successfully"
}

# Create channel
create_channel() {
    print_info "Creating channel ${CHANNEL_NAME}..."
    
    # Use peer CLI to create channel
    docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" \
               -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org1.example.com/msp" \
               peer0.org1.example.com \
               peer channel create -o orderer.example.com:7050 -c ${CHANNEL_NAME} -f /etc/hyperledger/configtx/${CHANNEL_NAME}.tx
    
    print_info "Channel created"
}

# Join peers to channel
join_channel() {
    print_info "Joining peers to channel..."
    
    for org in ${ORG1_NAME} ${ORG2_NAME} ${ORG3_NAME}; do
        docker exec -e "CORE_PEER_LOCALMSPID=${org}MSP" \
                   -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@${org}.example.com/msp" \
                   peer0.${org}.example.com \
                   peer channel join -b ${CHANNEL_NAME}.block
    done
    
    print_info "Peers joined channel"
}

# Deploy chaincode
deploy_chaincode() {
    print_info "Deploying chaincode ${CHAINCODE_NAME}..."
    
    # Package chaincode
    docker exec peer0.org1.example.com \
               peer chaincode package -n ${CHAINCODE_NAME} -v ${CHAINCODE_VERSION} -p /opt/gopath/src/github.com/chaincode ${CHAINCODE_NAME}.tar.gz
    
    # Install chaincode on all peers
    for org in ${ORG1_NAME} ${ORG2_NAME} ${ORG3_NAME}; do
        docker exec -e "CORE_PEER_LOCALMSPID=${org}MSP" \
                   -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@${org}.example.com/msp" \
                   peer0.${org}.example.com \
                   peer chaincode install ${CHAINCODE_NAME}.tar.gz
    done
    
    # Approve chaincode for each organization
    for org in ${ORG1_NAME} ${ORG2_NAME} ${ORG3_NAME}; do
        docker exec -e "CORE_PEER_LOCALMSPID=${org}MSP" \
                   -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@${org}.example.com/msp" \
                   peer0.${org}.example.com \
                   peer chaincode approveformyorg -C ${CHANNEL_NAME} -n ${CHAINCODE_NAME} -v ${CHAINCODE_VERSION}
    done
    
    # Commit chaincode
    docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" \
               -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org1.example.com/msp" \
               peer0.org1.example.com \
               peer chaincode commit -C ${CHANNEL_NAME} -n ${CHAINCODE_NAME} -v ${CHAINCODE_VERSION}
    
    print_info "Chaincode deployed"
}

# Initialize ledger (optional)
init_ledger() {
    print_info "Initializing ledger..."
    
    docker exec -e "CORE_PEER_LOCALMSPID=Org1MSP" \
               -e "CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/msp/users/Admin@org1.example.com/msp" \
               peer0.org1.example.com \
               peer chaincode invoke -C ${CHANNEL_NAME} -n ${CHAINCODE_NAME} -c '{"function":"InitLedger","Args":[]}'
    
    print_info "Ledger initialized"
}

# Stop the network
stop_network() {
    print_info "Stopping blockchain network..."
    
    docker-compose -f docker-compose.yaml down
    
    print_info "Network stopped"
}

# Clean the network
clean_network() {
    print_info "Cleaning network..."
    
    docker-compose -f docker-compose.yaml down -v
    rm -rf crypto-config
    rm -rf ${CHANNEL_NAME}.block
    rm -rf ${CHANNEL_NAME}.tx
    
    print_info "Network cleaned"
}

# Main script
main() {
    case "$1" in
        up)
            check_prerequisites
            generate_crypto
            generate_channel_artifacts
            start_network
            create_channel
            join_channel
            deploy_chaincode
            ;;
        start)
            start_network
            create_channel
            join_channel
            deploy_chaincode
            ;;
        down)
            stop_network
            ;;
        clean)
            stop_network
            clean_network
            ;;
        restart)
            stop_network
            clean_network
            start_network
            create_channel
            join_channel
            deploy_chaincode
            ;;
        createChannel)
            create_channel
            join_channel
            ;;
        deployChaincode)
            deploy_chaincode
            ;;
        *)
            echo "Usage: $0 {up|start|down|clean|restart|createChannel|deployChaincode}"
            echo "  up              - Full deployment (crypto, channel, chaincode)"
            echo "  start           - Start network and deploy (assumes crypto exists)"
            echo "  down            - Stop network"
            echo "  clean           - Stop and remove all artifacts"
            echo "  restart         - Restart network from scratch"
            echo "  createChannel   - Create and join channel only"
            echo "  deployChaincode - Deploy chaincode only"
            exit 1
            ;;
    esac
}

main "$@"
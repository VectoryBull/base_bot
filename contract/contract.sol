// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CompanyShipmentTracker {

    struct Shipment {
        uint256 deliveryTime; // in seconds
        bool success;
        uint256 feedbackScore; // 0 - 10000 (i.e., 9855 = 98.55%)
        uint256 timestamp;
    }

    struct Company {
        string name;
        address addr;
        Shipment[] shipments;
        bool exists;
    }

    mapping(address => Company) public companies;
    address[] public companyAddresses;

    modifier onlyRegistered() {
        require(companies[msg.sender].exists, "Company not registered");
        _;
    }

    event CompanyRegistered(address indexed company, string name);
    event ShipmentAdded(address indexed company, Shipment shipment);

    function registerCompany(string memory name) external {
        require(!companies[msg.sender].exists, "Already registered");

        Company storage company = companies[msg.sender];
        company.name = name;
        company.addr = msg.sender;
        company.exists = true;

        companyAddresses.push(msg.sender);
        emit CompanyRegistered(msg.sender, name);
    }

    function addShipment(uint256 deliveryTime, bool success, uint256 feedbackScore) external onlyRegistered {
        require(feedbackScore <= 10000, "Invalid feedback score");

        Shipment memory newShipment = Shipment({
            deliveryTime: deliveryTime,
            success: success,
            feedbackScore: feedbackScore,
            timestamp: block.timestamp
        });

        companies[msg.sender].shipments.push(newShipment);
        emit ShipmentAdded(msg.sender, newShipment);
    }

    function getShipments(address companyAddr) external view returns (Shipment[] memory) {
        return companies[companyAddr].shipments;
    }

    function getAllCompanies() external view returns (Company[] memory) {
        Company[] memory allCompanies = new Company[](companyAddresses.length);
        for (uint256 i = 0; i < companyAddresses.length; i++) {
            allCompanies[i] = companies[companyAddresses[i]];
        }
        return allCompanies;
    }

    function getShipmentStats(address companyAddr) external view returns (
        uint256 total,
        uint256 successes,
        uint256 failures,
        uint256 avgFeedback,
        uint256 avgDeliveryTime
    ) {
        Shipment[] storage list = companies[companyAddr].shipments;
        uint256 feedbackSum = 0;
        uint256 deliverySum = 0;

        for (uint256 i = 0; i < list.length; i++) {
            if (list[i].success) successes++;
            else failures++;
            feedbackSum += list[i].feedbackScore;
            deliverySum += list[i].deliveryTime;
        }

        total = list.length;
        avgFeedback = total > 0 ? feedbackSum / total : 0;
        avgDeliveryTime = total > 0 ? deliverySum / total : 0;
    }
}

// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

/**
 * @title Storage
 * @dev Store & retrieve value in a variable
 * Any address can deposit eth into this contract, any number of times.
 * The amount of eth deposited per address is stored.
 * An address can withdraw all of their eth if they want.
 */
contract Storage {
    // Mapping from address to uint
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        // There's still a reentrancy attack here?
        uint256 balance = balances[msg.sender];
        balances[msg.sender] = 0;
        (bool sent, ) = msg.sender.call{value: balance}("");
        if (!sent) {
            balances[msg.sender] = balance;
        }
    }
}
